"""Upload a file from disk to Notion."""

import asyncio
from pathlib import Path

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        result = await notion.file_uploads.upload_file(Path("report.pdf"))
        print(f"Uploaded: {result.filename}  status={result.status}")


if __name__ == "__main__":
    asyncio.run(main())
