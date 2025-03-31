from typing import List, Dict, Any
from notionary.core.notion_markdown_parser import NotionMarkdownParser

class NotionContentConverter:
    """Klasse zum Konvertieren zwischen Notion-Blöcken und Textformaten."""
    
    @staticmethod
    def markdown_to_blocks(text: str) -> List[Dict[str, Any]]:
        """Konvertiert Markdown-Text in Notion-API-Blockformat.
        
        Args:
            text: Markdown-Text, der konvertiert werden soll
            
        Returns:
            Liste von Notion-Block-Objekten
        """
        return NotionMarkdownParser.parse_markdown(text)
    
    @staticmethod
    def blocks_to_text(blocks: List[Dict[str, Any]]) -> str:
        """Konvertiert Notion-Blöcke in lesbaren Text.
        
        Args:
            blocks: Liste von Notion-Block-Objekten
            
        Returns:
            Textdarstellung der Blöcke
        """
        if not blocks:
            return "Keine Inhalte gefunden."
        
        text_parts = []
        
        for block in blocks:
            block_type = block.get("type", "")
            
            if block_type == "paragraph":
                paragraph_text = NotionContentConverter._extract_text_from_rich_text(
                    block.get("paragraph", {}).get("rich_text", [])
                )
                if paragraph_text:
                    text_parts.append(paragraph_text)
            
            elif block_type == "heading_1":
                heading_text = NotionContentConverter._extract_text_from_rich_text(
                    block.get("heading_1", {}).get("rich_text", [])
                )
                if heading_text:
                    text_parts.append(f"# {heading_text}")
            
            elif block_type == "heading_2":
                heading_text = NotionContentConverter._extract_text_from_rich_text(
                    block.get("heading_2", {}).get("rich_text", [])
                )
                if heading_text:
                    text_parts.append(f"## {heading_text}")
            
            elif block_type == "heading_3":
                heading_text = NotionContentConverter._extract_text_from_rich_text(
                    block.get("heading_3", {}).get("rich_text", [])
                )
                if heading_text:
                    text_parts.append(f"### {heading_text}")
            
            elif block_type == "bulleted_list_item":
                item_text = NotionContentConverter._extract_text_from_rich_text(
                    block.get("bulleted_list_item", {}).get("rich_text", [])
                )
                if item_text:
                    text_parts.append(f"• {item_text}")
            
            elif block_type == "numbered_list_item":
                item_text = NotionContentConverter._extract_text_from_rich_text(
                    block.get("numbered_list_item", {}).get("rich_text", [])
                )
                if item_text:
                    # Wir kennen die tatsächliche Nummer nicht, daher verwenden wir "1."
                    text_parts.append(f"1. {item_text}")
            
            elif block_type == "divider":
                text_parts.append("---")
            
            elif block_type == "code":
                code_text = NotionContentConverter._extract_text_from_rich_text(
                    block.get("code", {}).get("rich_text", [])
                )
                language = block.get("code", {}).get("language", "")
                if code_text:
                    text_parts.append(f"```{language}\n{code_text}\n```")
            
            # Weitere Blocktypen nach Bedarf hinzufügen
        
        return "\n\n".join(text_parts)
    
    @staticmethod
    def _extract_text_from_rich_text(rich_text: List[Dict[str, Any]]) -> str:
        """Extrahiert reinen Text aus dem rich_text-Format von Notion.
        
        Args:
            rich_text: Liste von Rich-Text-Objekten aus der Notion-API
            
        Returns:
            Reine Textdarstellung
        """
        return "".join([text.get("plain_text", "") for text in rich_text])



