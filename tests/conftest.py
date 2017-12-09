import asyncio
import sys
import logging
import pytest


logging.basicConfig(level='DEBUG', stream=sys.stdout)


@pytest.fixture(scope='function')
def loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    except:
        loop.close()
