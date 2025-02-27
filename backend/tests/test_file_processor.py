import pytest
from fastapi import UploadFile
import io
import os
import shutil
from unittest.mock import Mock, patch, mock_open
from services.file_processor import FileProcessor
from services.exceptions import FileValidationError, DocumentProcessingError
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
def file_processor(settings, mock_logger):
    return FileProcessor(settings)

@pytest.fixture(autouse=True)
def cleanup_after_test():
    # This fixture will run automatically after each test
    yield
    # Clean up any files in the default processed_content directory
    if os.path.exists("processed_content"):
        shutil.rmtree("processed_content")

def create_upload_file(content: str, filename: str) -> UploadFile:
    return UploadFile(
        file=io.BytesIO(content.encode()),
        filename=filename
    )

class TestFileProcessor:
    def test_process_text_file_success(self, file_processor, mock_logger):
        
        content = "Hello, this is a test file"
        file = create_upload_file(content, "test.txt")
        
        
        result = file_processor.process_file(file)
        
        # 
        assert result == content
        mock_logger.info.assert_called()
        
    def test_process_document_success(self, file_processor, mock_logger):
        
        content = "Test document content"
        file = create_upload_file(content, "test.docx")
        
        with patch('services.file_processor.DocumentConverter') as MockConverter:
            mock_converter = Mock()
            mock_document = Mock()
            mock_document.export_to_markdown.return_value = "Converted content"
            mock_converter.convert.return_value.document = mock_document
            MockConverter.return_value = mock_converter
            
            result = file_processor.process_file(file)
            
            assert result == "Converted content"
            mock_converter.convert.assert_called_once()
            mock_logger.info.assert_called()
            
    def test_invalid_file_extension(self, file_processor):
        
        file = create_upload_file("content", "test.invalid")
        
        with pytest.raises(FileValidationError):
            file_processor.process_file(file)
            
    def test_document_processing_error(self, file_processor):
        
        file = create_upload_file("content", "test.docx")
        
        with patch('services.file_processor.DocumentConverter') as MockConverter:
            mock_converter = Mock()
            mock_converter.convert.side_effect = Exception("Conversion failed")
            MockConverter.return_value = mock_converter
            
            with pytest.raises(DocumentProcessingError):
                file_processor.process_file(file)
                
    def test_store_processed_content(self, file_processor, tmp_path):
        
        content = "Test content"
        file = create_upload_file(content, "test.txt")
        processed_dir = str(tmp_path / "processed")
        
        try:
            
            result = file_processor.process_file(
                file,
                is_store_processed_content=True,
                processed_content_dir=processed_dir
            )
            
            # 
            assert result == content
            expected_output_path = os.path.join(processed_dir, "test_txt.md")
            assert os.path.exists(expected_output_path)
            with open(expected_output_path, 'r') as f:
                assert f.read() == content
        finally:
            # Clean up
            if os.path.exists(processed_dir):
                shutil.rmtree(processed_dir)
            
    def test_store_processed_content_directory_creation(self, file_processor, tmp_path):
        
        content = "Test content"
        file = create_upload_file(content, "test.txt")
        processed_dir = str(tmp_path / "new_dir" / "processed")
        
        try:
            
            file_processor.process_file(
                file,
                is_store_processed_content=True,
                processed_content_dir=processed_dir
            )
            
            # 
            assert os.path.exists(processed_dir)
        finally:
            # Clean up
            if os.path.exists(os.path.dirname(processed_dir)):  # Clean up the parent dir
                shutil.rmtree(os.path.dirname(processed_dir))
            
    def test_store_processed_content_write_error(self, file_processor, mock_logger):
        
        content = "Test content"
        file = create_upload_file(content, "test.txt")
        
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = IOError("Write failed")
            
            
            result = file_processor.process_file(
                file,
                is_store_processed_content=True
            )
            
            assert result == content  # Should still return content even if storage fails
            mock_logger.error.assert_called_once() 