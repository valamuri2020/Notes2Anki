from config import Settings
from fastapi import UploadFile, HTTPException


class Validator:
    def __init__(self, settings: Settings):
        self.settings = settings

    def validate_file_count(self, files):
        if len(files) > self.settings.MAX_FILES:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {self.settings.MAX_FILES} files allowed per request",
            )

    def validate_file_ext(self, file: UploadFile) -> None:
        # Check file type
        ext = file.filename.split(".")[-1].lower()
        if ext not in self.settings.ALLOWED_TYPES:
            raise HTTPException(
                status_code=400, detail=f"File type .{ext} not supported"
            )

    def validate_file_size(self, file: UploadFile) -> None:
        # seek to end
        file.file.seek(0, 2)
        # get position of seek pointer
        file_size_bytes = file.file.tell()
        # reset pointer
        file.file.seek(0)

        file_size_mb = file_size_bytes / (1024 * 1024)
        if file_size_mb > self.settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File {file.filename} too large, exceeds {self.settings.MAX_FILE_SIZE}",
            )
