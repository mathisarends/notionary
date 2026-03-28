"""Upload raw bytes (e.g. generated content) to Notion."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        content = b"Hello from notionary!"
        result = await notion.file_uploads.upload_from_bytes(
            content, filename="hello.txt"
        )
        print(f"Uploaded: {result.filename}  status={result.status}")


if __name__ == "__main__":
    asyncio.run(main())
