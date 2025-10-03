"""Script to fix *Block -> *Data in element files."""

import re
from pathlib import Path

# Mapping of Block types to Data types
REPLACEMENTS = {
    "AudioBlock": "AudioData",
    "BreadcrumbBlock": "BreadcrumbData",
    "BulletedListItemBlock": "BulletedListItemData",
    "CalloutBlock": "CalloutData",
    "ColumnBlock": "ColumnData",
    "DividerBlock": "DividerData",
    "EmbedBlock": "EmbedData",
    "EquationBlock": "EquationData",
    "FileBlock": "FileData",
    "NumberedListItemBlock": "NumberedListItemData",
    "QuoteBlock": "QuoteData",
    "TableOfContentsBlock": "TableOfContentsData",
    "ToDoBlock": "ToDoData",
    "VideoBlock": "VideoData",
}


def fix_file(file_path: Path):
    """Fix a single file."""
    content = file_path.read_text(encoding="utf-8")
    original_content = content

    # Fix imports
    for block_type, data_type in REPLACEMENTS.items():
        # Replace in imports
        content = re.sub(rf"\b{block_type}\b(?=\s*[,\)])", data_type, content)

    # Fix instantiations (but not in type hints or class definitions)
    for block_type, data_type in REPLACEMENTS.items():
        # Replace BlockType( instantiations
        content = re.sub(rf"{block_type}\s*\(", f"{data_type}(", content)

    if content != original_content:
        file_path.write_text(content, encoding="utf-8")
        print(f"Fixed: {file_path}")
        return True
    return False


def main():
    """Fix all mapping files."""
    mappings_dir = Path("notionary/blocks/mappings")

    python_files = list(mappings_dir.glob("*.py"))
    python_files = [f for f in python_files if f.name not in ["__init__.py", "base.py"]]

    fixed_count = 0
    for file_path in sorted(python_files):
        if fix_file(file_path):
            fixed_count += 1

    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
