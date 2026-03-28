"""List all uploaded files."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        files = await notion.file_uploads.list()
        for f in files:
            print(f"{f.filename}  status={f.status}  trash={f.in_trash}")


if __name__ == "__main__":
    asyncio.run(main())
