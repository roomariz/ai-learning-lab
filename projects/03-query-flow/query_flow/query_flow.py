"""
QueryFlow - Hybrid Retrieval Framework

A lightweight retrieval framework combining dense (semantic), sparse (BM25),
and query-aware selection for improved search relevance.
"""

from __future__ import annotations

import re
import logging
import hashlib

from .deps import require

try:
    import numpy as np
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    np = None

try:
    import faiss
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    faiss = None

try:
    from rank_bm25 import BM25Okapi
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    BM25Okapi = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _require_numpy(purpose: str):
    if np is None:
        require("NumPy", purpose)


def _require_faiss(purpose: str):
    if faiss is None:
        require("FAISS", purpose, "retrieval")


def _require_bm25(purpose: str):
    if BM25Okapi is None:
        require("BM25", purpose, "retrieval")


SAMPLE_DOCUMENTS = [
    {"id": "doc_001", "text": "Albert Einstein was a theoretical physicist who developed the theory of relativity."},
    {"id": "doc_002", "text": "Marie Curie was a Polish-born physicist and chemist who discovered radium and polonium."},
    {"id": "doc_003", "text": "Isaac Newton was an English mathematician and physicist who formulated the laws of motion."},
    {"id": "doc_004", "text": "Ada Lovelace was an English mathematician who is considered the first computer programmer."},
    {"id": "doc_005", "text": "Charles Darwin was an English naturalist who formulated the theory of evolution."},
    {"id": "doc_006", "text": "Nikola Tesla was an inventor and electrical engineer who developed alternating current systems."},
    {"id": "doc_007", "text": "Galileo Galilei was an Italian astronomer who made observational discoveries about the solar system."},
    {"id": "doc_008", "text": "Leonardo da Vinci was an Italian polymath of the Renaissance period."},
    {"id": "doc_009", "text": "Johannes Kepler was a German astronomer who formulated laws of planetary motion."},
    {"id": "doc_010", "text": "Rosalind Franklin was an English chemist who contributed to understanding DNA structure."},
    {"id": "doc_011", "text": "Alan Turing was a British mathematician and computer scientist, father of theoretical computer science."},
    {"id": "doc_012", "text": "Stephen Hawking was a British theoretical physicist who studied cosmology and black holes."},
    {"id": "doc_013", "text": "Niels Bohr was a Danish physicist who made foundational contributions to atomic structure."},
    {"id": "doc_014", "text": "Richard Feynman was an American physicist who developed quantum electrodynamics."},
    {"id": "doc_015", "text": "Max Planck was a German physicist who originated quantum theory."},
    {"id": "doc_016", "text": "Louis Pasteur was a French chemist who developed pasteurization and vaccines."},
    {"id": "doc_017", "text": "Alexander Graham Bell was a Scottish inventor who invented the telephone."},
    {"id": "doc_018", "text": "Thomas Edison was an American inventor who developed the phonograph and light bulb."},
    {"id": "doc_019", "text": "James Watt was a Scottish inventor who improved the steam engine."},
    {"id": "doc_020", "text": "Benjamin Franklin was an American polymath and statesman who invented the lightning rod."},
    {"id": "doc_021", "text": "Michael Faraday was an English scientist who discovered electromagnetic induction."},
    {"id": "doc_022", "text": "Gregor Mendel was an Austrian monk who founded the science of genetics."},
    {"id": "doc_023", "text": "Dmitri Mendeleev was a Russian chemist who created the periodic table."},
    {"id": "doc_024", "text": "Antoine Lavoisier was a French chemist who formulated the law of conservation of mass."},
    {"id": "doc_025", "text": "Carl Linnaeus was a Swedish botanist who created the classification system for living organisms."},
    {"id": "doc_026", "text": "Ernest Rutherford was a New Zealand physicist who discovered the atomic nucleus."},
    {"id": "doc_027", "text": "James Clerk Maxwell was a Scottish physicist who formulated electromagnetic theory."},
    {"id": "doc_028", "text": "Werner Heisenberg was a German physicist who developed quantum mechanics."},
    {"id": "doc_029", "text": "Erwin Schrodinger was an Austrian physicist who developed wave mechanics."},
    {"id": "doc_030", "text": "Paul Dirac was an English physicist who developed quantum mechanics and anti-matter theory."},
    {"id": "doc_031", "text": "Enrico Fermi was an Italian physicist who built the first nuclear reactor."},
    {"id": "doc_032", "text": "Lise Meitner was an Austrian-Swedish physicist who contributed to nuclear fission discovery."},
    {"id": "doc_033", "text": "Katherine Johnson was an American mathematician who worked on NASA missions."},
    {"id": "doc_034", "text": "Dorothy Vaughan was an American mathematician and aerospace engineer."},
    {"id": "doc_035", "text": "Mary Jackson was an American aerospace engineer and the first female African-American engineer at NASA."},
    {"id": "doc_036", "text": "Grace Hopper was an American computer scientist who developed the first compiler."},
    {"id": "doc_037", "text": "John von Neumann was a Hungarian-American mathematician who contributed to computer architecture."},
    {"id": "doc_038", "text": "Claude Shannon was an American mathematician who founded information theory."},
    {"id": "doc_039", "text": "Ada Lovelace started with the letter A and is considered the first programmer."},
    {"id": "doc_040", "text": "Grace Hopper started with the letter G and pioneered computer programming."},
    {"id": "doc_041", "text": "Blaise Pascal was a French mathematician who invented the mechanical calculator."},
    {"id": "doc_042", "text": "Gottfried Leibniz was a German mathematician who developed calculus alongside Newton."},
    {"id": "doc_043", "text": "Euclid was an ancient Greek mathematician known as the father of geometry."},
    {"id": "doc_044", "text": "Archimedes was an ancient Greek mathematician who discovered principles of physics."},
    {"id": "doc_045", "text": "Pythagoras was an ancient Greek mathematician known for the Pythagorean theorem."},
    {"id": "doc_046", "text": "Hypatia was an ancient Greek mathematician and philosopher."},
    {"id": "doc_047", "text": "Florence Nightingale was a British nurse and statistician who pioneered modern nursing."},
    {"id": "doc_048", "text": "Clara Barton was an American nurse who founded the American Red Cross."},
    {"id": "doc_049", "text": "Joseph Lister was a British surgeon who pioneered antiseptic surgery."},
    {"id": "doc_050", "text": "Ignaz Semmelweis was a Hungarian physician who discovered handwashing importance."},
]

