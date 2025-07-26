import re
from typing import Dict, Any, Optional, List

from notionary.blocks import NotionBlockElement
from notionary.blocks import ElementPromptContent, ElementPromptBuilder


class DocumentElement(NotionBlockElement):
    """
    Handles conversion between Markdown document embeds and Notion file blocks.

    Markdown document syntax (custom format):
    - %[Caption](https://example.com/document.pdf) - Basic document with caption
    - %[](https://example.com/document.pdf) - Document without caption
    - %[Meeting Notes](https://drive.google.com/file/d/123/view) - Google Drive document
    - %[Report](https://company.sharepoint.com/document.docx) - SharePoint document

    Supports various document URLs including PDFs, Word docs, Excel files, PowerPoint,
    Google Drive files, and other document formats that Notion can display.
    """

    PATTERN = re.compile(
        r"^%\[(.*?)\]"  # %[Caption] part
        + r'\((https?://[^\s"]+)'  # (URL part
        + r"\)$"  # closing parenthesis
    )

    DOCUMENT_EXTENSIONS = [
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".txt",
        ".rtf",
        ".odt",
        ".ods",
        ".odp",
        ".pages",
        ".numbers",
        ".key",
        ".epub",
        ".mobi",
    ]

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        """Check if text is a markdown document embed."""
        text = text.strip()
        return text.startswith("%[") and bool(cls.PATTERN.match(text))

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        """Check if block is a Notion file (document)."""
        return block.get("type") == "file"

    @classmethod
    def is_document_url(cls, url: str) -> bool:
        """Check if URL points to a document file."""
        url_lower = url.lower()

        # Check for common document file extensions
        if any(url_lower.endswith(ext) for ext in cls.DOCUMENT_EXTENSIONS):
            return True

        # Check for common document hosting services
        document_services = [
            "drive.google.com",
            "docs.google.com",
            "sheets.google.com",
            "slides.google.com",
            "sharepoint.com",
            "onedrive.com",
            "dropbox.com",
            "box.com",
            "scribd.com",
            "slideshare.net",
        ]

        return any(service in url_lower for service in document_services)

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown document embed to Notion file block."""
        doc_match = cls.PATTERN.match(text.strip())
        if not doc_match:
            return None

        caption = doc_match.group(1)
        url = doc_match.group(2)

        if not url:
            return None

        # Verify this looks like a document URL
        if not cls.is_document_url(url):
            # Still proceed - user might know better than our detection
            pass

        # Prepare the file block
        file_block = {
            "type": "file",
            "file": {"type": "external", "external": {"url": url}},
        }

        # Add caption if provided
        if caption:
            file_block["file"]["caption"] = [
                {"type": "text", "text": {"content": caption}}
            ]

        return file_block

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        """Convert Notion file block to markdown document embed."""
        if block.get("type") != "file":
            return None

        file_data = block.get("file", {})

        # Handle both external and file (uploaded) documents
        if file_data.get("type") == "external":
            url = file_data.get("external", {}).get("url", "")
        elif file_data.get("type") == "file":
            url = file_data.get("file", {}).get("url", "")
        elif file_data.get("type") == "file_upload":
            # Handle file uploads with special notion:// syntax
            file_upload_id = file_data.get("file_upload", {}).get("id", "")
            if file_upload_id:
                url = f"notion://file_upload/{file_upload_id}"
            else:
                return None
        else:
            return None

        if not url:
            return None

        # Extract caption if available
        caption = ""
        caption_rich_text = file_data.get("caption", [])
        if caption_rich_text:
            caption = cls._extract_text_content(caption_rich_text)

        return f"%[{caption}]({url})"

    @classmethod
    def is_multiline(cls) -> bool:
        """Document embeds are single-line elements."""
        return False

    @classmethod
    def _extract_text_content(cls, rich_text: List[Dict[str, Any]]) -> str:
        """Extract plain text content from Notion rich_text elements."""
        result = ""
        for text_obj in rich_text:
            if text_obj.get("type") == "text":
                result += text_obj.get("text", {}).get("content", "")
            elif "plain_text" in text_obj:
                result += text_obj.get("plain_text", "")
        return result

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """Returns information for LLM prompts about this element."""
        return (
            ElementPromptBuilder()
            .with_description(
                "Embeds document files from external sources like PDFs, Word docs, Excel files, or cloud storage services."
            )
            .with_usage_guidelines(
                "Use document embeds when you want to include reference materials, reports, presentations, or any "
                "file-based content directly in your document. Documents can be viewed inline or downloaded by users. "
                "Perfect for sharing contracts, reports, manuals, or any important files."
            )
            .with_syntax("%[Caption](https://example.com/document.pdf)")
            .with_examples(
                [
                    "%[Project Proposal](https://drive.google.com/file/d/1a2b3c4d5e/view)",
                    "%[Q4 Financial Report](https://company.sharepoint.com/reports/q4-2024.xlsx)",
                    "%[User Manual](https://cdn.company.com/docs/manual-v2.1.pdf)",
                    "%[Meeting Minutes](https://docs.google.com/document/d/1x2y3z4/edit)",
                    "%[](https://example.com/contract.pdf)",
                ]
            )
            .with_avoidance_guidelines(
                "Only use for actual document files. For web pages or articles, use bookmark or embed elements instead. "
                "Ensure document URLs are accessible to your intended audience."
            )
            .build()
        )
