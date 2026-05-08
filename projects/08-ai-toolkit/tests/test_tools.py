"""Unit tests for the tool-calling framework."""
import pytest
import json

import sys
sys.path.insert(0, "src")

from functions import search_docs, read_document, summarise_document, extract_keywords, answer_question, get_chuck_norris_fact
from tools_map import tools_map
from utils import parse_arguments, validate_tool_arguments, ValidationError
from chain import ToolChain, create_research_chain
from config import LLM_CONFIG, TOOL_CONFIG


class TestFunctions:
    """Test tool functions."""

    def test_search_docs(self):
        result = search_docs("Python")
        data = json.loads(result)
        assert "query" in data
        assert "results" in data
        assert data["query"] == "Python"

    def test_read_document(self):
        result = read_document("123")
        data = json.loads(result)
        assert data["id"] == "123"
        assert "content" in data

    def test_summarise_document(self):
        result = summarise_document("456")
        data = json.loads(result)
        assert data["id"] == "456"
        assert "summary" in data

    def test_extract_keywords(self):
        result = extract_keywords("test text")
        data = json.loads(result)
        assert "keywords" in data
        assert len(data["keywords"]) > 0

    def test_answer_question(self):
        result = answer_question("What is Python?", "Python is a language")
        data = json.loads(result)
        assert data["question"] == "What is Python?"
        assert "answer" in data


class TestToolsMap:
    """Test tools map."""

    def test_all_tools_registered(self):
        expected = ["search_docs", "read_document", "summarise_document", 
                   "extract_keywords", "answer_question", "get_chuck_norris_fact"]
        for tool in expected:
            assert tool in tools_map
            assert callable(tools_map[tool])


class TestUtils:
    """Test utility functions."""

    def test_parse_arguments(self):
        args = parse_arguments({"num": "42", "text": "hello"})
        assert args["num"] == 42
        assert args["text"] == "hello"

    def test_parse_arguments_empty(self):
        args = parse_arguments({})
        assert args == {}

    def test_parse_arguments_none(self):
        args = parse_arguments(None)
        assert args == {}

    def test_validate_tool_arguments_valid(self):
        schema = {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
        assert validate_tool_arguments("search_docs", {"query": "test"}, schema)

    def test_validate_tool_arguments_missing_required(self):
        schema = {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
        with pytest.raises(ValidationError):
            validate_tool_arguments("search_docs", {}, schema)


class TestConfig:
    """Test configuration."""

    def test_llm_config(self):
        assert "model" in LLM_CONFIG
        assert "base_url" in LLM_CONFIG

    def test_tool_config(self):
        assert "max_iterations" in TOOL_CONFIG
        assert "retry_attempts" in TOOL_CONFIG


class TestChain:
    """Test tool chaining."""

    def test_tool_chain_creation(self):
        chain = ToolChain()
        chain.add_step("search_docs")
        assert len(chain.steps) == 1

    def test_tool_chain_with_transform(self):
        chain = ToolChain()
        chain.add_step("search_docs")
        chain.add_step("read_document", lambda r: {"doc_id": "1"})
        assert len(chain.steps) == 2

    def test_create_research_chain(self):
        chain = create_research_chain()
        assert len(chain.steps) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])