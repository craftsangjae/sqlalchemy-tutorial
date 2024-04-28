import asyncio

if __name__ == '__main__':
    from src.database import Database
    from src.models import *

    database = Database()
    asyncio.run(database.create_database())