from starlette.applications import Starlette
import asyncpg, aioredis


class AppSkin(type):
    def __call__(cls, *args, **kargs):
        try:
            skargs = dict(kargs)
            skargs.pop('settings', None)
            skargs.pop('enable_dbs', None)
            app = Starlette(*args, **skargs)
        except TypeError: # handle parameters error, in order to accept arbitrary parameters
            app = Starlette()
        app._skin = cls.__new__(cls, app) # ref to a instance of StarletteSkin, so app can get func from StarletteSkin
        app._config = kargs.get('settings') or {}
        app._skin.registerDb(kargs.get('enable_dbs', []))
        return app

class StarletteSkin(metaclass=AppSkin):
    def __new__(cls, app):
        me = super().__new__(cls)
        me.app = app
        return me

    async def pg(self, method, *arg, **karg):
        async with self.app._pgpool.acquire() as conn:
            result = await type(conn).__dict__[method](conn, *arg, **karg)
        return result
    
    async def redis(self, *arg, **karg):
        async with self.app._redispool.get() as conn:
            result = await conn.execute(*arg, **karg)
        return result

    def registerDb(self, dbs):
        async def register_pg():
            self.app._pgpool = await asyncpg.create_pool(**self.app._config['PG'])
        async def register_redis():
            self.app._redispool = await aioredis.create_pool(**self.app._config['REDIS'])
        db_reg_map = {'pg':register_pg, 'redis':register_redis}
        async def close_pg():
            await self.app._pgpool.close()
        async def close_redis():
            self.app._redispool.close()
            await self.app._redispool.wait_closed()
        db_close_map = {'pg':close_pg, 'redis':close_redis}
        for db in dbs:
            self.app.add_event_handler('startup', db_reg_map[db])
            self.app.add_event_handler('shutdown', db_close_map[db])

