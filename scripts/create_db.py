import asyncio
from src.database import Database
from src.models import *

async def main():
    database = Database()
    await database.create_database()

if __name__ == '__main__':
    asyncio.run(main())