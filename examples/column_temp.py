import logging
import asyncio
import traceback
from notionary import NotionPage


async def main():
    """Tests batch processing by appending many blocks to a Notion page."""

    logger = logging.getLogger("notionary")
    logger.setLevel(logging.DEBUG)

    try:
        print("Searching for page by name...")
        page = await NotionPage.from_page_name("Jarvis Clipboard")

        icon, title, url = await asyncio.gather(
            page.get_icon(), page.get_title(), page.get_url()
        )
        print(f"Page found: {page.id}")
        print(f"{icon} → {title} → {url}")

        markdown = """
        ::: columns
        ::: column
        # Technische Spezifikationen

        Die **XYZ-5000** bietet folgende Spezifikationen:

        - **Prozessor**: Quantum Core i9-12900K
        - **Arbeitsspeicher**: 64GB DDR5-5600
        - **Grafikkarte**: Ultra RTX 4090 Ti
        - **Speicher**: 4TB NVMe SSD (Gen4)

        > "Die schnellste Workstation, die wir je getestet haben." - TechMagazin

        ```python
        # Benchmark-Ergebnisse
        scores = {
            'Rendering': 14500,
            'Compilation': 9800,
            'Machine Learning': 21300
        }
        ```
        :::

        ::: column
        ## Anwendungsbereiche

        1. **3D-Modellierung und Rendering**
        * Architekturvisualisierung
        * Produktdesign
        * Filmproduktion

        2. **Softwareentwicklung**
        * Kompilierung großer Codebases
        * Virtualisierung
        * Containerisierung

        3. **Datenanalyse**
        * Big Data Processing
        * Machine Learning Training
        * Neural Network Inference

        ---

        ### Branchen-Referenzen

        | Branche | Einsatzbereich | Effizienzsteigerung |
        |---------|----------------|---------------------|
        | Gaming  | Level-Design   | +87%                |
        | Medizin | CT-Analyse     | +92%                |
        | Finanz  | Risikomodelle  | +78%                |

        !> Unser Support-Team steht Ihnen bei Fragen zur Implementierung zur Verfügung.
        :::

        ::: column
        ## Preisgestaltung & Support

        ### Basis-Paket
        - Grundkonfiguration
        - 2 Jahre Garantie
        - Basic Support (E-Mail)
        - 4.999 €

        ### Professional-Paket
        - Erweiterte Konfiguration
        - 4 Jahre Garantie
        - Premium Support (24/7)
        - 7.499 €

        ### Enterprise-Paket
        - Maximale Konfiguration
        - 5 Jahre Garantie
        - Dedizierter Support-Manager
        - Individuelle Preisgestaltung

        ```javascript
        // Finanzierungsrechner
        function calculateMonthlyRate(price, months, interestRate) {
            const monthlyInterest = interestRate / 12 / 100;
            return price * monthlyInterest * Math.pow(1 + monthlyInterest, months) 
                / (Math.pow(1 + monthlyInterest, months) - 1);
        }
        ```

        ### Partner-Netzwerk
        * **Frankfurt**: TechSolutions GmbH
        * **Berlin**: DigiTech Berlin
        * **München**: BavarianBytes AG
        * **Hamburg**: NordBit Systems
        :::
        :::
        """
        
        markdown_appended = await page.append_markdown(markdown=markdown, append_divider=True)
        print(f"Markdown appended: {markdown_appended}")
        

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())
