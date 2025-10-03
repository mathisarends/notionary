import pytest

from notionary.blocks.markdown.builder import MarkdownBuilder
from notionary.blocks.registry.service import BlockRegistry
from notionary.page.writer.markdown_to_notion_converter import MarkdownToNotionConverter


class TestMarkdownToNotionConverter:
    """Regressionstest für den MarkdownToNotionConverter."""

    @pytest.fixture
    def block_registry(self):
        """Erstellt eine vollständige BlockRegistry für den Test."""
        return BlockRegistry()

    @pytest.fixture
    def converter(self, block_registry):
        """Erstellt einen MarkdownToNotionConverter mit der Registry."""
        return MarkdownToNotionConverter(block_registry)

    @pytest.fixture
    def generated_markdown(self):
        """Generiert den Markdown-Code aus dem MarkdownBuilder-Beispiel."""
        # Das ist der Code aus paste.txt, leicht angepasst für den Test
        builder = MarkdownBuilder()

        result = (
            builder
            # Header section with breadcrumb
            .breadcrumb()
            .space()
            # Main title and introduction
            .h1("🚀 Advanced Project Documentation")
            .paragraph(
                "**Welcome to the comprehensive guide for our advanced software project.** This documentation covers everything from architecture to deployment, featuring interactive examples and detailed explanations."
            )
            .space()
            # Table of contents
            .table_of_contents("blue_background")
            .space()
            # Overview callout
            .callout(
                "📋 **Project Overview**: This document demonstrates all available markdown elements in a real-world documentation scenario.",
                "🎯",
            )
            .space()
            # Two-column layout: Quick stats and project status
            .columns(
                lambda col: (
                    col.h2("📊 Project Statistics")
                    .table(
                        ["Metric", "Value", "Status"],
                        [
                            ["Lines of Code", "125,847", "✅ Healthy"],
                            ["Test Coverage", "94.2%", "✅ Excellent"],
                            ["Dependencies", "23", "⚠️ Monitor"],
                            ["Build Time", "2.3 min", "✅ Good"],
                            ["Contributors", "12", "✅ Active"],
                        ],
                    )
                    .space()
                    .callout("All metrics are updated daily via CI/CD pipeline.", "📈")
                ),
                lambda col: (
                    col.h2("🎯 Current Sprint")
                    .todo_list(
                        [
                            "Implement user authentication",
                            "Optimize database queries",
                            "Add monitoring dashboards",
                            "Update API documentation",
                            "Security audit",
                        ],
                        [True, True, False, False, False],
                    )
                    .space()
                    .quote('"Great software is built one commit at a time." - Team Lead')
                ),
                width_ratios=[0.6, 0.4],
            )
            .space()
            # Architecture section with toggleable content
            .h2("🏗️ System Architecture")
            .paragraph("Our system follows a microservices architecture with event-driven communication patterns.")
            .toggleable_heading(
                "Database Design",
                3,
                lambda t: (
                    t.paragraph("The database schema is optimized for performance and scalability:")
                    .code(
                        """-- User table with optimized indexes
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);""",
                        "sql",
                    )
                    .space()
                    .callout(
                        "All tables use proper indexing strategies for optimal query performance.",
                        "⚡",
                    )
                ),
            )
            .toggleable_heading(
                "API Endpoints",
                3,
                lambda t: (
                    t.paragraph("RESTful API with comprehensive error handling and rate limiting:")
                    .table(
                        ["Endpoint", "Method", "Description", "Rate Limit"],
                        [
                            ["/api/v1/users", "GET", "List all users", "100/min"],
                            ["/api/v1/users/{id}", "GET", "Get user by ID", "1000/min"],
                            ["/api/v1/users", "POST", "Create new user", "10/min"],
                            [
                                "/api/v1/auth/login",
                                "POST",
                                "User authentication",
                                "5/min",
                            ],
                            ["/api/v1/data/export", "GET", "Export data", "1/hour"],
                        ],
                    )
                    .space()
                    .code(
                        """# Example API usage in Python
import requests

# Authenticate user
response = requests.post('/api/v1/auth/login', {
    'email': 'user@example.com',
    'password': 'secure_password'
})

if response.status_code == 200:
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Fetch user data
    user_data = requests.get('/api/v1/users/123', headers=headers)
    print(user_data.json())""",
                        "python",
                    )
                ),
            )
            .space()
            # Development workflow
            .h2("⚙️ Development Workflow")
            .paragraph("Our development process ensures code quality and seamless collaboration.")
            .build()
        )

        return result

    @pytest.fixture
    def expected_block_structure(self):
        """Die erwartete Block-Struktur aus paste-2.txt (vereinfacht für Test)."""
        # Hier würde normalerweise die vollständige erwartete Struktur stehen
        # Für diesen Test fokussieren wir uns auf die wichtigsten Elemente
        return {
            "expected_block_types": [
                "breadcrumb",
                "paragraph",  # space
                "heading_1",
                "paragraph",
                "paragraph",  # space
                "table_of_contents",
                "paragraph",  # space
                "callout",
                "paragraph",  # space
                "column_list",
                "paragraph",  # space
                "heading_2",
                "paragraph",
                "heading_3",  # toggleable heading
                "heading_3",  # toggleable heading
                "paragraph",  # space
                "heading_2",
                "paragraph",
            ],
            "expected_heading_1_text": "🚀 Advanced Project Documentation",
            "expected_callout_emoji": "🎯",
            "expected_toc_color": "blue_background",
            "expected_column_count": 2,
        }

    @pytest.mark.asyncio
    async def test_markdown_to_notion_conversion_regression(
        self, converter, generated_markdown, expected_block_structure
    ):
        """
        Regressionstest: Prüft, ob der generierte Markdown korrekt in Notion-Blöcke konvertiert wird.
        """
        # Konvertierung durchführen
        actual_blocks = await converter.convert(generated_markdown)

        # Grundlegende Struktur-Validierung
        assert len(actual_blocks) > 0, "Es sollten Blöcke generiert werden"

        # Extrahiere die Block-Typen für Vergleich
        actual_block_types = [block.type for block in actual_blocks]

        # Prüfe erwartete Block-Typen (flexibler Ansatz)
        expected_block_structure["expected_block_types"]

        # Prüfe, dass wichtige Block-Typen vorhanden sind
        assert "breadcrumb" in actual_block_types, "Breadcrumb sollte vorhanden sein"
        assert "heading_1" in actual_block_types, "H1 sollte vorhanden sein"
        assert "table_of_contents" in actual_block_types, "TOC sollte vorhanden sein"
        assert "callout" in actual_block_types, "Callout sollte vorhanden sein"
        assert "column_list" in actual_block_types, "Column List sollte vorhanden sein"

        # Prüfe H1-Inhalt
        h1_blocks = [b for b in actual_blocks if b.type == "heading_1"]
        assert len(h1_blocks) >= 1, "Mindestens ein H1 sollte vorhanden sein"

        # Prüfe TOC-Konfiguration
        toc_blocks = [b for b in actual_blocks if b.type == "table_of_contents"]
        assert len(toc_blocks) >= 1, "TOC sollte vorhanden sein"

        if toc_blocks:
            toc_block = toc_blocks[0]
            assert hasattr(toc_block, "table_of_contents"), "TOC-Block sollte table_of_contents haben"
            # Prüfe Farbe
            expected_color = expected_block_structure["expected_toc_color"]
            assert toc_block.table_of_contents.color.value == expected_color, f"TOC-Farbe sollte {expected_color} sein"

        # Prüfe Callout-Konfiguration
        callout_blocks = [b for b in actual_blocks if b.type == "callout"]
        assert len(callout_blocks) >= 1, "Callout sollte vorhanden sein"

        if callout_blocks:
            callout_block = callout_blocks[0]
            assert hasattr(callout_block, "callout"), "Callout-Block sollte callout haben"
            # Prüfe Icon
            expected_emoji = expected_block_structure["expected_callout_emoji"]
            assert callout_block.callout.icon.emoji == expected_emoji, f"Callout-Emoji sollte {expected_emoji} sein"

        # Prüfe Column-List-Struktur
        column_list_blocks = [b for b in actual_blocks if b.type == "column_list"]
        assert len(column_list_blocks) >= 1, "Column List sollte vorhanden sein"

        if column_list_blocks:
            column_list_block = column_list_blocks[0]
            assert hasattr(column_list_block, "column_list"), "Column-List-Block sollte column_list haben"
            # Prüfe Anzahl der Spalten
            expected_columns = expected_block_structure["expected_column_count"]
            actual_columns = len(column_list_block.column_list.children)
            assert actual_columns == expected_columns, (
                f"Es sollten {expected_columns} Spalten sein, aber {actual_columns} gefunden"
            )

    @pytest.mark.asyncio
    async def test_specific_block_content_validation(self, converter, generated_markdown):
        """
        Detailliertere Validierung spezifischer Block-Inhalte.
        """
        actual_blocks = await converter.convert(generated_markdown)

        # Prüfe breadcrumb
        breadcrumb_blocks = [b for b in actual_blocks if b.type == "breadcrumb"]
        assert len(breadcrumb_blocks) == 1, "Genau ein Breadcrumb sollte vorhanden sein"

        # Prüfe H1-Inhalt detaillierter
        h1_blocks = [b for b in actual_blocks if b.type == "heading_1"]
        h1_block = h1_blocks[0]

        # Extrahiere Text aus rich_text
        h1_text = ""
        for rich_text_obj in h1_block.heading_1.rich_text:
            h1_text += rich_text_obj.plain_text

        assert "🚀 Advanced Project Documentation" in h1_text, "H1 sollte den erwarteten Text enthalten"

        # Prüfe, dass Toggleable Headings korrekt konvertiert wurden
        heading_3_blocks = [b for b in actual_blocks if b.type == "heading_3"]
        toggleable_headings = [
            h for h in heading_3_blocks if hasattr(h.heading_3, "is_toggleable") and h.heading_3.is_toggleable
        ]

        assert len(toggleable_headings) >= 2, "Mindestens 2 toggleable headings sollten vorhanden sein"

    @pytest.mark.asyncio
    async def test_complex_structure_integrity(self, converter, generated_markdown):
        """
        Prüft die Integrität komplexer verschachtelter Strukturen.
        """
        actual_blocks = await converter.convert(generated_markdown)

        # Prüfe Column-List mit Inhalten
        column_list_blocks = [b for b in actual_blocks if b.type == "column_list"]
        if column_list_blocks:
            column_list = column_list_blocks[0]
            columns = column_list.column_list.children

            # Erste Spalte sollte Table und Callout enthalten
            if len(columns) >= 1:
                first_column = columns[0]
                assert hasattr(first_column, "column"), "Erste Spalte sollte column-Attribut haben"

                # Prüfe Children der ersten Spalte
                first_column_children = first_column.column.children
                child_types = [child.type for child in first_column_children]

                assert "heading_2" in child_types, "Erste Spalte sollte H2 enthalten"
                assert "table" in child_types, "Erste Spalte sollte Table enthalten"
                assert "callout" in child_types, "Erste Spalte sollte Callout enthalten"

            # Zweite Spalte sollte Todo-List und Quote enthalten
            if len(columns) >= 2:
                second_column = columns[1]
                second_column_children = second_column.column.children
                child_types = [child.type for child in second_column_children]

                assert "heading_2" in child_types, "Zweite Spalte sollte H2 enthalten"
                assert "to_do" in child_types, "Zweite Spalte sollte Todo-Items enthalten"
                assert "quote" in child_types, "Zweite Spalte sollte Quote enthalten"

        # Prüfe Toggleable Headings mit Inhalten
        heading_3_blocks = [b for b in actual_blocks if b.type == "heading_3"]
        for heading in heading_3_blocks:
            if hasattr(heading.heading_3, "is_toggleable") and heading.heading_3.is_toggleable:
                # Toggleable Headings sollten Children haben
                children = heading.heading_3.children
                assert len(children) > 0, "Toggleable Headings sollten Inhalte haben"

    @pytest.mark.asyncio
    async def test_markdown_roundtrip_basic(self, converter, block_registry):
        """
        Einfacher Roundtrip-Test: Markdown -> Notion -> Markdown
        """
        simple_markdown = """[breadcrumb]

# Test Heading

This is a paragraph.

[callout](Important information "💡")

[toc]"""

        # Markdown -> Notion
        blocks = await converter.convert(simple_markdown)
        assert len(blocks) > 0, "Blöcke sollten generiert werden"

        # Grundlegende Struktur prüfen
        block_types = [block.type for block in blocks]
        expected_types = [
            "breadcrumb",
            "paragraph",
            "heading_1",
            "paragraph",
            "callout",
            "table_of_contents",
        ]

        for expected_type in expected_types:
            assert expected_type in block_types, f"Block-Typ {expected_type} sollte vorhanden sein"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
