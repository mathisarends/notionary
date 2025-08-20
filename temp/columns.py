from pydantic import functional_serializers

from notionary import MarkdownBuilder, NotionPage


def create_complex_markdown():
    """Erstellt ein komplexes zweispaltiges Layout als Proof of Concept."""

    builder = MarkdownBuilder()

    # Titel und Einleitung
    builder.h1("API Documentation & Implementation Guide")
    builder.paragraph(
        "Diese Dokumentation zeigt sowohl die API-Endpunkte als auch deren Implementierung."
    )
    builder.divider()

    # Zweispaltiges Layout: Tabelle links (60%), Code rechts (40%)
    builder.columns(
        # Linke Spalte: API-Endpunkte Tabelle
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
                    ["/api/users/{id}", "PUT", "Benutzer aktualisieren", "🔄 Beta"],
                    ["/api/users/{id}", "DELETE", "Benutzer löschen", "⚠️ Deprecated"],
                    [
                        "/api/auth/login",
                        "POST",
                        "Benutzer-Authentifizierung",
                        "✅ Aktiv",
                    ],
                    ["/api/auth/refresh", "POST", "Token erneuern", "✅ Aktiv"],
                ],
            )
            .callout(
                "💡 Alle Endpunkte erfordern eine gültige API-Authentifizierung", "🔐"
            )
        ),
        # Rechte Spalte: Implementierungsbeispiel
        lambda col: (
            col.h2("⚙️ Implementierung")
            .paragraph("Python-Client Beispiel für die API-Nutzung:")
            .code(
                code="""import requests
import json
from typing import Dict, List, Optional

class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def get_users(self) -> List[Dict]:
        \"\"\"Alle Benutzer abrufen.\"\"\"
        response = self.session.get(f'{self.base_url}/api/users')
        response.raise_for_status()
        return response.json()
    
    def get_user(self, user_id: int) -> Dict:
        \"\"\"Einzelnen Benutzer abrufen.\"\"\"
        response = self.session.get(
            f'{self.base_url}/api/users/{user_id}'
        )
        response.raise_for_status()
        return response.json()
    
    def create_user(self, user_data: Dict) -> Dict:
        \"\"\"Neuen Benutzer erstellen.\"\"\"
        response = self.session.post(
            f'{self.base_url}/api/users',
            data=json.dumps(user_data)
        )
        response.raise_for_status()
        return response.json()

# Verwendungsbeispiel
client = APIClient('https://api.example.com', 'your-api-key')
users = client.get_users()
print(f"Gefunden: {len(users)} Benutzer")""",
                language="python",
                caption="Python API Client Implementation",
            )
            .paragraph("**Wichtige Hinweise:**")
            .bulleted_list(
                [
                    "API-Key über Umgebungsvariablen laden",
                    "Retry-Mechanismus für fehlerhafte Requests",
                    "Rate-Limiting beachten (100 Requests/Min)",
                    "Logging für Debugging aktivieren",
                ]
            )
        ),
        # Breiten-Verhältnis: 60% links, 40% rechts
        width_ratios=[0.6, 0.4],
    )

    # Zusätzlicher Inhalt nach den Spalten
    builder.divider()
    builder.h2("🚀 Erweiterte Funktionen")

    # Dreispaltiges Layout für erweiterte Features
    builder.columns(
        lambda col: (
            col.h3("Authentication")
            .paragraph("OAuth 2.0 + JWT")
            .code("token = client.authenticate()", "python")
        ),
        lambda col: (
            col.h3("Caching")
            .paragraph("Redis-basiertes Caching")
            .code("@cache.memoize(timeout=300)", "python")
        ),
        lambda col: (
            col.h3("Monitoring")
            .paragraph("Prometheus Metriken")
            .code("metrics.increment('api.calls')", "python")
        ),
        width_ratios=[0.33, 0.33, 0.34],
    )
    # Abschluss mit Toggle für Details
    builder.toggle(
        "📊 Performance Benchmarks",
        lambda toggle: (
            toggle.h3("Was geht ab?")
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

    # Toggleable Heading Element
    builder.toggleable_heading(
        "🧩 Weitere technische Details anzeigen",
        2,
        lambda toggle: (
            toggle.h3("Technische Details")
            .paragraph(
                "Hier findest du weiterführende technische Informationen zur API-Architektur, Sicherheit und Skalierung."
            )
            .bulleted_list(
                [
                    "Microservice Architektur mit FastAPI",
                    "Automatisiertes Deployment via GitHub Actions",
                    "TLS/SSL Verschlüsselung für alle Endpunkte",
                    "Horizontal skalierbar durch Kubernetes",
                ]
            )
        ),
    )

    return builder.build()


async def main():
    page = await NotionPage.from_page_name("Jarvis Clipboard")

    markdown = create_complex_markdown()

    edge_result = await page.append_markdown(
        markdown, prepend_table_of_contents=True, append_divider=functional_serializers
    )
    if edge_result:
        print("✅ Edge case test with columns completed successfully")
    else:
        print("❌ Edge case test with columns failed")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