documents = SAMPLE_DOCUMENTS
doc_ids = [d["id"] for d in documents]
doc_texts = [d["text"] for d in documents]
doc_id_to_index = {doc_id: i for i, doc_id in enumerate(doc_ids)}


DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_EMBEDDING_URL = "http://localhost:11434/v1"

_client = None
_embedding_model = None
_embedding_cache = {}


def _cache_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def set_embedding_model(model_name: str, base_url: str = DEFAULT_EMBEDDING_URL):
    """Set the embedding model to use for dense retrieval."""
    if np is None:
        require("NumPy", "embedding initialization")
    global _client, _embedding_model, _embedding_cache
    try:
        from openai import OpenAI
    except ModuleNotFoundError:
        require("OpenAI", "embedding initialization", "retrieval")
    _client = OpenAI(base_url=base_url, api_key="ollama")
    _embedding_model = model_name
    _embedding_cache = {}


def _get_client():
    global _client
    if _client is None:
        set_embedding_model(DEFAULT_EMBEDDING_MODEL)
    return _client


def get_embedding(text: str) -> list:
    """Get embedding for a text using the configured embedding model."""
    if np is None:
        require("NumPy", "embedding computation")
    key = _cache_key(text)
    if key in _embedding_cache:
        return _embedding_cache[key]
    client = _get_client()
    embedding = client.embeddings.create(
        model=_embedding_model,
        input=text
    ).data[0].embedding
    _embedding_cache[key] = embedding
    return embedding


_doc_embeddings = None


