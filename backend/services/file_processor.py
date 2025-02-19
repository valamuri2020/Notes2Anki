from fastapi import UploadFile, HTTPException
from docling.document_converter import DocumentConverter
import tempfile
import os
from config import Settings
from services.validator import Validator


class FileProcessor:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.validator = Validator(self.settings)

    def _extract_content(self, file: UploadFile) -> str:
        if file.filename.endswith(".txt"):
            return file.file.read()
        try:
            # Create a temporary file to store the uploaded content
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                # Write the uploaded file content to the temp file
                content = file.file.read()
                temp_file.write(content)
                temp_file.flush()

                # Use DocumentConverter to extract text
                converter = DocumentConverter()
                res = converter.convert(temp_file.name)
                extracted_text = res.document.export_to_markdown()

                return extracted_text
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing file: {str(e)}"
            )
        finally:
            # Clean up the temporary file
            if "temp_file" in locals():
                os.unlink(temp_file.name)

    def process_file(self, file: UploadFile, processed_content_dir="mock_data/") -> str:
        print("Validating file type and size")
        self.validator.validate_file_ext(file)
        self.validator.validate_file_size(file)

        print("Extracting file content")
        text = self._extract_content(file)

        os.makedirs(processed_content_dir, exist_ok=True)
        output_path = os.path.join(
            processed_content_dir, "_".join(file.filename.split(".")) + ".md"
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        return text
