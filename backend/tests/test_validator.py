import pytest
from fastapi import UploadFile
import io
from unittest.mock import Mock, patch, MagicMock
from services.validator import Validator
from services.exceptions import FileCountError, FileTypeError, FileSizeError
from config import Settings

@pytest.fixture
def mock_logger():
    mock = Mock()
    with patch('services.logger.setup_logger', return_value=mock):
        yield mock

@pytest.fixture
def settings():
    return Settings()

@pytest.fixture
def validator(settings, mock_logger):
    return Validator(settings)

def create_upload_file(content: str, filename: str) -> UploadFile:
    """Helper to create an UploadFile with specific content"""
    return UploadFile(
        file=io.BytesIO(content.encode()),
        filename=filename
    )

def create_mock_file(size_bytes: int, filename: str) -> UploadFile:
    """Create a mock file with a specific size without actually allocating memory"""
    mock_file = MagicMock()
    mock_file.seek.return_value = None
    mock_file.tell.return_value = size_bytes
    
    file = UploadFile(
        file=mock_file,
        filename=filename
    )
    return file

class TestValidator:
    def test_validate_file_count_success(self, validator, settings):
        # Arrange
        files = [create_upload_file("content", f"test{i}.txt") for i in range(settings.MAX_FILES)]
        
        # Act & Assert
        validator.validate_file_count(files)  # Should not raise

    def test_validate_file_count_exceeds_limit(self, validator, settings):
        # Arrange
        files = [create_upload_file("content", f"test{i}.txt") for i in range(settings.MAX_FILES + 1)]
        
        # Act & Assert
        with pytest.raises(FileCountError) as exc_info:
            validator.validate_file_count(files)
        
        assert exc_info.value.details["file_count"] == settings.MAX_FILES + 1
        assert exc_info.value.details["max_files"] == settings.MAX_FILES

    def test_validate_file_ext_success(self, validator):
        # Test each allowed extension
        for ext in ["txt", "pdf", "docx", "pptx"]:
            file = create_upload_file("content", f"test.{ext}")
            validator.validate_file_ext(file)  # Should not raise

    def test_validate_file_ext_invalid(self, validator):
        # Arrange
        file = create_upload_file("content", "test.invalid")
        
        # Act & Assert
        with pytest.raises(FileTypeError) as exc_info:
            validator.validate_file_ext(file)
        
        assert exc_info.value.details["filename"] == "test.invalid"
        assert exc_info.value.details["extension"] == "invalid"
        assert exc_info.value.details["allowed_types"] == validator.settings.ALLOWED_TYPES

    def test_validate_file_size_success(self, validator, settings):
        # Arrange - Create a mock file just under the size limit
        size_bytes = (settings.MAX_FILE_SIZE - 1) * 1024 * 1024
        file = create_mock_file(size_bytes, "test.txt")
        
        # Act & Assert
        validator.validate_file_size(file)  # Should not raise

    def test_validate_file_size_exceeds_limit(self, validator, settings):
        # Arrange - Create a mock file just over the size limit
        size_bytes = (settings.MAX_FILE_SIZE + 1) * 1024 * 1024
        file = create_mock_file(size_bytes, "test.txt")
        
        # Act & Assert
        with pytest.raises(FileSizeError) as exc_info:
            validator.validate_file_size(file)
        
        assert exc_info.value.details["filename"] == "test.txt"
        assert exc_info.value.details["file_size_mb"] > settings.MAX_FILE_SIZE
        assert exc_info.value.details["max_size_mb"] == settings.MAX_FILE_SIZE

    def test_validate_file_size_resets_seek_position(self, validator):
        # Arrange
        content = "test content"
        file = create_upload_file(content, "test.txt")
        
        # Act
        validator.validate_file_size(file)
        
        # Assert
        # After validation, we should be able to read the content
        # This verifies that the file pointer was reset to the start
        assert file.file.read().decode() == content 