def get_doc_embeddings() -> np.ndarray:
    """Get pre-computed document embeddings."""
    _require_numpy("document embedding computation")
    global _doc_embeddings
    if _doc_embeddings is None:
        logger.info("Computing document embeddings...")
        _doc_embeddings = np.array([get_embedding(text) for text in doc_texts])
        logger.info(f"Computed embeddings for {len(doc_texts)} documents")
    return _doc_embeddings


_index_dense = None


def _get_index():
    """Get or create FAISS index for dense retrieval."""
    _require_faiss("dense retrieval indexing")
    _require_numpy("dense retrieval indexing")
    global _index_dense
    if _index_dense is None:
        doc_emb = get_doc_embeddings()
        doc_emb = doc_emb.astype("float32")
        faiss.normalize_L2(doc_emb)
        _index_dense = faiss.IndexFlatIP(doc_emb.shape[1])
        _index_dense.add(doc_emb)
    return _index_dense


def dense_scores(query: str) -> dict:
    """Compute dense (semantic) similarity scores for all documents."""
    _require_faiss("dense retrieval scoring")
    _require_numpy("dense retrieval scoring")
    q = np.array([get_embedding(query)], dtype="float32")
    faiss.normalize_L2(q)

    index = _get_index()
    scores, idx = index.search(q, len(doc_ids))

    return {
        doc_ids[i]: float(scores[0][j])
        for j, i in enumerate(idx[0])
    }


def retrieve_dense(query: str, k: int = 5) -> list:
    """Retrieve top-k documents using dense (semantic) similarity."""
    scores = dense_scores(query)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:k]


_tokenized_corpus = None
_bm25 = None


def _get_bm25():
    """Get or create BM25 index."""
    _require_bm25("BM25 retrieval")
    global _tokenized_corpus, _bm25
    if _tokenized_corpus is None:
        _tokenized_corpus = [doc.lower().split() for doc in doc_texts]
        _bm25 = BM25Okapi(_tokenized_corpus)
    return _bm25


def bm25_scores(query: str) -> dict:
    """Compute BM25 (keyword) scores for all documents."""
    _require_bm25("BM25 retrieval scoring")
    bm25 = _get_bm25()
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    max_score = max(scores) if max(scores) > 0 else 1

    return {
        doc_ids[i]: float(scores[i] / max_score)
        for i in range(len(doc_ids))
    }


def retrieve_bm25(query: str, k: int = 5) -> list:
    """Retrieve top-k documents using BM25 (keyword) search."""
    scores = bm25_scores(query)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:k]


def detect_query_type(query: str) -> str:
    """Detect query type: lexical, temporal, logical, or semantic."""
    q = query.lower()

    if "starts with" in q:
        return "lexical"

    if "century" in q:
        return "temporal"

    if "not" in q or "but" in q:
        return "logical"

    return "semantic"


def rewrite_query(query: str) -> str:
    """Rewrite query for better retrieval."""
    q = query.lower()

    if "not born in europe" in q:
        return "people born outside europe"

    return query


def extract_first_name(text: str) -> str:
    """Extract first name from document text."""
    text = text.replace(",", "").replace("(", "").replace(")", "")
    tokens = text.split()

    titles = {"sir", "dr", "mr", "mrs", "ms", "professor"}

    for token in tokens:
        if token.lower() not in titles:
            return token

    return tokens[0]


def extract_letter(query: str) -> str:
    """Extract letter from 'starts with X' queries."""
    match = re.search(r"starts with\s+([a-zA-Z])", query)

    if match:
        return match.group(1).lower()

    letters = re.findall(r"[a-zA-Z]", query)
    return letters[-1].lower() if letters else None


def extract_years(text: str) -> list:
    """Extract years from text."""
    return [
        int(y)
        for y in re.findall(r"\b(1[6-9]\d{2}|20\d{2})\b", text)
    ]


def rule_score(query: str, doc: dict) -> float:
    """Compute rule-based score for lexical queries."""
    q = query.lower()
    text = doc["text"]

    if "starts with" in q:
        letter = extract_letter(query)

        if not letter:
            return 0.0

        first_name = extract_first_name(text)

        return 1.0 if first_name.lower().startswith(letter) else 0.0

    return 0.0


