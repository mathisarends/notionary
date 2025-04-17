import unittest
from unittest.mock import patch

from notionary.elements.callout_element import CalloutElement


class TestCalloutElement(unittest.TestCase):
    """Einfacher Test für die CalloutElement-Klasse mit direkten Strings als Eingabe und Ausgabe."""

    def setUp(self):
        # Optional: Mock für extract_text_with_formatting, falls es ein Problem gibt
        self.extract_text_patcher = patch(
            "notionary.converters.elements.text_formatting.extract_text_with_formatting"
        )
        self.mock_extract_text = self.extract_text_patcher.start()

        # Standardverhalten des Mocks festlegen
        def mock_extract_text(rich_text):
            if not rich_text or len(rich_text) == 0:
                return ""
            for item in rich_text:
                if item.get("type") == "text" and item.get("text", {}).get("content"):
                    return item["text"]["content"]
            return ""

        self.mock_extract_text.side_effect = mock_extract_text

    def tearDown(self):
        self.extract_text_patcher.stop()

    def test_match_markdown(self):
        """Test zur Erkennung von Markdown-Callouts."""
        # Gültige Formate
        self.assertTrue(CalloutElement.match_markdown("!> Ein einfacher Callout"))
        self.assertTrue(CalloutElement.match_markdown("!> [💡] Ein Callout mit Emoji"))
        self.assertTrue(
            CalloutElement.match_markdown(
                "!> {blue_background} [🔥] Ein Callout mit Farbe und Emoji"
            )
        )

        # Ungültige Formate
        self.assertFalse(CalloutElement.match_markdown("Normaler Text"))
        self.assertFalse(CalloutElement.match_markdown("> Blockquote"))
        self.assertFalse(CalloutElement.match_markdown("!>"))  # Leerer Callout

    def test_markdown_to_notion_and_back(self):
        """Test der Konvertierung von Markdown zu Notion und zurück."""
        test_cases = [
            # Einfacher Callout
            "!> Einfacher Callout",
            # Callout mit Emoji
            "!> [🔥] Callout mit Emoji",
            # Callout mit Farbe
            "!> {blue_background} Callout mit Farbe",
            # Callout mit Farbe und Emoji
            "!> {red_background} [⚠️] Callout mit Farbe und Emoji",
        ]

        for markdown in test_cases:
            # Konvertiere Markdown zu Notion
            notion_block = CalloutElement.markdown_to_notion(markdown)
            self.assertIsNotNone(
                notion_block, f"Konnte {markdown} nicht zu Notion konvertieren"
            )

            # Konvertiere Notion zurück zu Markdown
            markdown_result = CalloutElement.notion_to_markdown(notion_block)
            self.assertIsNotNone(
                markdown_result,
                f"Konnte Notion-Block nicht zurück zu Markdown konvertieren",
            )

            # Logging für Debugging
            print(f"Original: {markdown}")
            print(f"Ergebnis: {markdown_result}")

            # Prüft grundlegende Übereinstimmung
            self.assertIn(
                "!>",
                markdown_result,
                "Markdown-Ergebnis enthält nicht das Callout-Präfix",
            )

            # Prüfe, dass der eigentliche Text-Inhalt erhalten bleibt
            # Wir extrahieren nur den tatsächlichen Textinhalt ohne Emoji/Farbe
            original_text = self._extract_text_only(markdown)
            result_text = self._extract_text_only(markdown_result)
            self.assertEqual(
                original_text,
                result_text,
                f"Textinhalt hat sich verändert. Original: '{original_text}', Ergebnis: '{result_text}'",
            )

    def test_specific_transformations(self):
        """Test spezifischer Transformationen mit erwarteten Ausgaben."""
        # Definiere Testfälle mit erwarteter Ausgabe
        test_cases = [
            {
                "input": "!> Einfacher Callout",
                "expected_notion": {
                    "type": "callout",
                    "callout": {
                        "icon": {"type": "emoji", "emoji": "💡"},
                        "color": "gray_background",
                    },
                },
            },
            {
                "input": "!> [🔥] Callout mit Emoji",
                "expected_notion": {
                    "type": "callout",
                    "callout": {
                        "icon": {"type": "emoji", "emoji": "🔥"},
                        "color": "gray_background",
                    },
                },
            },
            {
                "input": "!> {blue_background} Callout mit Farbe",
                "expected_notion": {
                    "type": "callout",
                    "callout": {
                        "icon": {"type": "emoji", "emoji": "💡"},
                        "color": "blue_background",
                    },
                },
            },
        ]

        for case in test_cases:
            # Konvertiere Markdown zu Notion
            notion_result = CalloutElement.markdown_to_notion(case["input"])

            # Prüfe grundlegende Eigenschaften
            for key, expected_value in case["expected_notion"]["callout"].items():
                if key != "rich_text":  # rich_text wird separat verarbeitet
                    self.assertEqual(
                        notion_result["callout"][key],
                        expected_value,
                        f"Für '{case['input']}': {key} nicht wie erwartet",
                    )

    def test_notion_to_markdown_examples(self):
        """Test der Konvertierung von Notion-Callout-Blöcken zu Markdown mit konkreten Beispielen."""
        # Mock für die extract_text_with_formatting konfigurieren
        # Dies garantiert, dass die Funktion den korrekten Inhalt zurückgibt

        test_cases = [
            {
                "input": {
                    "type": "callout",
                    "callout": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "Einfacher Callout"}}
                        ],
                        "icon": {"type": "emoji", "emoji": "💡"},
                        "color": "gray_background",
                    },
                },
                "expected_content": "Einfacher Callout",
                "expected_emoji": "💡",
                "expected_color": None,  # Default-Farbe wird nicht im Markdown angezeigt
            },
            {
                "input": {
                    "type": "callout",
                    "callout": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "Callout mit Farbe"}}
                        ],
                        "icon": {"type": "emoji", "emoji": "💡"},
                        "color": "blue_background",
                    },
                },
                "expected_content": "Callout mit Farbe",
                "expected_emoji": "💡",
                "expected_color": "blue_background",
            },
            {
                "input": {
                    "type": "callout",
                    "callout": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "Callout mit Emoji"}}
                        ],
                        "icon": {"type": "emoji", "emoji": "🔥"},
                        "color": "gray_background",
                    },
                },
                "expected_content": "Callout mit Emoji",
                "expected_emoji": "🔥",
                "expected_color": None,  # Default-Farbe wird nicht im Markdown angezeigt
            },
        ]

        for i, case in enumerate(test_cases):
            # Explizit den Rückgabewert des Mocks für diesen Fall setzen
            expected_content = case["expected_content"]
            self.mock_extract_text.return_value = expected_content

            result = CalloutElement.notion_to_markdown(case["input"])
            print(f"Testfall {i+1}:")
            print(f"Input: {case['input']}")
            print(f"Extract Text Mock gibt zurück: {expected_content}")
            print(f"Actual: {result}")
            print()

            # Überprüfen, dass ein Ergebnis zurückgegeben wurde
            self.assertIsNotNone(
                result, f"notion_to_markdown gab None für Testfall {i+1} zurück"
            )

            # Überprüfen grundlegender Anforderungen
            self.assertIn(
                "!>",
                result,
                f"Ergebnis enthält nicht das Callout-Präfix für Testfall {i+1}",
            )

            # Überprüfen des Emojis
            expected_emoji = case["expected_emoji"]
            if expected_emoji:
                self.assertIn(
                    expected_emoji,
                    result,
                    f"Emoji {expected_emoji} fehlt im Ergebnis für Testfall {i+1}",
                )

            # Überprüfen der Farbe
            expected_color = case["expected_color"]
            if expected_color:
                self.assertIn(
                    expected_color,
                    result,
                    f"Farbe {expected_color} fehlt im Ergebnis für Testfall {i+1}",
                )

            # Überprüfen des Inhalts
            self.assertIn(
                expected_content,
                result,
                f"Inhalt '{expected_content}' fehlt im Ergebnis für Testfall {i+1}",
            )

    def _extract_text_only(self, markdown):
        """Extrahiert nur den reinen Textinhalt aus einem Markdown-Callout."""
        # Entferne Callout-Präfix
        text = markdown.replace("!>", "").strip()

        # Entferne Emoji-Teil, wenn vorhanden
        if "]" in text and "[" in text:
            emoji_start = text.find("[")
            emoji_end = text.find("]") + 1
            text = text[:emoji_start] + text[emoji_end:].strip()

        # Entferne Farb-Teil, wenn vorhanden
        if "}" in text and "{" in text:
            color_start = text.find("{")
            color_end = text.find("}") + 1
            text = text[:color_start] + text[color_end:].strip()

        return text.strip()


if __name__ == "__main__":
    unittest.main()
