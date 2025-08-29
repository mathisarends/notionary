from __future__ import annotations

import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.file.file_element_models import (
    CreateFileBlock,
    ExternalFile,
    FileBlock,
    FileType,
    FileUploadFile,
)
from notionary.blocks.mixins.captions import CaptionMixin
from notionary.blocks.mixins.file_upload.file_upload_mixin import FileUploadMixin
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult, BlockType


class FileElement(BaseBlockElement, CaptionMixin, FileUploadMixin):
    """
    Handles conversion between Markdown file embeds and Notion file blocks.
    
    Supports both external URLs and local file uploads.

    Markdown file syntax:
    - [file](https://example.com/document.pdf) - External URL
    - [file](./local/document.pdf) - Local file (will be uploaded)
    - [file](C:\Documents\report.pdf) - Absolute local path (will be uploaded)
    - [file](https://example.com/document.pdf)(caption:Annual Report) - With caption
    - (caption:Important document)[file](./doc.pdf) - Caption before URL
    """

    # Pattern matches both URLs and file paths
    FILE_PATTERN = re.compile(r"\[file\]\(([^)]+)\)")

    @classmethod
    def _extract_file_path(cls, text: str) -> Optional[str]:
        """Extract file path/URL from text, handling caption patterns."""
        clean_text = cls.remove_caption(text)
        
        match = cls.FILE_PATTERN.search(clean_text)
        if match:
            return match.group(1).strip()
        
        return None

    @classmethod
    def _is_local_file_path(cls, path: str) -> bool:
        """Determine if the path is a local file rather than a URL."""
        # Check if it's a URL
        if path.startswith(('http://', 'https://', 'ftp://')):
            return False
        
        # Check if it looks like a file path
        return ('/' in path or '\\' in path or 
                path.startswith('./') or path.startswith('../') or
                ':' in path[:3])  # Windows drive letters like C:

    @classmethod
    def _get_content_type(cls, file_path: Path) -> str:
        """Get MIME type based on file extension."""
        extension_map = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.zip': 'application/zip',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
        }
        
        suffix = file_path.suffix.lower()
        return extension_map.get(suffix, 'application/octet-stream')

    @classmethod
    async def _upload_local_file(cls, file_path_str: str) -> Optional[str]:
        """
        Upload a local file and return the file upload ID.
        
        Args:
            file_path_str: String path to the local file
            
        Returns:
            File upload ID if successful, None otherwise
        """
        try:
            file_upload_client = cls._get_file_upload_client()
            file_path = Path(file_path_str)
            
            # Check if file exists
            if not file_path.exists():
                print(f"File not found: {file_path}")
                return None
            
            # Get file info
            file_size = file_path.stat().st_size
            content_type = cls._get_content_type(file_path)
            
            print(f"Uploading file: {file_path.name} ({file_size} bytes, {content_type})")
            
            # Step 1: Create file upload
            upload_response = await file_upload_client.create_file_upload(
                filename=file_path.name,
                content_type=content_type,
                content_length=file_size,
                mode="single_part"  # Use single_part for simplicity
            )
            
            if not upload_response:
                print("Failed to create file upload")
                return None
            
            print(f"Created file upload with ID: {upload_response.id}")
            
            # Step 2: Send file content
            success = await file_upload_client.send_file_from_path(
                file_upload_id=upload_response.id,
                file_path=file_path
            )
            
            if not success:
                print("Failed to send file content")
                return None
            
            print("File content sent successfully")
            
            print(f"File upload completed: {upload_response.id}")
            return upload_response.id
            
        except Exception as e:
            print(f"Error uploading file {file_path_str}: {e}")
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.FILE and block.file

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown file link to Notion FileBlock."""
        file_path = cls._extract_file_path(text.strip())
        if not file_path:
            return None
        
        print(f"Processing file: {file_path}")
        
        # Extract caption
        caption_text = cls.extract_caption(text.strip())
        caption_rich_text = cls.build_caption_rich_text(caption_text or "")
        
        # Determine if it's a local file or external URL
        if cls._is_local_file_path(file_path):
            print(f"Detected local file: {file_path}")
            
            # Upload the local file
            file_upload_id = await cls._upload_local_file(file_path)
            if not file_upload_id:
                print(f"Failed to upload file: {file_path}")
                return None
            
            # Create FILE_UPLOAD block
            file_block = FileBlock(
                type=FileType.FILE_UPLOAD,
                file_upload=FileUploadFile(id=file_upload_id),
                caption=caption_rich_text,
                name=Path(file_path).name
            )
            
        else:
            print(f"Using external URL: {file_path}")
            
            # Create EXTERNAL block for URLs
            file_block = FileBlock(
                type=FileType.EXTERNAL,
                external=ExternalFile(url=file_path),
                caption=caption_rich_text,
            )

        return CreateFileBlock(file=file_block)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.FILE or not block.file:
            return None

        fb: FileBlock = block.file

        # Determine the source for markdown
        if fb.type == FileType.EXTERNAL and fb.external:
            source = fb.external.url
        elif fb.type == FileType.FILE and fb.file:
            source = fb.file.url
        elif fb.type == FileType.FILE_UPLOAD and fb.file_upload:
            # For uploaded files, we can't recreate the original path
            # Use the filename if available, or a placeholder
            if fb.name:
                source = f"./uploaded/{fb.name}"
            else:
                source = f"./uploaded/file_{fb.file_upload.id}"
        else:
            return None

        result = f"[file]({source})"

        # Add caption if present
        caption_markdown = await cls.format_caption_for_markdown(fb.caption or [])
        if caption_markdown:
            result += caption_markdown

        return result

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for file blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="File blocks embed files from external URLs or upload local files with optional captions",
            syntax_examples=[
                "[file](https://example.com/document.pdf)",
                "[file](./local/document.pdf)",
                "[file](C:\\Documents\\report.xlsx)",
                "[file](https://example.com/document.pdf)(caption:Annual Report)",
                "(caption:Q1 Data)[file](./spreadsheet.xlsx)",
                "[file](./manual.docx)(caption:**User** manual)",
            ],
            usage_guidelines="Use for both external URLs and local files. Local files will be automatically uploaded to Notion. Supports various file formats including PDFs, documents, spreadsheets, images. Caption supports rich text formatting and should describe the file content or purpose.",
        )