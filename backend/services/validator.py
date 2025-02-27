from config import Settings
from fastapi import UploadFile
from services.logger import LoggerMixin
from services.exceptions import FileCountError, FileTypeError, FileSizeError


class Validator(LoggerMixin):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings

    def validate_file_count(self, files: list[UploadFile]) -> None:
        self.logger.debug(
            "Validating file count",
            extra={
                "extra_fields": {
                    "file_count": len(files),
                    "max_files": self.settings.MAX_FILES
                }
            }
        )

        if len(files) > self.settings.MAX_FILES:
            error_msg = f"Maximum {self.settings.MAX_FILES} files allowed per request"
            details = {
                "file_count": len(files),
                "max_files": self.settings.MAX_FILES
            }
            
            self.logger.error(
                "File count validation failed",
                extra={"extra_fields": {**details, "error": error_msg}}
            )
            raise FileCountError(error_msg, details=details)

    def validate_file_ext(self, file: UploadFile) -> None:
        ext = file.filename.split(".")[-1].lower()

        self.logger.debug(
            "Validating file extension",
            extra={
                "extra_fields": {
                    "filename": file.filename,
                    "extension": ext,
                    "allowed_types": self.settings.ALLOWED_TYPES
                }
            }
        )

        if ext not in self.settings.ALLOWED_TYPES:
            error_msg = f"File type .{ext} not supported"
            details = {
                "filename": file.filename,
                "extension": ext,
                "allowed_types": self.settings.ALLOWED_TYPES
            }
            
            self.logger.error(
                "File extension validation failed",
                extra={"extra_fields": {**details, "error": error_msg}}
            )
            raise FileTypeError(error_msg, details=details)

    def validate_file_size(self, file: UploadFile) -> None:
        # Get file size
        file.file.seek(0, 2)  # Seek to end
        file_size_bytes = file.file.tell()  # Get current position
        file.file.seek(0)  # Reset to start

        file_size_mb = file_size_bytes / (1024 * 1024)

        self.logger.debug(
            "Validating file size",
            extra={
                "extra_fields": {
                    "filename": file.filename,
                    "file_size_mb": round(file_size_mb, 2),
                    "max_size_mb": self.settings.MAX_FILE_SIZE
                }
            }
        )

        if file_size_mb > self.settings.MAX_FILE_SIZE:
            error_msg = f"File {file.filename} too large, exceeds {self.settings.MAX_FILE_SIZE}MB"
            details = {
                "filename": file.filename,
                "file_size_mb": round(file_size_mb, 2),
                "max_size_mb": self.settings.MAX_FILE_SIZE
            }
            
            self.logger.error(
                "File size validation failed",
                extra={"extra_fields": {**details, "error": error_msg}}
            )
            raise FileSizeError(error_msg, details=details)
