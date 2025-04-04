# main.py

import sys
import os
import inspect
from typing import List, Type

# Füge das aktuelle Verzeichnis zum Python-Pfad hinzu, falls notwendig
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importiere die erstellten Klassen
from llm_documentation_generator import LLMDocumentationGenerator
from system_prompt_generator import SystemPromptGenerator

# Importiere die NotionBlockElement-Klasse
from notionary.converters.notion_block_element import NotionBlockElement

def discover_element_classes_manually(package_name: str) -> List[Type[NotionBlockElement]]:
    """
    Entdeckt alle Klassen in einem Paket, die von NotionBlockElement erben.
    Diese Funktion zeigt, wie man die automatische Entdeckung selbst implementieren kann.
    
    Args:
        package_name: Name des Pakets, in dem die Klassen gefunden werden sollen
        
    Returns:
        Liste der gefundenen NotionBlockElement-Subklassen
    """
    import importlib
    import pkgutil
    
    element_classes = []
    
    # Importiere das Paket
    package = importlib.import_module(package_name)
    # Erhalte das Verzeichnis des Pakets
    if hasattr(package, '__path__'):
        package_path = package.__path__
    else:
        # Falls es kein Paket ist, sondern ein Modul
        package_path = [os.path.dirname(package.__file__)]
    
    # Durchsuche alle Module im Paket
    for _, module_name, is_pkg in pkgutil.iter_modules(package_path):
        # Ignoriere Unterpakete für dieses einfache Beispiel
        if is_pkg:
            continue
        
        # Importiere das Modul
        module_full_name = f"{package_name}.{module_name}"
        module = importlib.import_module(module_full_name)
        
        # Finde alle Klassen im Modul
        for name, obj in inspect.getmembers(module):
            # Prüfe, ob es eine Klasse ist und von NotionBlockElement erbt
            if (inspect.isclass(obj) and 
                issubclass(obj, NotionBlockElement) and 
                obj != NotionBlockElement):
                element_classes.append(obj)
                print(f"Gefunden: {obj.__name__} in {module_full_name}")
    
    return element_classes

def main():
    """
    Hauptfunktion zur Generierung der Dokumentation und des System-Prompts
    """
    print("Starte die Generierung der Notion LLM-Dokumentation...")
    
    # Methode 1: Nutzung der SystemPromptGenerator-Klasse für automatische Entdeckung
    print("\nMethode 1: Automatische Entdeckung über SystemPromptGenerator...")
    try:
        system_prompt = SystemPromptGenerator.generate_system_prompt(
            elements_package_path="notionary.converters.elements"
        )
        
        # Speichere den generierten System-Prompt
        output_path = "generated_system_prompt.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(system_prompt)
        print(f"System-Prompt wurde in '{output_path}' gespeichert")
    except Exception as e:
        print(f"Fehler bei der automatischen Entdeckung mit SystemPromptGenerator: {e}")
    
    # Methode 2: Direkte manuelle Implementierung der automatischen Entdeckung
    print("\nMethode 2: Direkte manuelle Implementierung der automatischen Entdeckung...")
    try:
        # Finde alle Element-Klassen im Paket
        element_classes = discover_element_classes_manually("notionary.converters.elements")
        print(f"Gefundene Element-Klassen: {[cls.__name__ for cls in element_classes]}")
        
        # Generiere Dokumentation für alle gefundenen Klassen
        if element_classes:
            element_docs = LLMDocumentationGenerator.generate_full_documentation(element_classes)
            
            # Erstelle einen System-Prompt mit dieser Dokumentation
            manual_system_prompt = f"""
Sie sind ein Assistent, der Benutzern hilft, Inhalte für Notion-Seiten zu erstellen.
Verwenden Sie die unten definierte benutzerdefinierte Markdown-Syntax, um richtig formatierte Notion-Blöcke zu erstellen.

{element_docs}

Verwenden Sie diese speziellen Markdown-Formate anstelle von regulärem Markdown, wenn es angebracht ist.
Dies stellt sicher, dass der Inhalt korrekt in Notion-Blöcke umgewandelt wird.
"""
            
            # Speichere den System-Prompt
            manual_output_path = "manual_discovery_system_prompt.txt"
            with open(manual_output_path, 'w', encoding='utf-8') as f:
                f.write(manual_system_prompt.strip())
            print(f"System-Prompt mit manueller Entdeckung wurde in '{manual_output_path}' gespeichert")
        else:
            print("Keine Element-Klassen gefunden!")
    except Exception as e:
        print(f"Fehler bei der manuellen Implementierung der Entdeckung: {e}")
    
    # Methode 3: Explizite Auflistung einzelner Klassen (statisch)
    print("\nMethode 3: Explizite Auflistung einzelner Klassen...")
    try:
        # Hier importieren wir explizit die Element-Klassen, die wir verwenden möchten
        from notionary.converters.elements.callout_element import CalloutElement
        # Weitere explizite Importe hier...
        
        # Statische Liste von Element-Klassen
        static_element_classes = [
            CalloutElement,
            # Weitere Element-Klassen hier manuell hinzufügen
        ]
        
        print(f"Statisch aufgelistete Element-Klassen: {[cls.__name__ for cls in static_element_classes]}")
        
        # Generiere Dokumentation für diese statisch aufgelisteten Klassen
        static_element_docs = LLMDocumentationGenerator.generate_full_documentation(static_element_classes)
        
        # Erstelle einen System-Prompt mit dieser Dokumentation
        static_system_prompt = f"""
Sie sind ein Assistent, der Benutzern hilft, Inhalte für Notion-Seiten zu erstellen.
Verwenden Sie die unten definierte benutzerdefinierte Markdown-Syntax, um richtig formatierte Notion-Blöcke zu erstellen.

{static_element_docs}

Verwenden Sie diese speziellen Markdown-Formate anstelle von regulärem Markdown, wenn es angebracht ist.
Dies stellt sicher, dass der Inhalt korrekt in Notion-Blöcke umgewandelt wird.
"""
        
        # Speichere den System-Prompt
        static_output_path = "static_list_system_prompt.txt"
        with open(static_output_path, 'w', encoding='utf-8') as f:
            f.write(static_system_prompt.strip())
        print(f"System-Prompt mit statischer Liste wurde in '{static_output_path}' gespeichert")
    except Exception as e:
        print(f"Fehler bei der expliziten Auflistung: {e}")

if __name__ == "__main__":
    main()