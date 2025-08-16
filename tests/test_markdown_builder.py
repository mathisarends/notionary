"""
Tests für komplexe verschachtelte MarkdownBuilder Szenarien.
Testet realistische Anwendungsfälle mit mehrstufiger Verschachtelung.
FIXED for new caption syntax!
"""

from notionary.markdown.markdown_builder import MarkdownBuilder


def test_nested_columns_with_mixed_content():
    """Test verschachtelte Spalten mit verschiedenen Content-Typen"""
    builder = MarkdownBuilder()

    result = (
        builder.h1("Complex Documentation")
        .paragraph("Introduction text")
        .columns(
            # Linke Spalte: Tabelle + Liste
            lambda col: (
                col.h2("API Overview")
                .table(
                    headers=["Endpoint", "Method", "Status"],
                    rows=[["/users", "GET", "Active"], ["/auth", "POST", "Beta"]],
                )
                .bulleted_list(
                    ["Authentication required", "Rate limited", "JSON responses"]
                )
            ),
            # Rechte Spalte: Code + Callout
            lambda col: (
                col.h2("Implementation")
                .code("def get_users():\n    return api.request('/users')", "python")
                .callout("Important: Always handle exceptions!", "⚠️")
            ),
            width_ratios=[0.6, 0.4],
        )
        .build()
    )

    # Grundlegende Struktur prüfen
    assert "# Complex Documentation" in result
    assert "Introduction text" in result
    assert "## API Overview" in result
    assert "## Implementation" in result
    assert "| Endpoint | Method | Status |" in result
    assert "```python" in result
    assert "def get_users():" in result
    assert '[callout](Important: Always handle exceptions! "⚠️")' in result
    assert "- Authentication required" in result

    # Column-spezifische Struktur prüfen
    assert "::: column" in result
    assert ":::" in result


def test_deeply_nested_toggles():
    """Test tief verschachtelte Toggle-Strukturen"""
    builder = MarkdownBuilder()

    result = (
        builder.h1("Nested Configuration")
        .toggle(
            "Database Settings",
            lambda t: (
                t.h2("Connection Configuration")
                .paragraph("Main database settings")
                .toggle(
                    "Advanced Options",
                    lambda inner: (
                        inner.h3("Performance Tuning")
                        .table(
                            headers=["Parameter", "Value", "Description"],
                            rows=[
                                [
                                    "max_connections",
                                    "100",
                                    "Maximum concurrent connections",
                                ],
                                ["timeout", "30s", "Connection timeout"],
                            ],
                        )
                        .callout("Restart required after changes", "🔄")
                    ),
                )
                .paragraph("End of database configuration")
            ),
        )
        .build()
    )

    # FIXED: Toggle-Titel bekommen automatisch Quotes
    assert '+++ "Database Settings"' in result
    assert "## Connection Configuration" in result
    assert "Main database settings" in result

    # FIXED: Innerer Toggle auch mit Quotes
    assert '+++ "Advanced Options"' in result
    assert "### Performance Tuning" in result
    assert "| Parameter | Value | Description |" in result
    assert "| max_connections | 100 | Maximum concurrent connections |" in result
    assert '[callout](Restart required after changes "🔄")' in result
    assert "End of database configuration" in result


def test_complex_documentation_structure():
    """Test einer komplexen Dokumentationsstruktur - FIXED for new caption syntax"""
    builder = MarkdownBuilder()

    result = (
        builder.h1("API Documentation & Implementation Guide")
        .paragraph(
            "Diese Dokumentation zeigt sowohl die API-Endpunkte als auch deren Implementierung."
        )
        .divider()
        .columns(
            # Linke Spalte: Tabelle mit API-Endpunkten
            lambda col: (
                col.h2("📋 API Endpunkte")
                .paragraph("Übersicht aller verfügbaren REST-API Endpunkte:")
                .table(
                    headers=["Endpunkt", "Methode", "Beschreibung", "Status"],
                    rows=[
                        ["/api/users", "GET", "Alle Benutzer abrufen", "✅ Aktiv"],
                        [
                            "/api/users/{id}",
                            "GET",
                            "Einzelnen Benutzer abrufen",
                            "✅ Aktiv",
                        ],
                        ["/api/users", "POST", "Neuen Benutzer erstellen", "✅ Aktiv"],
                        [
                            "/api/users/{id}",
                            "DELETE",
                            "Benutzer löschen",
                            "⚠️ Deprecated",
                        ],
                    ],
                )
                .callout(
                    "💡 Alle Endpunkte erfordern eine gültige API-Authentifizierung",
                    "🔐",
                )
            ),
            # Rechte Spalte: Code-Implementierung
            lambda col: (
                col.h2("⚙️ Implementierung")
                .paragraph("Python-Client Beispiel für die API-Nutzung:")
                .code(
                    """import requests
import json

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def get_users(self):
        response = self.session.get(f'{self.base_url}/api/users')
        response.raise_for_status()
        return response.json()""",
                    "python",
                    "Python API Client Implementation",
                )
                .paragraph("**Wichtige Hinweise:**")
                .bulleted_list(
                    [
                        "API-Key über Umgebungsvariablen laden",
                        "Retry-Mechanismus für fehlerhafte Requests",
                        "Rate-Limiting beachten (100 Requests/Min)",
                    ]
                )
            ),
            width_ratios=[0.6, 0.4],
        )
        .toggle(
            "📊 Performance Benchmarks",
            lambda toggle: (
                toggle.h3("Benchmark Results")
                .table(
                    headers=["Endpunkt", "Avg Response Time", "RPS", "P95"],
                    rows=[
                        ["/api/users", "45ms", "850", "120ms"],
                        ["/api/users/{id}", "12ms", "2400", "35ms"],
                        ["/api/auth/login", "180ms", "200", "450ms"],
                    ],
                )
                .callout(
                    "Tests durchgeführt mit 1000 concurrent users über 5 Minuten", "📈"
                )
            ),
        )
        .build()
    )

    # Hauptstruktur
    assert "# API Documentation & Implementation Guide" in result
    assert (
        "Diese Dokumentation zeigt sowohl die API-Endpunkte als auch deren Implementierung."
        in result
    )
    assert "---" in result  # Divider

    # Spalten-Content
    assert "## 📋 API Endpunkte" in result
    assert "## ⚙️ Implementierung" in result
    assert "| Endpunkt | Methode | Beschreibung | Status |" in result
    assert "| /api/users | GET | Alle Benutzer abrufen | ✅ Aktiv |" in result
    assert "```python" in result
    assert "class APIClient:" in result
    
    # FIXED: Caption now appears in quotes on the first line, not as separate "Caption:" line
    assert '```python "Python API Client Implementation"' in result

    # Callouts und Listen
    assert (
        '[callout](💡 Alle Endpunkte erfordern eine gültige API-Authentifizierung "🔐")'
        in result
    )
    assert "- API-Key über Umgebungsvariablen laden" in result

    # Toggle mit Benchmarks - FIXED: Auch hier Quotes
    assert '+++ "📊 Performance Benchmarks"' in result
    assert "### Benchmark Results" in result
    assert "| /api/users | 45ms | 850 | 120ms |" in result
    assert (
        '[callout](Tests durchgeführt mit 1000 concurrent users über 5 Minuten "📈")'
        in result
    )