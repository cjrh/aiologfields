import logging
import asyncio
from uuid import uuid4
import aiologfields


def test_main(loop: asyncio.AbstractEventLoop, caplog):
    aiologfields.install()
    correlation_id = str(uuid4())
    logger = logging.getLogger('blah')

    async def cf2():
        logger.info('blah blah')

    async def cf1():
        ct = asyncio.Task.current_task()
        ct.logging_fields.correlation_id = correlation_id
        await cf2()

    loop.run_until_complete(cf1())

    assert caplog.records[0].correlation_id == correlation_id


def test_set(loop: asyncio.AbstractEventLoop, caplog):
    # TODO: add a negative test for running in a thread lacking a loop
    aiologfields.install()
    correlation_id = str(uuid4())
    logger = logging.getLogger('blah')

    async def cf2():
        logger.info('blah blah')

    async def cf1():
        aiologfields.set_fields(correlation_id=correlation_id)
        await cf2()

    loop.run_until_complete(cf1())

    assert caplog.records[0].correlation_id == correlation_id


def test_set_multi(loop: asyncio.AbstractEventLoop, caplog):
    # TODO: add a negative test for running in a thread lacking a loop
    aiologfields.install()
    correlation_id = str(uuid4())
    logger = logging.getLogger('blah')

    async def cf2():
        logger.info('blah blah')

    async def cf1():
        aiologfields.set_fields(correlation_id=correlation_id, blah=12345)
        await cf2()

    loop.run_until_complete(cf1())

    assert caplog.records[0].correlation_id == correlation_id
    assert caplog.records[0].blah == 12345


def test_inner_task(loop: asyncio.AbstractEventLoop, caplog):
    aiologfields.install()
    correlation_id = str(uuid4())
    logger = logging.getLogger('blah2')

    async def cf2():
        logger.info('hey')

    async def cf1():
        ct = asyncio.Task.current_task()
        ct.logging_fields.correlation_id = correlation_id
        t = loop.create_task(cf2())
        await t

    loop.run_until_complete(cf1())

    assert caplog.records[0].correlation_id == correlation_id


def test_thread(loop: asyncio.AbstractEventLoop, caplog):
    """Verify that logging across thread boundaries still works."""
    aiologfields.install()
    correlation_id = str(uuid4())
    logger = logging.getLogger('blah2')

    def thread_func():
        logger.info('from thread')

    async def cf2():
        await loop.run_in_executor(None, thread_func)

    async def cf1():
        ct = asyncio.Task.current_task()
        ct.logging_fields.correlation_id = correlation_id
        t = loop.create_task(cf2())
        await t

    loop.run_until_complete(cf1())

    r = caplog.records[0]
    assert r.name == 'blah2'
    assert r.message == 'from thread'
    assert not hasattr(r, 'correlation_id')
