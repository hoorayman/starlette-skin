from setuptools import setup


setup(
    name='starlette-skin',
    version='0.1.0',
    packages=['starlette_skin'],
    url='https://github.com/beforeicer/starlette-skin',
    license='BSD License',
    author='hoo',
    author_email='beforeicer@126.com',
    keywords="starlette like tornado style",
    install_requires=['starlette>=0.11.4', 'asyncpg>=0.18.3', 'aioredis>=1.2.0'],
    description='a wrapper for starlette in order to code in a tornado-like way',
    long_description='a wrapper for starlette in order to code in a tornado-like way',
    platforms=["*nix"],
)

