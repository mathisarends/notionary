#!/usr/bin/env python3
"""
Notionary CLI - Integration Key Setup
"""

import click
import os
import platform
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

def get_paste_tips():
    """Get platform-specific paste tips"""
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        return [
            "• Terminal: [cyan]Cmd+V[/cyan]",
            "• iTerm2: [cyan]Cmd+V[/cyan]",
        ]
    elif system == "windows":
        return [
            "• PowerShell: [cyan]Right-click[/cyan] or [cyan]Shift+Insert[/cyan]",
            "• cmd: [cyan]Right-click[/cyan]",
        ]
    else:  # Linux and others
        return [
            "• Terminal: [cyan]Ctrl+Shift+V[/cyan] or [cyan]Right-click[/cyan]",
            "• Some terminals: [cyan]Shift+Insert[/cyan]",
        ]

def show_paste_tips():
    """Show platform-specific paste tips"""
    console.print("\n[bold yellow]💡 Paste Tips:[/bold yellow]")
    for tip in get_paste_tips():
        console.print(tip)
    console.print()

def get_notion_secret() -> str:
    """Get NOTION_SECRET using the same logic as NotionClient"""
    load_dotenv()
    return os.getenv("NOTION_SECRET", "")

@click.group()
@click.version_option()  # Automatische Version aus setup.py
def main():
    """
    Notionary CLI - Notion API Integration
    """
    pass

@main.command()
def init():
    """
    Setup your Notion Integration Key
    """
    # Check if key already exists
    existing_key = get_notion_secret()
    
    if existing_key:
        console.print(Panel.fit(
            "[bold green]✅ You're all set![/bold green]\n"
            f"Your Notion Integration Key is already configured.\n"
            f"Key: [dim]{existing_key[:8]}...[/dim]",
            title="Already Configured"
        ))
        
        # Option to reconfigure
        if Confirm.ask("\n[yellow]Would you like to update your key?[/yellow]"):
            setup_new_key()
        else:
            console.print("\n[blue]No changes made. Happy coding! 🚀[/blue]")
    else:
        # No key found, start setup
        console.print(Panel.fit(
            "[bold green]🚀 Notionary Setup[/bold green]\n"
            "Enter your Notion Integration Key to get started...\n\n"
            "[bold blue]🔗 Create an Integration Key or get an existing one:[/bold blue]\n"
            "[cyan]https://www.notion.so/profile/integrations[/cyan]",
            title="Initialization"
        ))
        setup_new_key()

def setup_new_key():
    """Handle the key setup process"""
    try:
        # Show Integration Key creation link
        console.print("\n[bold blue]🔗 Create an Integration Key:[/bold blue]")
        console.print("[cyan]https://www.notion.so/profile/integrations[/cyan]")
        console.print()
        
        # Get integration key
        integration_key = Prompt.ask(
            "[bold cyan]Notion Integration Key[/bold cyan]"
        )
        
        # Input validation
        if not integration_key or not integration_key.strip():
            console.print("[bold red]❌ Integration Key cannot be empty![/bold red]")
            return
            
        # Trim whitespace
        integration_key = integration_key.strip()
        
        # Check for common paste issues
        if integration_key in ["^V", "^v", "^C", "^c"]:
            console.print("[bold red]❌ Paste didn't work! Try:[/bold red]")
            show_paste_tips()
            return
        
        # Show masked feedback that paste worked
        masked_key = "•" * len(integration_key)
        console.print(f"[dim]Received: {masked_key} ({len(integration_key)} characters)[/dim]")
        
        # Basic validation for Notion keys
        if not integration_key.startswith('ntn_') or len(integration_key) < 30:
            console.print("[bold yellow]⚠️  Warning: This doesn't look like a valid Notion Integration Key[/bold yellow]")
            console.print("[dim]Notion keys usually start with 'ntn_' and are about 50+ characters long[/dim]")
            if not Confirm.ask("Continue anyway?"):
                return
        
        # Save the key
        if save_integration_key(integration_key):
            return  # Success!
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled.[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Error during setup: {e}[/bold red]")
        raise click.Abort()

def save_integration_key(integration_key: str) -> bool:
    """Save the integration key to .env file"""
    try:
        # .env Datei im aktuellen Verzeichnis erstellen/aktualisieren
        env_file = Path.cwd() / ".env"
        
        # Bestehende .env lesen falls vorhanden
        existing_lines = []
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                existing_lines = [line.rstrip() for line in f.readlines()]
        
        # NOTION_SECRET Zeile hinzufügen/ersetzen
        updated_lines = []
        notion_secret_found = False
        
        for line in existing_lines:
            if line.startswith('NOTION_SECRET='):
                updated_lines.append(f'NOTION_SECRET={integration_key}')
                notion_secret_found = True
            else:
                updated_lines.append(line)
        
        # Falls NOTION_SECRET noch nicht existiert, hinzufügen
        if not notion_secret_found:
            updated_lines.append(f'NOTION_SECRET={integration_key}')
        
        # .env Datei schreiben
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(updated_lines) + '\n')
        
        # Verification
        written_key = get_notion_secret()
        if written_key == integration_key:
            console.print("\n[bold green]✅ Integration Key saved and verified![/bold green]")
            console.print(f"[dim]Configuration: {env_file}[/dim]")
            console.print("\n[blue]Ready to use notionary in your Python code! 🚀[/blue]")
            return True
        else:
            console.print("\n[bold red]❌ Error: Key verification failed![/bold red]")
            return False
            
    except Exception as e:
        console.print(f"\n[bold red]❌ Error saving key: {e}[/bold red]")
        return False

if __name__ == '__main__':
    main()