import pytest
from fastapi.testclient import TestClient
import json
from unittest.mock import Mock, patch, MagicMock
from main import app
from services.exceptions import FileValidationError, ProcessingError, LLMError
import os
from services.card_creator import Card

@pytest.fixture
def mock_logger():
    mock = Mock()
    with patch('services.logger.setup_logger', return_value=mock):
        yield mock

@pytest.fixture
def mock_app_logger():
    with patch('main.app_logger') as mock:
        yield mock

@pytest.fixture
def mock_processor():
    with patch('main.processor') as mock:
        yield mock

@pytest.fixture
def mock_validator():
    with patch('main.validator') as mock:
        yield mock

@pytest.fixture
def client(mock_logger, mock_app_logger, mock_processor, mock_validator):
    return TestClient(app)

def create_test_file(content: str, filename: str):
    return (filename, content.encode(), 'text/plain')

class TestAPI:
    def test_generate_flashcards_success(self, client, tmp_path, mock_processor):
        # Arrange
        request_data = {
            "id": "test-123",
            "multiple_decks": False,
            "output_format": "apkg",
            "deck_names": {
                "test1.txt": "test_deck",
                "test2.txt": "test_deck"
            }
        }
        files = [
            ("files", create_test_file("Test content 1", "test1.txt")),
            ("files", create_test_file("Test content 2", "test2.txt"))
        ]
        
        # Mock the card creation and deck generation
        with patch('services.card_creator.LLMCardCreator.create_cards') as mock_create_cards, \
             patch('services.anki_generator.AnkiDeckInterface.generate_deck') as mock_generate_deck:
            
            # Setup mocks
            mock_processor.process_file.return_value = "Processed content"
            mock_create_cards.return_value = [
                Card(id=1, concept="Test", description="Description")
            ]
            mock_generate_deck.return_value = str(tmp_path / "test_deck.apkg")
            
            # Create a dummy Anki file
            os.makedirs(tmp_path, exist_ok=True)
            with open(mock_generate_deck.return_value, 'wb') as f:
                f.write(b'dummy anki package')
            
            # Act
            response = client.post(
                "/generate",
                data={"request": json.dumps(request_data)},
                files=files
            )
            
            # Assert
            assert response.status_code == 200
            assert response.headers["x-request-id"] == "test-123"
            assert "test_deck.apkg" in response.headers["content-disposition"]

    def test_generate_flashcards_validation_error(self, client, mock_validator):
        # Arrange
        request_data = {
            "id": "test-123",
            "multiple_decks": False,
            "output_format": "apkg",
            "deck_names": {
                "test.invalid": "test_deck"
            }
        }
        files = [
            ("files", create_test_file("Test content", "test.invalid"))
        ]
        
        # Setup mock to raise validation error
        mock_validator.validate_file_ext.side_effect = FileValidationError(
            "File type .invalid not supported",
            details={"filename": "test.invalid"}
        )
        
        # Mock the validator to validate each file
        def validate_file(file):
            mock_validator.validate_file_ext(file)
            return True
            
        mock_validator.validate_file_count.return_value = True
        
        # Act
        response = client.post(
            "/generate",
            data={"request": json.dumps(request_data)},
            files=files
        )
        
        # Assert
        assert response.status_code == 400
        assert "File type .invalid not supported" in response.json()["detail"]

    def test_generate_flashcards_processing_error(self, client, mock_processor):
        # Arrange
        request_data = {
            "id": "test-123",
            "multiple_decks": False,
            "output_format": "apkg",
            "deck_names": {
                "test.txt": "test_deck"
            }
        }
        files = [
            ("files", create_test_file("Test content", "test.txt"))
        ]
        
        # Setup mock to raise processing error
        mock_processor.process_file.side_effect = ProcessingError("Processing failed")
        
        # Act
        response = client.post(
            "/generate",
            data={"request": json.dumps(request_data)},
            files=files
        )
        
        # Assert
        assert response.status_code == 500
        assert "Processing failed" in response.json()["detail"]

    def test_generate_flashcards_llm_error(self, client, mock_processor):
        # Arrange
        request_data = {
            "id": "test-123",
            "multiple_decks": False,
            "output_format": "apkg",
            "deck_names": {
                "test.txt": "test_deck"
            }
        }
        files = [
            ("files", create_test_file("Test content", "test.txt"))
        ]
        
        # Mock LLM error
        with patch('services.card_creator.LLMCardCreator.create_cards') as mock_create_cards:
            mock_processor.process_file.return_value = "Processed content"
            mock_create_cards.side_effect = LLMError("LLM API failed")
            
            # Act
            response = client.post(
                "/generate",
                data={"request": json.dumps(request_data)},
                files=files
            )
            
            # Assert
            assert response.status_code == 500
            assert "LLM API failed" in response.json()["detail"]

    def test_generate_flashcards_invalid_request(self, client):
        # Arrange - missing required field
        request_data = {
            "id": "test-123"
            # missing deck_names
        }
        files = [
            ("files", create_test_file("Test content", "test.txt"))
        ]
        
        # Act
        response = client.post(
            "/generate",
            data={"request": json.dumps(request_data)},
            files=files
        )
        
        # Assert
        assert response.status_code == 422  # FastAPI validation error

    def test_generate_flashcards_no_files(self, client):
        # Arrange
        request_data = {
            "id": "test-123",
            "multiple_decks": False,
            "output_format": "apkg",
            "deck_names": {
                "test1.txt": "test_deck"
            }
        }
        
        # Act
        response = client.post(
            "/generate",
            data={"request": json.dumps(request_data)},
            files=[]  # No files
        )
        
        # Assert
        assert response.status_code == 422
        assert "files" in str(response.json()["detail"])

    def test_generate_multiple_decks_success(self, client, tmp_path, mock_processor):
        # Arrange
        request_data = {
            "id": "test-123",
            "multiple_decks": True,
            "output_format": "apkg",
            "deck_names": {
                "test1.txt": "Deck One",
                "test2.txt": "Deck Two"
            }
        }
        files = [
            ("files", create_test_file("Test content 1", "test1.txt")),
            ("files", create_test_file("Test content 2", "test2.txt"))
        ]
        
        # Mock the card creation and deck generation
        with patch('services.card_creator.LLMCardCreator.create_cards') as mock_create_cards, \
             patch('services.anki_generator.AnkiDeckInterface.generate_deck') as mock_generate_deck:
            
            # Setup mocks
            mock_processor.process_file.return_value = "Processed content"
            mock_create_cards.return_value = [
                Card(id=1, concept="Test", description="Description")
            ]
            
            # Mock generate_deck to return different paths for each deck
            deck_paths = [
                str(tmp_path / "deck_one.apkg"),
                str(tmp_path / "deck_two.apkg")
            ]
            mock_generate_deck.side_effect = deck_paths
            
            # Create dummy deck files
            os.makedirs(tmp_path, exist_ok=True)
            for path in deck_paths:
                with open(path, 'wb') as f:
                    f.write(b'dummy anki package')
            
            # Create dummy zip file
            zip_path = str(tmp_path / "test-123.zip")
            with open(zip_path, 'wb') as f:
                f.write(b'dummy zip file')
            
            # Act
            response = client.post(
                "/generate",
                data={"request": json.dumps(request_data)},
                files=files
            )
            
            # Assert
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/zip"
            assert response.headers["x-request-id"] == "test-123"
            assert "filename=" in response.headers["content-disposition"]
            assert ".zip" in response.headers["content-disposition"]

    def test_generate_pdf_format_success(self, client, tmp_path, mock_processor):
        # Arrange
        request_data = {
            "id": "test-123",
            "multiple_decks": False,
            "output_format": "pdf",
            "deck_names": {
                "test1.txt": "PDF Deck"
            }
        }
        files = [
            ("files", create_test_file("Test content", "test1.txt"))
        ]
        
        # Mock the card creation and deck generation
        with patch('services.card_creator.LLMCardCreator.create_cards') as mock_create_cards, \
             patch('services.anki_generator.AnkiDeckInterface.generate_deck') as mock_generate_deck:
            
            # Setup mocks
            mock_processor.process_file.return_value = "Processed content"
            mock_create_cards.return_value = [
                Card(id=1, concept="Test", description="Description")
            ]
            mock_generate_deck.return_value = str(tmp_path / "PDF_Deck.pdf")
            
            # Create a dummy PDF file
            os.makedirs(tmp_path, exist_ok=True)
            with open(mock_generate_deck.return_value, 'wb') as f:
                f.write(b'dummy pdf content')
            
            # Act
            response = client.post(
                "/generate",
                data={"request": json.dumps(request_data)},
                files=files
            )
            
            # Assert
            assert response.status_code == 200
            assert "PDF_Deck.pdf" in response.headers["content-disposition"]
            assert response.headers["x-request-id"] == "test-123"

    def test_generate_csv_format_success(self, client, tmp_path, mock_processor):
        # Arrange
        request_data = {
            "id": "test-123",
            "multiple_decks": False,
            "output_format": "csv",
            "deck_names": {
                "test1.txt": "CSV Deck"
            }
        }
        files = [
            ("files", create_test_file("Test content", "test1.txt"))
        ]
        
        # Mock the card creation and deck generation
        with patch('services.card_creator.LLMCardCreator.create_cards') as mock_create_cards, \
             patch('services.anki_generator.AnkiDeckInterface.generate_deck') as mock_generate_deck:
            
            # Setup mocks
            mock_processor.process_file.return_value = "Processed content"
            mock_create_cards.return_value = [
                Card(id=1, concept="Test", description="Description")
            ]
            mock_generate_deck.return_value = str(tmp_path / "CSV_Deck.csv")
            
            # Create a dummy CSV file
            os.makedirs(tmp_path, exist_ok=True)
            with open(mock_generate_deck.return_value, 'wb') as f:
                f.write(b'question,answer,source\nTest,Description,test1.txt')
            
            # Act
            response = client.post(
                "/generate",
                data={"request": json.dumps(request_data)},
                files=files
            )
            
            # Assert
            assert response.status_code == 200
            assert "CSV_Deck.csv" in response.headers["content-disposition"]
            assert response.headers["x-request-id"] == "test-123"

    def test_generate_invalid_format(self, client):
        # Arrange
        request_data = {
            "id": "test-123",
            "multiple_decks": False,
            "output_format": "invalid",  # Invalid format
            "deck_names": {
                "test1.txt": "Invalid Format Deck"
            }
        }
        files = [
            ("files", create_test_file("Test content", "test1.txt"))
        ]
        
        # Act
        response = client.post(
            "/generate",
            data={"request": json.dumps(request_data)},
            files=files
        )
        
        # Assert
        assert response.status_code == 500
        assert "Unsupported output format" in response.json()["detail"] 