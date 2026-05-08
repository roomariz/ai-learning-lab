"""Dataset loader abstraction for QueryFlow."""

import logging
from typing import Optional, Union, List
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """A single document in a dataset."""
    id: str
    text: str
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class Dataset:
    """Abstraction for loading and managing documents.
    
    Usage:
        # From list
        ds = Dataset.from_list([{"id": "1", "text": "..."}])
        
        # From JSON file
        ds = Dataset.from_json("documents.json")
        
        # From CSV
        ds = Dataset.from_csv("documents.csv")
        
        # Use with retriever
        retriever.set_documents(ds.documents)
    """

    def __init__(self, documents: List[Document]):
        self._documents = documents

    @classmethod
    def from_list(cls, data: List[dict]) -> "Dataset":
        """Create dataset from a list of dictionaries.
        
        Each dict should have 'id' and 'text' keys.
        Optional: 'metadata' key for additional data.
        """
        documents = []
        for item in data:
            doc = Document(
                id=item.get("id", item.get("_id", "")),
                text=item.get("text", item.get("content", "")),
                metadata=item.get("metadata", {})
            )
            documents.append(doc)
        
        logger.info(f"Loaded {len(documents)} documents from list")
        return cls(documents)

    @classmethod
    def from_json(cls, path: Union[str, Path]) -> "Dataset":
        """Load documents from JSON file."""
        import json
        with open(path, "r") as f:
            data = json.load(f)
        
        if isinstance(data, dict) and "documents" in data:
            data = data["documents"]
        
        return cls.from_list(data)

    @classmethod
    def from_csv(cls, path: Union[str, Path], text_column: str = "text", id_column: str = "id") -> "Dataset":
        """Load documents from CSV file."""
        import csv
        
        documents = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                doc = Document(
                    id=row.get(id_column, ""),
                    text=row.get(text_column, ""),
                    metadata={k: v for k, v in row.items() if k not in [text_column, id_column]}
                )
                documents.append(doc)
        
        logger.info(f"Loaded {len(documents)} documents from CSV")
        return cls(documents)

    @property
    def documents(self) -> List[dict]:
        """Return documents as list of dicts (for compatibility with retriever)."""
        return [
            {"id": doc.id, "text": doc.text, "metadata": doc.metadata}
            for doc in self._documents
        ]

    @property
    def ids(self) -> List[str]:
        """Return list of document IDs."""
        return [doc.id for doc in self._documents]

    @property
    def texts(self) -> List[str]:
        """Return list of document texts."""
        return [doc.text for doc in self._documents]

    def __len__(self) -> int:
        return len(self._documents)

    def __getitem__(self, index: int) -> Document:
        return self._documents[index]

    def filter(self, predicate) -> "Dataset":
        """Filter documents by a predicate function."""
        filtered = [doc for doc in self._documents if predicate(doc)]
        return Dataset(filtered)

    def map(self, func) -> "Dataset":
        """Apply a function to each document."""
        mapped = [func(doc) for doc in self._documents]
        return Dataset(mapped)