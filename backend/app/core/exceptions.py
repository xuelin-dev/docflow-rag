"""Custom exception classes for the application."""

from fastapi import HTTPException


class DocumentNotFoundError(HTTPException):
    """Raised when a document is not found."""

    def __init__(self, doc_id: str) -> None:
        super().__init__(status_code=404, detail=f"Document not found: {doc_id}")


class NamespaceNotFoundError(HTTPException):
    """Raised when a namespace is not found."""

    def __init__(self, name: str) -> None:
        super().__init__(status_code=404, detail=f"Namespace not found: {name}")


class IngestionError(Exception):
    """Raised when document ingestion fails."""

    def __init__(self, doc_id: str, reason: str) -> None:
        self.doc_id = doc_id
        self.reason = reason
        super().__init__(f"Ingestion failed for {doc_id}: {reason}")


class RetrievalError(Exception):
    """Raised when the retrieval engine encounters an error."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
