from typing import Dict, Any, List, Optional

from notionary.elements.block_element_registry import (
    BlockElementRegistry,
)
from notionary.elements.block_element_registry_builder import (
    BlockElementRegistryBuilder,
)


class NotionToMarkdownConverter:
    """Converts Notion blocks to Markdown text with support for nested structures."""

    def __init__(self, block_registry: Optional[BlockElementRegistry] = None):
        """
        Initialize the NotionToMarkdownConverter.

        Args:
            block_registry: Optional registry of Notion block elements
        """
        self._block_registry = (
            block_registry or BlockElementRegistryBuilder().create_standard_registry()
        )

    def convert(self, blocks: List[Dict[str, Any]]) -> str:
        """
        Convert Notion blocks to Markdown text, handling nested structures.

        Args:
            blocks: List of Notion blocks

        Returns:
            Markdown text
        """
        if not blocks:
            return ""

        markdown_parts = []

        for block in blocks:
            # Verarbeite den aktuellen Block
            block_markdown = self._process_block(block)
            if block_markdown:
                markdown_parts.append(block_markdown)

        return "\n\n".join(filter(None, markdown_parts))

    def _process_block(self, block: Dict[str, Any]) -> str:
        """
        Process a single block, including any children.

        Args:
            block: Notion block to process

        Returns:
            Markdown representation of the block and its children
        """
        if not block:
            return ""

        # Hauptinhalt des Blocks konvertieren
        block_markdown = self._block_registry.notion_to_markdown(block)
        
        # Wenn der Block keine Kinder hat, einfach den Block-Markdown zurückgeben
        if not block.get("has_children", False) or "children" not in block:
            return block_markdown
            
        # Wenn der Block Kinder hat, diese verarbeiten
        children_markdown = self.convert(block["children"])
        
        # Besondere Behandlung für verschiedene Block-Typen
        block_type = block.get("type", "")
        
        if block_type == "toggle":
            # Für Toggles: Kind-Inhalt einrücken und unter dem Toggle anzeigen
            if children_markdown:
                indented_children = "\n".join([f"    {line}" for line in children_markdown.split("\n")])
                return f"{block_markdown}\n{indented_children}"
        elif block_type in ["numbered_list_item", "bulleted_list_item"]:
            # Für Listen: Kind-Inhalt einrücken und direkt unter dem Listenelement anzeigen
            if children_markdown:
                indented_children = "\n".join([f"    {line}" for line in children_markdown.split("\n")])
                return f"{block_markdown}\n{indented_children}"
        elif block_type == "column_list":
            # Spalten einfach zusammenfügen
            return children_markdown
        elif block_type == "column":
            # Spalteninhalt ohne spezielle Formatierung
            return children_markdown
        else:
            # Standardverhalten für andere Block-Typen: Kind-Markdown nach dem Block
            if children_markdown:
                return f"{block_markdown}\n\n{children_markdown}"
                
        return block_markdown

    def extract_toggle_content(self, blocks: List[Dict[str, Any]]) -> str:
        """
        Speziell für Toggles: Extrahiere nur den Inhalt der Toggles.
        
        Args:
            blocks: Liste von Notion-Blöcken
            
        Returns:
            Markdown-Text mit dem Inhalt der Toggles
        """
        if not blocks:
            return ""
            
        toggle_contents = []
        
        def process_toggle_block(block):
            if block.get("type") == "toggle" and "children" in block:
                # Toggle-Titel extrahieren
                toggle_text = ""
                rich_text = block.get("toggle", {}).get("rich_text", [])
                if rich_text:
                    toggle_text = "".join([rt.get("plain_text", "") for rt in rich_text])
                
                # Toggle-Inhalt extrahieren
                children_content = []
                for child in block.get("children", []):
                    child_type = child.get("type")
                    if child_type and child_type in child:
                        rich_text = child.get(child_type, {}).get("rich_text", [])
                        if rich_text:
                            child_text = "".join([rt.get("plain_text", "") for rt in rich_text])
                            children_content.append(f"- {child_text}")
                
                # Toggle mit Inhalt zum Ergebnis hinzufügen
                if toggle_text:
                    toggle_contents.append(f"### {toggle_text}")
                if children_content:
                    toggle_contents.extend(children_content)
            
            # Rekursiv durch alle Kinder gehen
            if block.get("has_children", False) and "children" in block:
                for child in block["children"]:
                    process_toggle_block(child)
        
        # Starte die Verarbeitung mit allen Top-Level-Blöcken
        for block in blocks:
            process_toggle_block(block)
            
        return "\n".join(toggle_contents)