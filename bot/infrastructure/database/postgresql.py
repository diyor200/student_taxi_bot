from typing import Union
import logging
import sys

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from tgbot.data import config


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

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE 
        );
        """
        await self.execute(sql, execute=True)
    
    async def create_table_registration(self):
        sql = """
        CREATE TABLE IF NOT EXISTS registration(
            id serial primary key,
            name varchar(255),
            surname varchar(255),
            age integer,
            lang varchar(255),
            address varchar(500),
            phone varchar(255) unique not null,
            created_at timestamp 
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_subject_registration(self):
        sql = """
        CREATE TABLE IF NOT EXISTS subject_registration(
            id serial primary key,
            name varchar(255),
            surname varchar(255),
            age integer,
            lang varchar(255),
            address varchar(500),
            phone varchar(255) unique not null,
            subject varchar(255),
            created_at timestamp 
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    # subject registraion
    async def add_subject_registration_data(self, name, surname, age, lang, address, phone, subject):
        sql = ("INSERT INTO subject_registration(name, surname, age, lang, address, phone, subject, created_at)"
               " VALUES($1, $2, $3, $4, $5, $6, $7, date_trunc('minute', NOW() AT TIME ZONE 'Asia/Tashkent'))")
        return await self.execute(sql, name, surname, int(age), lang, address, phone, subject, execute=True)

    async def get_all_subject_registration_data(self):
        return await self.execute("select * from subject_registration", fetch=True)

    #  contest registration
    async def add_registration_data(self, name, surname, age, lang, address, phone):
        sql = ("INSERT INTO registration(name, surname, age, lang, address, phone, created_at)"
               " VALUES($1, $2, $3, $4, $5, $6, date_trunc('minute', NOW() AT TIME ZONE 'Asia/Tashkent'))")
        return await self.execute(sql, name, surname, int(age), lang, address, phone, execute=True)

    async def get_all_registration_data(self):
        return await self.execute("select * from registration", fetch=True)

    # users
    async def add_user(self, full_name, username, telegram_id):
        sql = "INSERT INTO users (full_name, username, telegram_id) VALUES($1, $2, $3)"
        return await self.execute(sql, full_name, username, telegram_id, execute=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

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
