from notionary.file_upload import NotionFileUploadClient
from notionary.page.page_context import get_page_context


class FileUploadMixin:
    """Mixin to add caption parsing functionality to block elements."""

    
    def _get_file_upload_client(self) -> NotionFileUploadClient:
        context = get_page_context()
        
        return context.file_upload_client