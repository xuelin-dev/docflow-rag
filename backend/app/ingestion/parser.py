"""Document parsing using Unstructured.io."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    MARKDOWN = "markdown"
    HTML = "html"
    TXT = "txt"


@dataclass
class DocumentElement:
    """A structural element within a parsed document."""
    element_type: str  # "paragraph", "table", "code_block", "heading"
    text: str
    metadata: dict = field(default_factory=dict)  # page_number, heading_level, etc.


@dataclass
class ParsedDocument:
    """Output of the document parser."""
    doc_id: str
    title: str
    doc_type: DocumentType
    elements: list[DocumentElement]
    metadata: dict = field(default_factory=dict)


class DocumentParser:
    """Parse documents into structured elements using Unstructured.io.

    Supports PDF, Markdown, HTML, and plain text formats.
    """

    MIME_MAP: dict[str, DocumentType] = {
        ".pdf": DocumentType.PDF,
        ".md": DocumentType.MARKDOWN,
        ".markdown": DocumentType.MARKDOWN,
        ".html": DocumentType.HTML,
        ".htm": DocumentType.HTML,
        ".txt": DocumentType.TXT,
    }

    def detect_type(self, file_path: Path) -> DocumentType:
        """Detect document type from file extension."""
        suffix = file_path.suffix.lower()
        if suffix not in self.MIME_MAP:
            raise ValueError(f"Unsupported file type: {suffix}")
        return self.MIME_MAP[suffix]

    async def parse(self, file_path: Path, doc_id: str, title: str | None = None) -> ParsedDocument:
        """Parse a document file into structured elements.

        Args:
            file_path: Path to the document file.
            doc_id: Unique document identifier.
            title: Optional document title (defaults to filename).

        Returns:
            ParsedDocument with extracted elements.
        """
        doc_type = self.detect_type(file_path)
        title = title or file_path.stem

        elements = await self._parse_by_type(file_path, doc_type)

        return ParsedDocument(
            doc_id=doc_id,
            title=title,
            doc_type=doc_type,
            elements=elements,
            metadata={"source_path": str(file_path)},
        )

    async def _parse_by_type(self, file_path: Path, doc_type: DocumentType) -> list[DocumentElement]:
        """Dispatch to the appropriate parser based on document type."""
        if doc_type == DocumentType.TXT:
            return await self._parse_txt(file_path)

        # Use Unstructured.io for structured formats
        try:
            from unstructured.partition.auto import partition
        except ImportError:
            raise ImportError("Install 'unstructured' package for PDF/HTML/MD parsing")

        raw_elements = partition(filename=str(file_path))

        return [
            DocumentElement(
                element_type=type(el).__name__.lower(),
                text=str(el),
                metadata=el.metadata.to_dict() if hasattr(el.metadata, "to_dict") else {},
            )
            for el in raw_elements
            if str(el).strip()
        ]

    async def _parse_txt(self, file_path: Path) -> list[DocumentElement]:
        """Parse a plain text file into paragraph elements."""
        text = file_path.read_text(encoding="utf-8")
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        return [
            DocumentElement(element_type="paragraph", text=p, metadata={"index": i})
            for i, p in enumerate(paragraphs)
        ]
