class Notes2AnkiError(Exception):
    """Base exception for all Notes2Anki errors."""
    pass


class ValidationError(Notes2AnkiError):
    """Base class for validation errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}


class FileValidationError(ValidationError):
    """Raised when file validation fails."""
    pass


class FileSizeError(FileValidationError):
    """Raised when file size exceeds limits."""
    pass


class FileTypeError(FileValidationError):
    """Raised when file type is not supported."""
    pass


class FileCountError(FileValidationError):
    """Raised when too many files are uploaded."""
    pass


class ProcessingError(Notes2AnkiError):
    """Base class for processing errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}


class FileProcessingError(ProcessingError):
    """Raised when there's an error processing a file."""
    pass


class PDFProcessingError(FileProcessingError):
    """Raised when there's an error processing a PDF file."""
    pass


class DocumentProcessingError(FileProcessingError):
    """Raised when there's an error processing a document."""
    pass


class LLMError(ProcessingError):
    """Base class for LLM-related errors."""
    pass


class LLMAPIError(LLMError):
    """Raised when there's an error communicating with the LLM API."""
    pass


class LLMResponseError(LLMError):
    """Raised when there's an error parsing the LLM response."""
    pass


class AnkiError(Notes2AnkiError):
    """Base class for Anki-related errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}


class AnkiDeckGenerationError(AnkiError):
    """Raised when there's an error generating the Anki deck."""
    pass 

class CSVGenerationError(AnkiError):
    """Raised when there's an error generating the Anki deck."""
    pass 

class PDFGenerationError(AnkiError):
    """Raised when there's an error generating the Anki deck."""
    pass 
