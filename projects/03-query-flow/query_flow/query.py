"""Query type definitions and utilities."""

from enum import Enum


class QueryType(Enum):
    SEMANTIC = "semantic"
    LEXICAL = "lexical"
    TEMPORAL = "temporal"
    LOGICAL = "logical"