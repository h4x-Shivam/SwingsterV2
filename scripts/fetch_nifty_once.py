import asyncio
import aiohttp
import sys
from fetcher.fetch_all import fetch_one
from fetcher.db_writer import write_ohlcv

# Windows asyncio policy fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    connector = aiohttp.TCPConnector(ssl=False)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    }
    timeout = aiohttp.ClientTimeout(total=30)
    semaphore = asyncio.Semaphore(1)
    
    async with aiohttp.ClientSession(connector=connector, headers=headers, timeout=timeout) as session:
        print("Fetching ^NSEI benchmark data...")
        rows = await fetch_one(session, semaphore, "^NSEI", "1y")
        if rows:
            written = write_ohlcv(rows)
            print(f"Successfully fetched and wrote {written} rows of ^NSEI data to the database.")
        else:
            print("Failed to fetch ^NSEI data.")

if __name__ == '__main__':
    asyncio.run(main())
