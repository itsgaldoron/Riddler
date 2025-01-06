"""Unit tests for OpenAI service"""

import pytest
from unittest.mock import patch, MagicMock
from services.openai_service import OpenAIService
from config.exceptions import RiddlerException

@pytest.fixture
def openai_service():
    """Create OpenAI service instance"""
    return OpenAIService()

def test_init(openai_service):
    """Test OpenAI service initialization"""
    assert openai_service.model == "gpt-4"
    assert openai_service.max_tokens == 500
    assert openai_service.temperature == 0.7

@patch('openai.ChatCompletion.create')
def test_generate_riddle_success(mock_create, openai_service):
    """Test successful riddle generation"""
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = """
    {
        "riddle": "What has cities, but no houses?",
        "answer": "A map",
        "explanation": "A map shows cities but doesn't contain actual houses",
        "fun_fact": "The oldest known map is from ancient Babylon"
    }
    """
    mock_create.return_value = mock_response
    
    result = openai_service.generate_riddle("geography", "medium")
    
    # Verify result structure
    assert isinstance(result, dict)
    assert "riddle" in result
    assert "answer" in result
    assert "explanation" in result
    assert "fun_fact" in result
    
    # Verify API call
    mock_create.assert_called_once()
    args = mock_create.call_args[1]
    assert args["model"] == "gpt-4"
    assert args["temperature"] == 0.7
    assert args["max_tokens"] == 500

@patch('openai.ChatCompletion.create')
def test_generate_riddle_invalid_response(mock_create, openai_service):
    """Test handling invalid API response"""
    # Mock invalid response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Invalid JSON"
    mock_create.return_value = mock_response
    
    with pytest.raises(RiddlerException) as exc_info:
        openai_service.generate_riddle("geography", "medium")
    assert "Failed to parse riddle response" in str(exc_info.value)

@patch('openai.ChatCompletion.create')
def test_generate_riddle_api_error(mock_create, openai_service):
    """Test handling API errors"""
    # Mock API error
    mock_create.side_effect = Exception("API error")
    
    with pytest.raises(RiddlerException) as exc_info:
        openai_service.generate_riddle("geography", "medium")
    assert "API error" in str(exc_info.value)

def test_generate_riddle_invalid_category(openai_service):
    """Test handling invalid category"""
    with pytest.raises(ValueError) as exc_info:
        openai_service.generate_riddle("invalid_category", "medium")
    assert "Invalid category" in str(exc_info.value)

def test_generate_riddle_invalid_difficulty(openai_service):
    """Test handling invalid difficulty"""
    with pytest.raises(ValueError) as exc_info:
        openai_service.generate_riddle("geography", "invalid_difficulty")
    assert "Invalid difficulty" in str(exc_info.value)

@patch('openai.ChatCompletion.create')
def test_generate_riddle_different_categories(mock_create, openai_service):
    """Test generating riddles for different categories"""
    # Mock response template
    def mock_response(category):
        mock = MagicMock()
        mock.choices[0].message.content = f"""
        {{
            "riddle": "Test {category} riddle",
            "answer": "Test answer",
            "explanation": "Test explanation",
            "fun_fact": "Test fun fact"
        }}
        """
        return mock
    
    # Test each category
    categories = ["geography", "math", "physics", "history", "logic", "wordplay"]
    for category in categories:
        mock_create.return_value = mock_response(category)
        result = openai_service.generate_riddle(category, "medium")
        assert category in result["riddle"]

@patch('openai.ChatCompletion.create')
def test_generate_riddle_different_difficulties(mock_create, openai_service):
    """Test generating riddles with different difficulties"""
    # Mock response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = """
    {
        "riddle": "Test riddle",
        "answer": "Test answer",
        "explanation": "Test explanation",
        "fun_fact": "Test fun fact"
    }
    """
    mock_create.return_value = mock_response
    
    # Test each difficulty
    difficulties = ["easy", "medium", "hard"]
    for difficulty in difficulties:
        result = openai_service.generate_riddle("geography", difficulty)
        assert isinstance(result, dict)
        
        # Verify difficulty was passed to API
        args = mock_create.call_args[1]
        assert difficulty in str(args["messages"]) 