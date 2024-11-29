from typing import Union
import logging
import sys

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from ...data import config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None]

    async def create(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=config.DB_USER,
                password=config.DB_PASS,
                host=config.DB_HOST,
                database=config.DB_NAME,
                port=config.DB_PORT,
            )
        except:
            logging.error("can't connect to database")
            sys.exit(1)

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

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    # users
    async def add_user(self, username, telegram_id, name, surname, phone, user_type):
        sql = """insert into users(username, telegram_id, name, surname, phone, type, status, created_at, updated_at) 
                    values ($1, $2, $3, $4, $5, $6, true, now(), now()) returning id;"""
        return await self.execute(sql, username, telegram_id, name, surname, phone, user_type, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM users"
        return await self.execute(sql, fetch=True)

    async def get_user_by_telegram_id(self, telegram_id):
        sql = "SELECT * FROM users WHERE telegram_id = $1"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def update_user_type(self, telegram_id, user_type):
        sql = "UPDATE Users SET type=$1 WHERE telegram_id=$2"
        return await self.execute(sql, user_type, telegram_id, execute=True)

    # cars
    async def add_car(self, user_id, car_model, car_number):
        sql = """insert into cars(user_id, model, number, created_at, updated_at)
                    values ($1, $2, $3, now(), now()) returning id;"""
        return await self.execute(sql, user_id, car_model, car_number, fetchrow=True)

    # routes
    async def add_route(self, driver_id, from_region_id, from_district_id, to_region_id, to_district_id, start_time,
                        seats, price, comment):
        sql = """insert into directions(driver_id, from_region_id, from_district_id, to_region_id, to_district_id,
                    start_time, seats, price, comment, created_at, updated_at)
                 values($1, $2, $3, $4, $5, $6, $7, $8, $9, now(), now()) returning id;"""
        return await self.execute(sql, driver_id, from_region_id, from_district_id, to_region_id, to_district_id,
                                  start_time, seats, price, comment, fetchrow=True)
