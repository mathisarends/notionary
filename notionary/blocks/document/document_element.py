import re
from typing import Dict, Any, Optional, List

from notionary.blocks import NotionBlockElement, NotionBlockResult
from notionary.blocks import ElementPromptContent, ElementPromptBuilder

class DocumentElement(NotionBlockElement):
    """
    Handles conversion between Markdown document embeds and Notion file blocks.

    Markdown document syntax:
    - [document](https://example.com/document.pdf "Caption")
    - [document](https://example.com/document.pdf)
    """
    # Nur noch die neue Syntax!
    PATTERN = re.compile(
        r'^\[document\]\('
        r'(https?://[^\s")]+)'           # URL
        r'(?:\s+"([^"]*)")?'             # Optional caption
        r'\)$'
    )

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        text = text.strip()
        return text.startswith("[document]") and bool(cls.PATTERN.match(text))

    @classmethod
    def match_notion(cls, block: Dict[str, Any]) -> bool:
        return block.get("type") == "file"

    @classmethod
    def markdown_to_notion(cls, text: str) -> Optional[List[Dict[str, Any]]]:
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None
        url = match.group(1)
        caption = match.group(2) or ""
        file_block = {
            "type": "file",
            "file": {
                "type": "external",
                "external": {"url": url},
                "caption": [{"type": "text", "text": {"content": caption}}] if caption else [],
            }
        }
        # Für Konsistenz mit anderen Blöcken geben wir ein Array zurück
        empty_paragraph = {"type": "paragraph", "paragraph": {"rich_text": []}}
        return [file_block, empty_paragraph]

    @classmethod
    def notion_to_markdown(cls, block: Dict[str, Any]) -> Optional[str]:
        if block.get("type") != "file":
            return None
        file_data = block.get("file", {})
        url = ""
        if file_data.get("type") == "external":
            url = file_data.get("external", {}).get("url", "")
        elif file_data.get("type") == "file":
            url = file_data.get("file", {}).get("url", "")
        if not url:
            return None
        caption_list = file_data.get("caption", [])
        caption = cls._extract_text_content(caption_list)
        if caption:
            return f'[document]({url} "{caption}")'
        return f'[document]({url})'

    @classmethod
    def _extract_text_content(cls, rich_text: List[Dict[str, Any]]) -> str:
        return "".join(
            t.get("text", {}).get("content", "")
            for t in rich_text
            if t.get("type") == "text"
        ) or "".join(t.get("plain_text", "") for t in rich_text if "plain_text" in t)

    @classmethod
    def is_multiline(cls) -> bool:
        return False

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        return (
            ElementPromptBuilder()
            .with_description(
                "Embeds document files from external sources like PDFs, Word docs, Excel files, or cloud storage services."
            )
            .with_usage_guidelines(
                "Use document embeds for sharing contracts, reports, manuals, or any important files."
            )
            .with_syntax('[document](https://example.com/document.pdf "Caption")')
            .with_examples(
                [
                    '[document](https://drive.google.com/file/d/1a2b3c4d5e/view "Project Proposal")',
                    '[document](https://company.sharepoint.com/reports/q4-2024.xlsx "Q4 Financial Report")',
                    '[document](https://cdn.company.com/docs/manual-v2.1.pdf "User Manual")',
                    '[document](https://docs.google.com/document/d/1x2y3z4/edit "Meeting Minutes")',
                    '[document](https://example.com/contract.pdf)',
                ]
            )
            .build()
        )
