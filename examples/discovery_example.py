"""
# Notionary: Database Discovery Example
=========================================

This example demonstrates how to discover databases available to your
Notion integration using the DatabaseDiscovery class.
"""

import asyncio
from notionary import DatabaseDiscovery

async def main():
    """Discover databases in your Notion workspace."""
    discovery = DatabaseDiscovery()

    await discovery.discover_and_print()
    
    print("\n ℹ️ You can use these names or IDs with NotionDatabaseFactory.")


if __name__ == "__main__":
    asyncio.run(main())