def metadata_score(query: str, doc: dict) -> float:
    """Compute metadata-based score for temporal queries."""
    q = query.lower()
    text = doc["text"]

    if "20th century but not born" in q:
        years = extract_years(text)

        if not years:
            return 0.0

        birth_year = min(years)
        lived_20th = any(y >= 1900 for y in years)
        born_before_20th = birth_year < 1900

        return 1.0 if lived_20th and born_before_20th else 0.0

    return 0.0


def get_weights(query: str) -> dict:
    """Get scoring weights based on query type."""
    q = query.lower()

    if "starts with" in q:
        return {
            "dense": 0.9,
            "bm25": 0.1,
            "rule": 0.0,
            "meta": 0.0
        }

    if "century" in q:
        return {
            "dense": 0.3,
            "bm25": 0.0,
            "rule": 0.0,
            "meta": 0.7
        }

    if "not" in q:
        return {
            "dense": 0.8,
            "bm25": 0.0,
            "rule": 0.0,
            "meta": 0.2
        }

    return {
        "dense": 0.7,
        "bm25": 0.3,
        "rule": 0.0,
        "meta": 0.0
    }


def experimental_selection(query: str, k: int = 5) -> list:
    """Hybrid selection combining dense, BM25, and query-aware scoring."""
    q = query.lower()
    rewritten_query = rewrite_query(query)

    qtype = detect_query_type(query)
    dense = dense_scores(rewritten_query)
    bm25_score_map = bm25_scores(query)

    weights = get_weights(query)

    if qtype == "lexical":
        candidates = [d for d in documents if rule_score(query, d) == 1.0]

        if not candidates:
            candidates = documents

        ranked = sorted(
            candidates,
            key=lambda d: (
                weights["dense"] * dense.get(d["id"], 0.0) +
                weights["bm25"] * bm25_score_map.get(d["id"], 0.0)
            ),
            reverse=True
        )

        return [{
            "doc_id": d["id"],
            "final_score": (
                weights["dense"] * dense.get(d["id"], 0.0) +
                weights["bm25"] * bm25_score_map.get(d["id"], 0.0)
            ),
            "dense_score": dense.get(d["id"], 0.0),
            "bm25_score": bm25_score_map.get(d["id"], 0.0),
            "rule_score": rule_score(query, d),
            "metadata_score": metadata_score(query, d),
            "text": d["text"]
        } for d in ranked[:k]]

    if qtype == "temporal":
        candidates = [d for d in documents if metadata_score(query, d) == 1.0]

        if not candidates:
            candidates = documents

        ranked = sorted(
            candidates,
            key=lambda d: (
                weights["dense"] * dense.get(d["id"], 0.0) +
                weights["meta"] * metadata_score(query, d)
            ),
            reverse=True
        )

        return [{
            "doc_id": d["id"],
            "final_score": (
                weights["dense"] * dense.get(d["id"], 0.0) +
                weights["meta"] * metadata_score(query, d)
            ),
            "dense_score": dense.get(d["id"], 0.0),
            "bm25_score": bm25_score_map.get(d["id"], 0.0),
            "rule_score": rule_score(query, d),
            "metadata_score": metadata_score(query, d),
            "text": d["text"]
        } for d in ranked[:k]]

    rows = []

    for doc in documents:
        doc_id = doc["id"]

        d_score = dense.get(doc_id, 0.0)
        b_score = bm25_score_map.get(doc_id, 0.0)
        r_score = rule_score(query, doc)
        m_score = metadata_score(query, doc)

        final_score = (
            weights["dense"] * d_score +
            weights["bm25"] * b_score +
            weights["rule"] * r_score +
            weights["meta"] * m_score
        )

        rows.append({
            "doc_id": doc_id,
            "final_score": final_score,
            "dense_score": d_score,
            "bm25_score": b_score,
            "rule_score": r_score,
            "metadata_score": m_score,
            "text": doc["text"]
        })

    ranked = sorted(rows, key=lambda x: x["final_score"], reverse=True)

    return ranked[:k]


