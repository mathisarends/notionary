#!/usr/bin/env python3
"""
Notionary CLI - Integration Key Setup
"""

import click
import os
import platform
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from notionary.workspace import NotionWorkspace


# Disable logging for CLI usage
def disable_notionary_logging():
    """Disable logging for notionary modules when used in CLI"""
    # Option 1: Set to WARNING level (recommended for CLI)
    logging.getLogger("notionary").setLevel(logging.WARNING)
    logging.getLogger("DatabaseDiscovery").setLevel(logging.WARNING)
    logging.getLogger("NotionClient").setLevel(logging.WARNING)


def enable_verbose_logging():
    """Enable verbose logging for debugging (use with --verbose flag)"""
    logging.getLogger("notionary").setLevel(logging.DEBUG)
    logging.getLogger("DatabaseDiscovery").setLevel(logging.DEBUG)
    logging.getLogger("NotionClient").setLevel(logging.DEBUG)


# Initialize logging configuration for CLI
disable_notionary_logging()

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


async def fetch_notion_databases_with_progress():
    """Fetch databases using DatabaseDiscovery with progress animation"""
    try:
        workspace = NotionWorkspace()

        # Create progress display with custom spinner
        with Progress(
            SpinnerColumn(spinner_name="dots12", style="cyan"),
            TextColumn("[bold blue]Discovering databases..."),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            # Add progress task
            task = progress.add_task("Fetching...", total=None)

            # Fetch databases
            databases = await workspace.list_all_databases(limit=50)

            # Update progress to show completion
            progress.update(
                task, description=f"[bold green]Found {len(databases)} databases!"
            )

            # Brief pause to show completion
            await asyncio.sleep(0.5)

        return {"databases": databases, "success": True}

    except Exception as e:
        return {"error": str(e), "success": False}


def show_databases_overview(api_key: str):
    """Show available databases with nice formatting"""
    console.print("\n[bold blue]🔍 Connecting to Notion...[/bold blue]")

    # Run async function in sync context
    try:
        result = asyncio.run(fetch_notion_databases_with_progress())
    except Exception as e:
        console.print(
            Panel.fit(
                f"[bold red]❌ Unexpected error[/bold red]\n\n"
                f"[red]{str(e)}[/red]\n\n"
                "[yellow]Please check:[/yellow]\n"
                "• Your internet connection\n"
                "• Your integration key validity\n"
                "• Try running the command again",
                title="Connection Error",
            )
        )
        return

    if not result["success"]:
        console.print(
            Panel.fit(
                f"[bold red]❌ Could not fetch databases[/bold red]\n\n"
                f"[red]{result['error']}[/red]\n\n"
                "[yellow]Common issues:[/yellow]\n"
                "• Check your integration key\n"
                "• Make sure your integration has access to databases\n"
                "• Visit your integration settings to grant access",
                title="Connection Error",
            )
        )
        return

    databases = result["databases"]

    if not databases:
        console.print(
            Panel.fit(
                "[bold yellow]⚠️  No databases found[/bold yellow]\n\n"
                "Your integration key is valid, but no databases are accessible.\n\n"
                "[bold blue]To grant access:[/bold blue]\n"
                "1. Go to any Notion database\n"
                "2. Click the '...' menu (top right)\n"
                "3. Go to 'Add connections'\n"
                "4. Find and select your integration\n\n"
                "[cyan]https://www.notion.so/help/add-and-manage-connections-with-the-api[/cyan]",
                title="No Databases Available",
            )
        )
        return

    # Create beautiful table
    table = Table(
        title=f"📊 Available Databases ({len(databases)} found)",
        box=box.ROUNDED,
        title_style="bold green",
        header_style="bold cyan",
    )

    table.add_column("#", style="dim", justify="right", width=3)
    table.add_column("Database Name", style="bold white", min_width=25)
    table.add_column("ID", style="dim cyan", min_width=36)

    for i, (title, db_id) in enumerate(databases, 1):
        table.add_row(str(i), title or "Untitled Database", db_id)

    console.print("\n")
    console.print(table)

    # Success message with next steps
    console.print(
        Panel.fit(
            "[bold green]🎉 Setup Complete![/bold green]\n\n"
            f"Found [bold cyan]{len(databases)}[/bold cyan] accessible database(s).\n"
            "You can now use notionary in your Python code!\n\n"
            "[bold yellow]💡 Tip:[/bold yellow] Run [cyan]notionary db[/cyan] anytime to see this overview again.",
            title="Ready to Go!",
        )
    )


@click.group()
@click.version_option()  # Automatische Version aus setup.py
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def main(verbose):
    """
    Notionary CLI - Notion API Integration
    """
    if verbose:
        enable_verbose_logging()
        console.print("[dim]Verbose logging enabled[/dim]")
    pass


@main.command()
def init():
    """
    Setup your Notion Integration Key
    """
    # Check if key already exists
    existing_key = get_notion_secret()

    if existing_key:
        console.print(
            Panel.fit(
                "[bold green]✅ You're all set![/bold green]\n"
                f"Your Notion Integration Key is already configured.\n"
                f"Key: [dim]{existing_key[:8]}...[/dim]",
                title="Already Configured",
            )
        )

        # Option to reconfigure or show databases
        choice = Prompt.ask(
            "\n[yellow]What would you like to do?[/yellow]",
            choices=["show", "update", "exit"],
            default="show",
        )

        if choice == "show":
            show_databases_overview(existing_key)
        elif choice == "update":
            setup_new_key()
        else:
            console.print("\n[blue]Happy coding! 🚀[/blue]")
    else:
        # No key found, start setup
        console.print(
            Panel.fit(
                "[bold green]🚀 Notionary Setup[/bold green]\n"
                "Enter your Notion Integration Key to get started...\n\n"
                "[bold blue]🔗 Create an Integration Key or get an existing one:[/bold blue]\n"
                "[cyan]https://www.notion.so/profile/integrations[/cyan]",
                title="Initialization",
            )
        )
        setup_new_key()


@main.command()
def db() -> None:
    """
    Show available Notion databases
    """
    existing_key = get_notion_secret()

    if not existing_key:
        console.print(
            Panel.fit(
                "[bold red]❌ No Integration Key found![/bold red]\n\n"
                "Please run [cyan]notionary init[/cyan] first to set up your key.",
                title="Not Configured",
            )
        )
        return

    show_databases_overview(existing_key)


def setup_new_key():
    """Handle the key setup process"""
    try:
        # Show Integration Key creation link
        console.print("\n[bold blue]🔗 Create an Integration Key:[/bold blue]")
        console.print("[cyan]https://www.notion.so/profile/integrations[/cyan]")
        console.print()

        # Get integration key
        integration_key = Prompt.ask("[bold cyan]Notion Integration Key[/bold cyan]")

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
        console.print(
            f"[dim]Received: {masked_key} ({len(integration_key)} characters)[/dim]"
        )

        # Basic validation for Notion keys
        if not integration_key.startswith("ntn_") or len(integration_key) < 30:
            console.print(
                "[bold yellow]⚠️  Warning: This doesn't look like a valid Notion Integration Key[/bold yellow]"
            )
            console.print(
                "[dim]Notion keys usually start with 'ntn_' and are about 50+ characters long[/dim]"
            )
            if not Confirm.ask("Continue anyway?"):
                return

        # Save the key
        if save_integration_key(integration_key):
            # Show databases overview after successful setup
            show_databases_overview(integration_key)

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
            with open(env_file, "r", encoding="utf-8") as f:
                existing_lines = [line.rstrip() for line in f.readlines()]

        # NOTION_SECRET Zeile hinzufügen/ersetzen
        updated_lines = []
        notion_secret_found = False

        for line in existing_lines:
            if line.startswith("NOTION_SECRET="):
                updated_lines.append(f"NOTION_SECRET={integration_key}")
                notion_secret_found = True
            else:
                updated_lines.append(line)

        # Falls NOTION_SECRET noch nicht existiert, hinzufügen
        if not notion_secret_found:
            updated_lines.append(f"NOTION_SECRET={integration_key}")

        # .env Datei schreiben
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("\n".join(updated_lines) + "\n")

        # Verification
        written_key = get_notion_secret()
        if written_key == integration_key:
            console.print(
                "\n[bold green]✅ Integration Key saved and verified![/bold green]"
            )
            console.print(f"[dim]Configuration: {env_file}[/dim]")
            return True
        else:
            console.print("\n[bold red]❌ Error: Key verification failed![/bold red]")
            return False

    except Exception as e:
        console.print(f"\n[bold red]❌ Error saving key: {e}[/bold red]")
        return False


if __name__ == "__main__":
    main()
