"""
Example usage of the Notion File Upload functionality.
"""

import asyncio
from pathlib import Path
from notionary import NotionFileUpload, NotionPage


async def upload_small_file_example():
    """Example: Upload a small file (< 20MB)"""

    # Initialize the file upload service
    file_uploader = NotionFileUpload()

    # Upload a file
    file_path = Path(__file__).parent / "files" / "my_document.pdf"
    upload_result = await file_uploader.upload_file(file_path)

    if upload_result:
        print("File uploaded successfully!")
        print(f"File ID: {upload_result.id}")
        print(f"Status: {upload_result.status}")
        print(f"Upload URL: {upload_result.upload_url}")
        return upload_result.id
    else:
        print("File upload failed")
        return None

async def upload_from_bytes_example():
    """Example: Upload file content from bytes"""

    file_uploader = NotionFileUpload()

    # Example: Upload some text as a file
    content = "Hello, this is my file content!".encode("utf-8")

    upload_result = await file_uploader.upload_from_bytes(
        file_content=content, filename="hello.txt", content_type="text/plain"
    )

    if upload_result:
        print(f"Bytes uploaded as file: {upload_result.id}")
        return upload_result.id

    return None


async def use_uploaded_file_in_page():
    """Example: Use an uploaded file in a Notion page"""

    # First upload a file
    file_uploader = NotionFileUpload()
    file_path = Path("./image.jpg")
    upload_result = await file_uploader.upload_file(file_path)

    if not upload_result:
        print("Failed to upload file")
        return

    # Wait for it to be ready
    completed = await file_uploader.wait_for_upload_completion(upload_result.id)

    if not completed:
        print("Upload did not complete successfully")
        return

    # Now use it in a page
    page = await NotionPage.from_page_id("your-page-id-here")

    # Add the uploaded file to the page using the file_upload ID
    markdown_content = f"""
# My Page with Uploaded File

Here's the file I uploaded:

![Uploaded Image](notion://file_upload/{upload_result.id})

The file has been successfully integrated into the page!
"""

    success = await page.append_markdown(markdown_content)

    if success:
        print("File successfully added to page!")
    else:
        print("Failed to add file to page")


async def list_recent_uploads_example():
    """Example: List recent file uploads"""

    file_uploader = NotionFileUpload()

    # Get recent uploads
    recent_uploads = await file_uploader.list_recent_uploads(limit=10)

    print(f"Found {len(recent_uploads)} recent uploads:")
    for upload in recent_uploads:
        print(
            f"- {upload.filename or 'Unknown'} (ID: {upload.id}, Status: {upload.status})"
        )


async def check_upload_status_example():
    """Example: Check the status of a file upload"""

    file_uploader = NotionFileUpload()
    file_upload_id = "your-upload-id-here"

    status = await file_uploader.get_upload_status(file_upload_id)

    if status:
        print(f"Upload status: {status}")

        if status == "uploaded":
            print("File is ready to use!")
        elif status == "pending":
            print("File is still processing...")
        elif status == "failed":
            print("File upload failed!")
    else:
        print("Could not retrieve upload status")


# Run examples
async def main():
    """Run all examples"""

    print("=== Notion File Upload Examples ===\n")

    # Upload a small file
    """ print("1. Uploading small file...")
    await upload_small_file_example()
    print() """

    # Upload from bytes
    print("2. Uploading from bytes...")
    await upload_from_bytes_example()
    print()

if __name__ == "__main__":
    asyncio.run(main())
