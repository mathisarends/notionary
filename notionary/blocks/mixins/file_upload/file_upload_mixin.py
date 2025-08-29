from notionary.file_upload import NotionFileUploadClient
from notionary.page.page_context import get_page_context


class FileUploadMixin:
    """Mixin to add caption parsing functionality to block elements."""
    
    @classmethod
    def _get_file_upload_client(cls) -> NotionFileUploadClient:
        """Get the file upload client from the current page context."""
        context = get_page_context()
        
        return context.file_upload_client