#!/usr/bin/env python3
"""Test script for SyntaxPromptBuilder functionality."""

from notionary import NotionPage
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.syntax_prompt_builder import SyntaxPromptBuilder


async def main():
    """Test the SyntaxPromptBuilder with the actual block registry."""
    print("=" * 60)
    print("Testing SyntaxPromptBuilder")
    print("=" * 60)
    
    # Create block registry and syntax builder
    page = await NotionPage.from_page_name("Jarvis Clipboard")
    builder = SyntaxPromptBuilder(page.block_element_registry)
    
    print("\n3. Testing build_markdown_reference() (first 1000 chars):")
    print("-" * 60)
    full_ref = builder.build_markdown_reference()
    print(full_ref)
    
    print(f"\nFull reference length: {len(full_ref)} characters")
    print("=" * 60)
    print("Test completed successfully!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
