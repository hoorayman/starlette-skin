# starlette-skin
A wrapper for starlette in order to code in a tornado-like way<br>

Starlette is a flask-like python web framework, I write this module to enable a easy way which make starlette act like a tornado one.<br>
I also make postgresql and redis easy-use interface in it.<br>

## installation
* pip install starlette-skin<br>
## usage
Use StarletteSkin instead of starlette to instantiate. I add three optional parameters:<br>
* settings is a dict object of your own settings,<br>
* enable_dbs is a list object which you can add 'pg' or 'redis'.<br>

When you want to access db in handlers, you can use request.app._skin.pg/redis to achieve safe using of db which is a simplified way of using asyncpg and aioredis in which you have to always use async with statement.<br>

## Example1:<br>
```python
from starlette_skin import StarletteSkin
from starlette.routing import Route
from starlette.responses import UJSONResponse
import uvicorn

settings = {'PG':{
    'host':'127.0.0.1',
    'port':5432,
    'user':'postgres',
    'password':'postgres',
    'database':'community',
    'min_size':10,
    'max_size':10,
  },
  'REDIS':{
    'address':('127.0.0.1', 6379),
    'db':0,
    'minsize':10,
    'maxsize':10,
  }
}

async def homepage(request):
    user = await request.app._skin.pg('fetchval', 'select username from auth_user where id=$1', 1)
    return UJSONResponse({'hello':user})


app = StarletteSkin(debug=False, routes=[Route('/', endpoint=homepage, methods=['GET'])], settings=settings, enable_dbs=['pg', 'redis'])

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
```
<br>

## Example2:<br>

root(directory)<br>
--handlers(directory)<br>
----foo.py(file)<br>
--app.py(file)<br>
--urls.py(file)<br>
--settings.py(file)<br>
--utils.py(file)<br>
<br>

### app.py:<br>
```python
from starlette_skin import StarletteSkin
from urls import url_patterns
from settings import settings
import uvicorn


app = StarletteSkin(debug=False, routes=url_patterns, settings=settings, enable_dbs=['pg', 'redis'])

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
```
<br>

### urls.py:<br>
```python
from handlers import foo
from starlette.routing import Route


url_patterns = [
    Route('/', endpoint=foo.FooHdlr, methods=['GET']),
]
```
<br>

### settings.py:<br>
```python
settings = {}

settings['PG'] = {
    'host':'127.0.0.1',
    'port':5432,
    'user':'postgres',
    'password':'postgres',
    'database':'community',
    'min_size':10,
    'max_size':10,
}

settings['REDIS'] = {
    'address':('127.0.0.1', 6379),
    'db':0,
    'minsize':10,
    'maxsize':10,
}
```
<br>

### utils.py:<br>
```python
import functools


def speed_embed(method):
    "Only used when module starlette-skin installed!"
    @functools.wraps(method)
    async def wrapped(self, request, *args, **kwargs):
        self._req = request
        self._pg = request.app._skin.pg
        self._redis = request.app._skin.redis
        self._pgpool = request.app._pgpool
        return await method(self, request, *args, **kwargs)
    return wrapped
```
<br>

### foo.py:<br>
```python
from starlette.endpoints import HTTPEndpoint
from starlette.responses import UJSONResponse
import utils


class FooHdlr(HTTPEndpoint):
    @utils.speed_embed
    async def get(self, request):
        user = await self._pg('fetchval', 'select username from auth_user where id=$1', 1)
        return UJSONResponse({'hello':user})
```
<br>

