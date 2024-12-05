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

    async def get_user_by_telegram_id(self, telegram_id):
        sql = "SELECT * FROM users WHERE telegram_id = $1"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def get_user_by_id(self, id):
        sql = "select * from users where id = $1"
        return await self.execute(sql, id, fetchrow=True)

    async def update_user_type(self, telegram_id, user_type):
        sql = "UPDATE Users SET type=$1 WHERE telegram_id=$2"
        return await self.execute(sql, user_type, telegram_id, execute=True)

    async def update_user(self, name=None, surname=None, phone=None, telegram_id=0):
        count = 1
        args = []
        sql = "UPDATE users SET "

        if name is not None:
            sql += f"name=${count}"
            args.append(name)
            count += 1

        if surname is not None:
            sql += f"surname=${count}"
            args.append(surname)
            count += 1

        if phone is not None:
            sql += f"phone=${count}"
            args.append(phone)
            count += 1

        sql += f" WHERE telegram_id=${count}"

        return await self.execute(sql, *args, telegram_id, execute=True)

    # cars
    async def add_car(self, user_id, car_model, car_number):
        sql = """insert into cars(user_id, model, number, created_at, updated_at)
                    values ($1, $2, $3, now(), now()) returning id;"""
        return await self.execute(sql, user_id, car_model, car_number, fetchrow=True)

    async def get_car_by_driver_id(self, driver_id):
        sql = "select * from cars where user_id = $1 limit 1"
        return await self.execute(sql, driver_id, fetchrow=True)

    async def update_car(self, car_model=None, car_number=None, telegram_id=0):
        count = 1
        args = []
        sql = "UPDATE cars SET "

        if car_model is not None:
            sql += f"model=${count}"
            args.append(car_model)
            count += 1

        if car_number is not None:
            sql += f"number=${count}"
            args.append(car_number)
            count += 1

        args.append(telegram_id)
        sql += f" WHERE user_id=(select id from users where telegram_id = ${count})"

        return await self.execute(sql, *args, execute=True)

    # routes
    async def add_route(self, driver_id, from_region_id, from_district_id, to_region_id, to_district_id, message_id,
                        start_time, seats, price, comment, status):
        sql = """insert into directions(driver_id, from_region_id, from_district_id, to_region_id, to_district_id,
         message_id, start_time, seats, price, comment, status, created_at, updated_at)
                 values($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, now(), now()) returning id;"""
        return await self.execute(sql, driver_id, from_region_id, from_district_id, to_region_id, to_district_id,
                                  message_id, start_time, seats, price, comment, status, fetchrow=True)

    async def get_daily_routes(self):
        sql = "SELECT * FROM directions where created_at::date = now()::date;"
        return await self.execute(sql, fetch=True)

    async def get_monthly_routes(self):
        sql = "SELECT * FROM directions where created_at::date = now()::date;"
        return await self.execute(sql, fetch=True)

    async def get_route_by_region_district(self, from_region_id, from_district_id, to_region_id, to_district_id, date):
        sql = """select * from directions where from_region_id=$1
                           and from_district_id=$2 and to_region_id=$3 and to_district_id=$4 and status = 1 
                           and created_at::date=$5 order by start_time;"""
        return await self.execute(sql, from_region_id, from_district_id, to_region_id, to_district_id, date, fetch=True)

    async def get_routes_by_region(self, from_region_id, to_region_id, date):
        sql = """select * from directions where from_region_id=$1
                           and to_region_id=$2 and status = 1 and created_at::date=$3 order by start_time;;"""
        return await self.execute(sql, from_region_id, to_region_id, date, fetch=True)

    async def get_expired_direction_message_ids_for_passive(self):
        sql = ("""select
                        d.message_id,
                        d.from_region_id,
                        d.from_district_id,
                        d.to_region_id,
                        d.to_district_id,
                        d.start_time,
                        d.price,
                        d.comment,
                        u.telegram_id,
                        u.telegram_id,
                        u.name,
                        u.surname,
                        u.phone,
                        c.model,
                        c.number,
                        d.status
                    from directions d join users u on d.driver_id=u.id join cars c on c.user_id=u.id
                    where  d.created_at::date < now()::date and d.status = 1 and d.message_id > 0;
        """)
        return await self.execute(sql, fetch=True)

    async def passive_expired_directions(self):
        sql = "UPDATE directions SET status = 3 WHERE created_at::date < NOW()::date AND status = 1"
        return await self.execute(sql, execute=True)

    async def get_route_by_id(self, route_id):
        sql = "select * from directions where id = $1"
        return await self.execute(sql, route_id, fetchrow=True)

    async def get_active_route_by_user_id(self, user_id):
        sql = "select * from directions where driver_id = $1 and status = 1"
        return await self.execute(sql, user_id, fetchrow=True)

    # user routes
    async def add_user_route(self, driver_id, from_region_id, from_district_id, to_region_id, to_district_id,
                             start_time, seats, price, comment):
        sql = """insert into user_directions(user_id, direction_id, created_at, updated_at)
                    values ($1, $2, now(), now()) returning id;"""
        return await self.execute(sql, driver_id, from_region_id, from_district_id, to_region_id, to_district_id,
                                  start_time, seats, price, comment, fetchrow=True)

    async def update_direction_status(self, route_id, status: int):
        sql = "UPDATE directions SET status = $1 WHERE id = $2"
        return await self.execute(sql, status, route_id, execute=True)

    # topics
    async def add_topic(self, region_id, topic_id, name):
        sql = """insert into topics(region_id, topic_id, name) values ($1, $2, $3) returning id;"""
        return await self.execute(sql, region_id, topic_id, name, fetchrow=True)

    async def get_topic_by_region_id(self, region_id):
        sql = "select * from topics where region_id=$1"
        return await self.execute(sql, region_id, fetchrow=True)