def retrieve_experimental(query: str, k: int = 5) -> list:
    """Retrieve doc_ids using experimental selection."""
    return [row["doc_id"] for row in experimental_selection(query, k)]


def retrieve_smart(query: str, k: int = 5) -> list:
    """Smart retrieval with query-type aware routing."""
    qtype = detect_query_type(query)
    rewritten_query = rewrite_query(query)

    if qtype == "lexical":
        scored = experimental_selection(query, k=len(doc_ids))
        filtered = [r["doc_id"] for r in scored if r["rule_score"] == 1.0]
        return filtered[:k]

    if qtype == "temporal":
        scored = experimental_selection(query, k=len(doc_ids))
        filtered = [r["doc_id"] for r in scored if r["metadata_score"] == 1.0]

        if filtered:
            return filtered[:k]

        return [x[0] for x in retrieve_dense(rewritten_query, k)]

    if qtype == "logical":
        return [x[0] for x in retrieve_dense(rewritten_query, k)]

    return [x[0] for x in retrieve_dense(rewritten_query, k)]


def precision_at_k(retrieved: list, gt: list, k: int = 5) -> float:
    """Compute precision@k."""
    retrieved = retrieved[:k]
    return len(set(retrieved) & set(gt)) / k


def recall_at_k(retrieved: list, gt: list, k: int = 5) -> float:
    """Compute recall@k."""
    retrieved = retrieved[:k]
    return len(set(retrieved) & set(gt)) / len(gt) if len(gt) > 0 else 0.0


def f1_score_at_k(retrieved: list, gt: list, k: int = 5) -> float:
    """Compute F1@k."""
    p = precision_at_k(retrieved, gt, k)
    r = recall_at_k(retrieved, gt, k)
    if p + r == 0:
        return 0.0
    return 2 * (p * r) / (p + r)


def mrr(retrieved: list, gt: list) -> float:
    """Compute Mean Reciprocal Rank."""
    for i, doc in enumerate(retrieved):
        if doc in gt:
            return 1 / (i + 1)
    return 0.0


def dcg_at_k(retrieved: list, gt: list, k: int = 5) -> float:
    """Compute Discounted Cumulative Gain@k."""
    dcg = 0.0
    for i, doc in enumerate(retrieved[:k]):
        if doc in gt:
            dcg += 1 / np.log2(i + 2)
    return dcg


def ndcg_at_k(retrieved: list, gt: list, k: int = 5) -> float:
    """Compute Normalized DCG@k."""
    ideal = sorted(gt, key=lambda x: 1, reverse=True)
    idcg = dcg_at_k(ideal, gt, k)
    if idcg == 0:
        return 0.0
    return dcg_at_k(retrieved, gt, k) / idcg


def compute_all_metrics(retrieved: list, gt: list, k: int = 5) -> dict:
    """Compute all retrieval metrics."""
    return {
        "precision": precision_at_k(retrieved, gt, k),
        "recall": recall_at_k(retrieved, gt, k),
        "f1": f1_score_at_k(retrieved, gt, k),
        "mrr": mrr(retrieved, gt),
        "ndcg": ndcg_at_k(retrieved, gt, k)
    }


def score_label(score: float) -> str:
    """Label scores as high/medium/low."""
    if score > 0.8:
        return "high"
    elif score > 0.5:
        return "medium"
    return "low"


def set_documents(new_documents: list):
    """Replace the default documents with custom ones."""
    global documents, doc_ids, doc_texts, doc_id_to_index, _doc_embeddings, _index_dense, _tokenized_corpus, _bm25
    documents = new_documents
    doc_ids = [d["id"] for d in documents]
    doc_texts = [d["text"] for d in documents]
    doc_id_to_index = {doc_id: i for i, doc_id in enumerate(doc_ids)}
    _doc_embeddings = None
    _index_dense = None
    _tokenized_corpus = None
    _bm25 = None
