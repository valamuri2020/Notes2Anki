from fastapi import UploadFile
from docling.document_converter import DocumentConverter
import tempfile
import os
from config import Settings
from services.validator import Validator
from google import genai
from services.logger import LoggerMixin
from services.exceptions import PDFProcessingError, DocumentProcessingError
import asyncio


class FileProcessor(LoggerMixin):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.validator = Validator(self.settings)
        self.google_client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    async def _extract_content(self, file: UploadFile) -> str:
        if file.filename.endswith(".txt"):
            self.logger.debug(
                "Processing text file",
                extra={"extra_fields": {"filename": file.filename}},
            )
            content = file.file.read()
            return content.decode()

        elif file.filename.endswith(".pdf"):
            self.logger.debug(
                "Processing PDF file",
                extra={"extra_fields": {"filename": file.filename}},
            )
            uploaded_file = None
            temp_file_path = None

            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file_path = temp_file.name
                    content = file.file.read()
                    temp_file.write(content)
                    temp_file.flush()

                    self.logger.debug("Uploading PDF to Google API")
                    uploaded_file = await self.google_client.aio.files.upload(
                        file=temp_file.name, config=dict(mime_type="application/pdf")
                    )

                self.logger.debug("Generating content from PDF using Gemini")
                response = await self.google_client.aio.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[
                        uploaded_file,
                        """Extract all of the contents in the file and return it as markdown. After each page, insert the text "[[Page N]]" where N is the page number.
                        If there are any images/diagrams/charts, describe what it's showing and the concept it highlights by enclosing that in <diagram></diagram> tags.""",
                    ],
                )
                return response.text

            except Exception as e:
                details = {"filename": file.filename, "error": str(e)}
                self.logger.error(
                    "Error processing PDF file", extra={"extra_fields": details}
                )
                raise PDFProcessingError("Failed to process PDF file", details=details)

            finally:
                # Clean up resources
                if uploaded_file:
                    try:
                        self.logger.debug("Cleaning up Google API uploaded file")
                        await self.google_client.aio.files.delete(
                            name=uploaded_file.name
                        )
                    except Exception as e:
                        self.logger.warning(
                            "Failed to clean up Google API file",
                            extra={"extra_fields": {"error": str(e)}},
                        )

                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        else:
            # Handle other document types
            self.logger.debug(
                "Processing document using DocumentConverter",
                extra={"extra_fields": {"filename": file.filename}},
            )
            temp_file_path = None

            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file_path = temp_file.name
                    content = file.file.read()
                    temp_file.write(content)
                    temp_file.flush()

                    converter = DocumentConverter()
                    res = converter.convert(temp_file.name)
                    return res.document.export_to_markdown()

            except Exception as e:
                details = {"filename": file.filename, "error": str(e)}
                self.logger.error(
                    "Error processing document", extra={"extra_fields": details}
                )
                raise DocumentProcessingError(
                    "Failed to process document", details=details
                )

            finally:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

    async def process_file(
        self,
        file: UploadFile,
        is_store_processed_content=os.getenv("IS_LOCAL_MODE", False),
        processed_content_dir="processed_content/",
    ) -> str:
        self.logger.info(
            "Starting file processing",
            extra={
                "extra_fields": {
                    "filename": file.filename,
                    "store_processed_content": is_store_processed_content,
                }
            },
        )

        # Validate file
        self.validator.validate_file_ext(file)
        self.validator.validate_file_size(file)

        # Extract content
        try:
            text = await self._extract_content(file)

            # Store processed content if requested
            if is_store_processed_content:
                os.makedirs(processed_content_dir, exist_ok=True)
                output_path = os.path.join(
                    processed_content_dir, "_".join(file.filename.split(".")) + ".md"
                )

                self.logger.debug(
                    "Storing processed content",
                    extra={
                        "extra_fields": {
                            "filename": file.filename,
                            "output_path": output_path,
                        }
                    },
                )

                try:
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(text)
                except Exception as e:
                    self.logger.error(
                        "Failed to store processed content",
                        extra={
                            "extra_fields": {
                                "filename": file.filename,
                                "output_path": output_path,
                                "error": str(e),
                            }
                        },
                    )
                    # Don't raise here as this is not critical to the main functionality

            self.logger.info(
                "File processing completed",
                extra={
                    "extra_fields": {
                        "filename": file.filename,
                        "content_length": len(text),
                    }
                },
            )
            return text
        except Exception as e:
            raise e


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

    settings = Settings()
    processor = FileProcessor(settings)
    text = asyncio.run(processor.process_file(upload_file))
    print(text)
