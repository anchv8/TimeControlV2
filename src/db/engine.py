import os

import asyncpg


db_credentials = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'database': os.getenv('DB_NAME'),
    'host': os.getenv('DB_HOST'),
    'port': '5432'
}


# Create the database pool
async def create_pool():
    pool = await asyncpg.create_pool(**db_credentials, max_inactive_connection_lifetime=300)
    return pool


# Initialize the database pool
async def initialize_db():
    pool = await create_pool()
    return pool


# A function to set and get the database pool
async def get_pool():
    if not hasattr(get_pool, 'pool'):
        get_pool.pool = await initialize_db()
    return get_pool.pool
