"""QueryAnalyzer - Reusable query understanding component."""

import re
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class QueryType(Enum):
    """Query type classification."""
    SEMANTIC = "semantic"
    LEXICAL = "lexical"
    TEMPORAL = "temporal"
    LOGICAL = "logical"


@dataclass
class QueryAnalysis:
    """Analysis result for a query."""
    query_type: QueryType
    rewritten_query: str
    detected_patterns: list
    confidence: float
    suggested_retrieval: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query_type": self.query_type.value,
            "rewritten_query": self.rewritten_query,
            "detected_patterns": self.detected_patterns,
            "confidence": self.confidence,
            "suggested_retrieval": self.suggested_retrieval
        }


class QueryAnalyzer:
    """Reusable query understanding and analysis."""

    PATTERNS = {
        "starts_with": (r"starts with (?:the letter )?([a-zA-Z])", "lexical"),
        "century": (r"(\d+)(?:st|nd|rd|th) century", "temporal"),
        "not_clause": (r"\bnot\b", "logical"),
        "but_clause": (r"\bbut\b", "logical"),
        "comparison": (r"(?:greater|less|more|less|fewer) than", "logical"),
        "born_in": (r"born in", "semantic"),
        "year": (r"\b(1[6-9]\d{2}|20\d{2})\b", "semantic"),
    }

    REWRITE_RULES = {
        "not born in europe": "people born outside europe",
        "not american": "non-american",
        "not from europe": "outside europe",
        "starts with the letter": "starts with",
    }

    @classmethod
    def detect(cls, query: str) -> str:
        """Detect query type from query string."""
        q = query.lower()

        if "starts with" in q:
            return "lexical"

        if "century" in q:
            return "temporal"

        if "not" in q or "but" in q:
            return "logical"

        return "semantic"

    @classmethod
    def analyze(cls, query: str) -> QueryAnalysis:
        """Perform comprehensive query analysis."""
        q = query.lower()
        detected_patterns = []
        query_type_str = "semantic"

        for pattern_name, (pattern_regex, ptype) in cls.PATTERNS.items():
            if re.search(pattern_regex, q):
                detected_patterns.append(pattern_name)
                if ptype == "lexical" or ptype == "temporal":
                    query_type_str = ptype
                    break
                elif ptype == "logical" and query_type_str == "semantic":
                    query_type_str = "logical"

        if "lexical" in detected_patterns:
            query_type_str = "lexical"
        elif "century" in detected_patterns:
            query_type_str = "temporal"
        elif "not_clause" in detected_patterns or "but_clause" in detected_patterns:
            query_type_str = "logical"

        rewritten = cls.rewrite(query)
        confidence = cls._calculate_confidence(detected_patterns, query_type_str)
        suggested = cls._suggest_retrieval(query_type_str)

        return QueryAnalysis(
            query_type=QueryType(query_type_str),
            rewritten_query=rewritten,
            detected_patterns=detected_patterns,
            confidence=confidence,
            suggested_retrieval=suggested
        )

    @classmethod
    def rewrite(cls, query: str) -> str:
        """Rewrite query for better retrieval."""
        q = query.lower()

        for pattern, replacement in cls.REWRITE_RULES.items():
            if pattern in q:
                return query.replace(pattern, replacement)

        return query

    @classmethod
    def _calculate_confidence(cls, patterns: list, query_type: str) -> float:
        """Calculate confidence of the detection."""
        if not patterns:
            return 0.5

        base_confidence = 0.6

        if query_type in ["lexical", "temporal"]:
            base_confidence += 0.3
        elif query_type == "logical":
            base_confidence += 0.2

        if len(patterns) > 1:
            base_confidence += 0.1

        return min(base_confidence, 1.0)

    @classmethod
    def _suggest_retrieval(cls, query_type: str) -> str:
        """Suggest appropriate retrieval method."""
        suggestions = {
            "lexical": "Use rule-based filtering + dense retrieval",
            "temporal": "Use metadata scoring + dense retrieval",
            "logical": "Use dense retrieval with semantic matching",
            "semantic": "Use hybrid dense + BM25 retrieval"
        }
        return suggestions.get(query_type, "Use hybrid retrieval")

    @classmethod
    def extract_entities(cls, query: str) -> dict:
        """Extract entities from query."""
        result = {}

        letter_match = re.search(r"starts with (?:the letter )?([a-zA-Z])", query.lower())
        if letter_match:
            result["letter"] = letter_match.group(1).lower()

        year_matches = re.findall(r"\b(1[6-9]\d{2}|20\d{2})\b", query)
        if year_matches:
            result["years"] = [int(y) for y in year_matches]

        country_matches = re.findall(r"\b(europe|america|american|european|asian|african)\b", query.lower())
        if country_matches:
            result["locations"] = country_matches

        return result