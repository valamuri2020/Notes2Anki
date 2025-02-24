from fastapi import UploadFile, HTTPException
from docling.document_converter import DocumentConverter
import tempfile
import os
from config import Settings
from services.validator import Validator
from google import genai


class FileProcessor:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.validator = Validator(self.settings)
        self.google_client = genai.Client()

    def _extract_content(self, file: UploadFile) -> str:
        if file.filename.endswith(".txt"):
            content = file.file.read()
            return content.decode()
        elif file.filename.endswith(".pdf"):
            try:
                # Upload using the File API
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    content = file.file.read()
                    temp_file.write(content)
                    temp_file.flush()
                    uploaded_file = self.google_client.files.upload(
                        file=temp_file.name, config=dict(mime_type="application/pdf")
                    )
                os.unlink(temp_file.name)  # Clean up the temporary file

                response = self.google_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=[
                        uploaded_file,
                        "Extract all of the contents in the file and return it as markdown. If there are any images/diagrams/charts, describe what it's showing and the concept it highlights by enclosing that in <diagram></diagram> tags.",
                    ],
                )
                return response.text

            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Error processing file: {str(e)}"
                )
        else:
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


if __name__ == "__main__":
    import io
    import sys
    from dotenv import load_dotenv
    from config import Settings
    from fastapi import UploadFile

    load_dotenv()
    demo_filepath = sys.argv[1]
    filename = os.path.basename(demo_filepath)

    with open(demo_filepath, "rb") as f:
        file_content = f.read()

    # use same interface as server to process file
    upload_file = UploadFile(file=io.BytesIO(file_content), filename=filename)

    print("Created UploadFile")

    settings = Settings()
    processor = FileProcessor(settings)
    text = processor.process_file(upload_file)
    print(text)
