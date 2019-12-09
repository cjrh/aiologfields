.. image:: https://github.com/cjrh/aiologfields/workflows/Python%20application/badge.svg
    :target: https://github.com/cjrh/aiologfields/actions

.. image:: https://coveralls.io/repos/github/cjrh/aiologfields/badge.svg?branch=master
    :target: https://coveralls.io/github/cjrh/aiologfields?branch=master

.. image:: https://img.shields.io/pypi/pyversions/aiologfields.svg
    :target: https://pypi.python.org/pypi/aiologfields

.. image:: https://img.shields.io/github/tag/cjrh/aiologfields.svg
    :target: https://img.shields.io/github/tag/cjrh/aiologfields.svg

.. image:: https://img.shields.io/badge/install-pip%20install%20aiologfields-ff69b4.svg
    :target: https://img.shields.io/badge/install-pip%20install%20aiologfields-ff69b4.svg

.. image:: https://img.shields.io/pypi/v/aiologfields.svg
    :target: https://img.shields.io/pypi/v/aiologfields.svg

.. image:: https://img.shields.io/badge/calver-YYYY.MM.MINOR-22bfda.svg
    :target: http://calver.org/

.. image:: https://pepy.tech/badge/aiologfields
    :alt: Downloads
    :target: https://pepy.tech/project/aiologfields

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: This project uses the "black" style formatter for Python code
    :target: https://github.com/python/black



aiologfields
======================

``aiologfields`` makes it easy to include **correlation IDs**, as well
as other contextual information into log messages, across ``await``
calls and ``loop.create_task()`` calls.  Correlation IDs are critically
important for accurate telemetry in monitoring and debugging distributed
microservices.

Instructions
------------

It couldn't be easier:

.. code-block:: python

    aiologfields.install()

After this, *every single task* created will have a ``logging_fields``
attribute. To add a field to a ``LogRecord``, simply apply it to any task:

.. code-block:: python

    t = loop.create_task(coro)
    t.logging_fields.correlation_id = '12345'

If you're using a logging handler that produces JSON output
(like ``logjson``!), or some other formatter that produces output with
all fields in the ``LogRecord``, you will find that each record within the
context of the task will include an additional field called ``correlation_id``
with a value of ``12345``.

Demo
----

This is adapted from one of the tests:

.. code-block:: python

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

In the ``LogRecord`` produced inside ``cf2()``, an additional field
``correlation_id`` is included, even though the field was set in
coroutine function ``cf1()``.

It would also have worked if ``cf2()`` had been executed in a separate
task itself, since the ``logging_fields`` namespace is copied between
nested tasks.
