import re
from typing import Dict, Any, Optional, List, Tuple, Callable

from notionary.elements.notion_block_element import NotionBlockElement
from notionary.elements.prompts.element_prompt_content import ElementPromptContent


class ToggleElement(NotionBlockElement):
    """
    Verbesserte ToggleElement-Klasse mit Pipe-Syntax statt Einrückung.
    """

    TOGGLE_PATTERN = re.compile(r"^[+]{3}\s+(.+)$")
    PIPE_CONTENT_PATTERN = re.compile(r"^\|\s?(.*)$")
    
    TRANSCRIPT_TOGGLE_PATTERN = re.compile(r"^[+]{3}\s+Transcript$")

    @staticmethod
    def match_markdown(text: str) -> bool:
        """Check if text is a markdown toggle."""
        return bool(ToggleElement.TOGGLE_PATTERN.match(text.strip()))

    @staticmethod
    def match_notion(block: Dict[str, Any]) -> bool:
        """Check if block is a Notion toggle."""
        return block.get("type") == "toggle"

    @staticmethod
    def markdown_to_notion(text: str) -> Optional[Dict[str, Any]]:
        """Convert markdown toggle to Notion toggle block."""
        toggle_match = ToggleElement.TOGGLE_PATTERN.match(text.strip())
        if not toggle_match:
            return None

        # Extract content
        title = toggle_match.group(1)

        return {
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": title}}],
                "color": "default",
                "children": [],
            },
        }

    @staticmethod
    def extract_nested_content(
        lines: List[str], start_index: int
    ) -> Tuple[List[str], int]:
        """
        Extrahiert den verschachtelten Inhalt eines Toggle-Elements mit Pipe-Syntax.
        Vereinfachte Version mit geringerer kognitiver Komplexität.

        Args:
            lines: Alle Textzeilen
            start_index: Startindex für die Suche nach verschachtelten Inhalten

        Returns:
            Tuple aus (verschachtelte_Inhaltszeilen, nächster_Zeilenindex)
        """
        nested_content = []
        current_index = start_index
        
        while current_index < len(lines):
            current_line = lines[current_index]
            
            # Fall 1: Leere Zeile - kann Teil des Inhalts sein, wenn die nächste Zeile eine Pipe hat
            if not current_line.strip():
                if ToggleElement.is_next_line_pipe_content(lines, current_index):
                    nested_content.append("")
                    current_index += 1
                    continue
                else:
                    # Leere Zeile ohne nachfolgende Pipe beendet den Inhalt
                    break
                    
            # Fall 2: Zeile mit Pipe-Präfix - Teil des Inhalts
            pipe_content = ToggleElement.extract_pipe_content(current_line)
            if pipe_content is not None:
                nested_content.append(pipe_content)
                current_index += 1
                continue
                
            # Fall 3: Normale Zeile ohne Pipe - Ende des verschachtelten Inhalts
            break
            
        return nested_content, current_index

    @staticmethod
    def is_next_line_pipe_content(lines: List[str], current_index: int) -> bool:
        """Prüft, ob die nächste Zeile mit einem Pipe-Präfix beginnt."""
        next_index = current_index + 1
        return (next_index < len(lines) and 
                ToggleElement.PIPE_CONTENT_PATTERN.match(lines[next_index]) is not None)

    @staticmethod
    def extract_pipe_content(line: str) -> Optional[str]:
        """
        Extrahiert den Inhalt einer Zeile mit Pipe-Präfix.
        
        Returns:
            Den Inhalt ohne Pipe oder None, wenn keine Pipe-Syntax gefunden wurde
        """
        pipe_match = ToggleElement.PIPE_CONTENT_PATTERN.match(line)
        if pipe_match:
            return pipe_match.group(1)
        return None


    @staticmethod
    def notion_to_markdown(block: Dict[str, Any]) -> Optional[str]:
        """
        Konvertiert einen Notion-Toggle-Block in Markdown mit Pipe-Syntax.
        Optimiert mit Python-Konventionen für ungenutzte Variablen.
        """
        if block.get("type") != "toggle":
            return None

        toggle_data = block.get("toggle", {})

        # Titel aus rich_text extrahieren
        title = ToggleElement._extract_text_content(toggle_data.get("rich_text", []))

        # Toggle-Zeile erstellen
        toggle_line = f"+++ {title}"

        # Kinder verarbeiten, falls vorhanden
        children = toggle_data.get("children", [])
        if not children:
            return toggle_line
            
        # Für jedes Kind eine Zeile mit Pipe-Syntax hinzufügen
        # Wir verwenden _ für die ungenutzte Variable
        child_lines = ["| [Nested content]" for _ in children]
        
        return toggle_line + "\n" + "\n".join(child_lines)

    @staticmethod
    def is_multiline() -> bool:
        """Toggle blocks can span multiple lines due to their nested content."""
        return True

    @staticmethod
    def _extract_text_content(rich_text: List[Dict[str, Any]]) -> str:
        """Extract plain text content from Notion rich_text elements."""
        result = ""
        for text_obj in rich_text:
            if text_obj.get("type") == "text":
                result += text_obj.get("text", {}).get("content", "")
            elif "plain_text" in text_obj:
                result += text_obj.get("plain_text", "")
        return result


    @classmethod
    def find_matches(
        cls,
        text: str,
        process_nested_content: Callable = None,
        context_aware: bool = True,
    ) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Verbesserte find_matches-Methode mit Pipe-Syntax für verschachtelte Inhalte.
        Mit reduzierter kognitiver Komplexität durch bessere Strukturierung.

        Args:
            text: Der zu durchsuchende Text
            process_nested_content: Optionale Callback-Funktion zur Verarbeitung verschachtelter Inhalte
            context_aware: Ob der Kontext (vorhergehende Zeilen) beim Finden von Toggles berücksichtigt werden soll

        Returns:
            Liste von (start_pos, end_pos, block) Tupeln
        """
        if not text:
            return []

        toggle_blocks = []
        lines = text.split("\n")
        current_line_index = 0
        
        while current_line_index < len(lines):
            current_line = lines[current_line_index]
            
            # Überprüfen, ob die aktuelle Zeile ein Toggle ist
            if not cls._is_toggle_line(current_line):
                current_line_index += 1
                continue
                
            # Transcript-Toggle-Kontextverarbeitung
            if cls._should_skip_transcript_toggle(current_line, lines, current_line_index, context_aware):
                current_line_index += 1
                continue
                
            # Toggle-Block erstellen und Position berechnen
            start_position = cls._calculate_start_position(lines, current_line_index)
            toggle_block = cls.markdown_to_notion(current_line)
            
            if not toggle_block:
                current_line_index += 1
                continue
                
            # Verschachtelte Inhalte extrahieren und verarbeiten
            nested_content, next_line_index = cls.extract_nested_content(lines, current_line_index + 1)
            end_position = cls._calculate_end_position(start_position, current_line, nested_content)
            
            # Verschachtelte Inhalte verarbeiten, wenn vorhanden
            cls._process_nested_content_if_needed(nested_content, process_nested_content, toggle_block)
            
            # Toggle-Block mit Positionsinformationen speichern
            toggle_blocks.append((start_position, end_position, toggle_block))
            current_line_index = next_line_index
            
        return toggle_blocks
        
    @staticmethod
    def _is_toggle_line(line: str) -> bool:
        """Prüft, ob eine Zeile ein Toggle-Element ist."""
        return bool(ToggleElement.TOGGLE_PATTERN.match(line.strip()))
        
    @classmethod
    def _should_skip_transcript_toggle(cls, line: str, lines: List[str], current_index: int, context_aware: bool) -> bool:
        """Entscheidet, ob ein Transcript-Toggle übersprungen werden soll basierend auf dem Kontext."""
        is_transcript_toggle = cls.TRANSCRIPT_TOGGLE_PATTERN.match(line.strip())
        
        if not (context_aware and is_transcript_toggle):
            return False
            
        # Nur Transcript-Toggles behalten, die nach einer Listen-Zeile kommen
        has_list_item_before = current_index > 0 and lines[current_index - 1].strip().startswith("- ")
        return not has_list_item_before
        
    @staticmethod
    def _calculate_start_position(lines: List[str], current_index: int) -> int:
        """Berechnet die Startposition in Zeichen für den aktuellen Zeilenindex."""
        start_pos = 0
        for index in range(current_index):
            start_pos += len(lines[index]) + 1  # +1 für Zeilenumbruch
        return start_pos
        
    @staticmethod
    def _calculate_end_position(start_pos: int, current_line: str, nested_content: List[str]) -> int:
        """Berechnet die Endposition eines Toggle-Blocks inkl. verschachtelter Inhalte."""
        line_length = len(current_line)
        nested_content_length = sum(len(line) + 1 for line in nested_content)  # +1 für jeden Zeilenumbruch
        return start_pos + line_length + nested_content_length
        
    @staticmethod
    def _process_nested_content_if_needed(
        nested_content: List[str], 
        process_function: Optional[Callable], 
        toggle_block: Dict[str, Any]
    ) -> None:
        """Verarbeitet verschachtelte Inhalte mit der gegebenen Funktion, wenn vorhanden."""
        if not (nested_content and process_function):
            return
            
        nested_text = "\n".join(nested_content)
        nested_blocks = process_function(nested_text)
        
        if nested_blocks:
            toggle_block["toggle"]["children"] = nested_blocks

    @classmethod
    def get_llm_prompt_content(cls) -> ElementPromptContent:
        """
        Returns structured LLM prompt metadata for the toggle element with pipe syntax examples.
        """
        return {
            "description": "Toggle elements are collapsible sections that help organize and hide detailed information.",
            "when_to_use": (
                "Use toggles for supplementary information that's not essential for the first reading, "
                "such as details, examples, or technical information."
            ),
            "syntax": "+++ Toggle Title\n| Toggle content with pipe prefix",
            "examples": [
                "+++ Key Findings\n| The research demonstrates **three main conclusions**:\n| 1. First important point\n| 2. Second important point",
                "+++ FAQ\n| **Q: When should I use toggles?**\n| *A: Use toggles for supplementary information.*",
            ],
        }