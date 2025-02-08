from fastapi import UploadFile, HTTPException
from docling.document_converter import DocumentConverter
import tempfile
import os
from typing import List, Dict
from ..config import Settings
from validator import Validator


class FileProcessor:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.validator = Validator(self.settings)
    
    def _extract_content(self, file: UploadFile) -> str:
        try:
            # Create a temporary file to store the uploaded content
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                # Write the uploaded file content to the temp file
                content = file.file.read()
                temp_file.write(content)
                temp_file.flush()
                
                # Use DocumentConverter to extract text
                converter = DocumentConverter()
                extracted_text = converter.extract_text(temp_file.name)
                
                return extracted_text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
        finally:
            # Clean up the temporary file
            if 'temp_file' in locals():
                os.unlink(temp_file.name)

    def process_file(self, file: UploadFile) -> str:
        self.validator.validate_file_ext(file)
        self.validator.validate_file_size(file)

        text = self._extract_content(file)
             
        return text