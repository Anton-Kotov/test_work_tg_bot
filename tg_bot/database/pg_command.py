from typing import Union

import asyncpg as asyncpg
from asyncpg import Pool, Connection

from tg_bot.config import load_config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        config = load_config(".env")
        self.pool = await asyncpg.create_pool(
            user=config.db.user,
            password=config.db.password,
            host=config.db.host,
            database=config.db.database
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
        return result

    async def create_table(self, sql):
        await self.execute(sql, execute=True)

    async def drop_table(self):
        sql = """
        DROP TABLE IF EXISTS users;"""
        await self.execute(sql, execute=True)

    async def add_user(self, id, first_name, last_name):
        sql = """
        INSERT INTO users
            (telegram_id, first_name, last_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id)
            DO NOTHING;
        """
        await self.execute(sql, id, first_name, last_name, execute=True)

    async def exist_user(self, id):
        sql = """
                SELECT EXISTS 
                (SELECT * FROM users 
                 WHERE telegram_id = $1);"""
        return await self.execute(sql, int(id), fetchrow=True)

    async def get_user(self, id):
        sql = f""" 
                SELECT *
                FROM users
                WHERE telegram_id = $1; """

        return await self.execute(sql, int(id), fetchrow=True)


    async def get_state(self, id):
        sql = f""" 
                SELECT state
                FROM users
                WHERE telegram_id = $1; """

        return await self.execute(sql, int(id), fetchrow=True)

    async def get_all(self):
        sql = f""" 
                SELECT *
                FROM users;
               """

        return await self.execute(sql, fetchrow=True)


    async def add_balance(self, id, money):
        sql = """
                UPDATE users
                SET balance = balance + $1
                WHERE telegram_id = $2;
                """
        await self.execute(sql, int(money), id, execute=True)

    async def new_balance(self, id, money):
        sql = """
                UPDATE users
                SET balance = $2
                WHERE telegram_id = $1;
                """
        await self.execute(sql, int(id), int(money), execute=True)

    async def ban_user(self, id):
        sql = """
                UPDATE users
                SET state = FALSE
                WHERE telegram_id = $1;
                """
        await self.execute(sql, int(id), execute=True)

    async def unban_user(self, id):
        sql = """
                UPDATE users
                SET state = TRUE
                WHERE telegram_id = $1;
                """
        await self.execute(sql, int(id), execute=True)

    async def delete_user(self, id):
        sql = """
                DELETE FROM users
                WHERE telegram_id = $1;
                """
        await self.execute(sql, int(id), execute=True)



    async def close(self) -> None:
        if self.pool is None:
            return None

        await self.pool.close()