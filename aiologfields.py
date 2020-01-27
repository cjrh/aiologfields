""" aiologfields: inject Task-context-fields into loggers

   Copyright 2017 Caleb Hattingh

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""


__version__ = '2019.12.1'


import asyncio
import logging
from types import SimpleNamespace
from copy import deepcopy
import sys
from contextlib import suppress


def get_current_task(*args, **kwargs):  # pragma: no cover
    if sys.version_info < (3, 7):
        return asyncio.Task.current_task(*args, **kwargs)
    else:
        return asyncio.current_task(*args, **kwargs)


def _record_factory_factory(loop, task_attr='logging_fields'):

    old_factory = logging.getLogRecordFactory()

    def _record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        try:
            t = get_current_task(loop=loop)
        except RuntimeError:
            pass  # No loop in this thread. Don't worry about it.
        else:
            if t and hasattr(t, task_attr):
                attr = getattr(t, task_attr)
                assert isinstance(attr, SimpleNamespace)
                for k, v in attr.__dict__.items():
                    setattr(record, k, v)

        return record

    return _record_factory


def set_log_record_factory_logging_fields(loop, task_attr: str = 'logging_fields'):
    """ Modify the default LogRecord factory so that we automatically
    insert Task-local logging fields into the LoggingRecords. """
    logging.setLogRecordFactory(_record_factory_factory(loop, task_attr=task_attr))


def _new_task_factory_factory(task_attr='logging_fields'):
    def _new_task_factory(loop, coro):
        """ Automatically add SimpleNamespace attribute to new task
        objects """
        t = asyncio.Task(coro, loop=loop)
        setattr(t, task_attr, SimpleNamespace())

        # If there are fields on the CURRENT task, copy them over to this
        # task.
        current_task = get_current_task(loop=loop)
        if current_task:
            current_attr = getattr(current_task, task_attr, None)
            if current_attr:
                # The NEW task's container
                attr = getattr(t, task_attr)
                attr.__dict__.update(
                    # Using a full copy to make sure that we don't
                    # inadvertently make objects live for longer than they
                    # should, i.e. create references that never go away.
                    deepcopy(current_attr.__dict__)
                )

        return t

    return _new_task_factory


def set_task_factory_logging_fields(loop, task_attr='logging_fields'):
    loop.set_task_factory(_new_task_factory_factory(task_attr))


def install(loop, task_attr='logging_fields'):
    """The factory function that produces LogRecord will get replaced
    by our one. But we don't want to do this more than once."""
    if hasattr(loop, "_logfields_installed"):
        return

    set_log_record_factory_logging_fields(loop)
    set_task_factory_logging_fields(loop)

    # If called within the context of an existing task, add the special
    # field to that one.
    with suppress(RuntimeError):
        pass
        t = get_current_task()
        if t and not hasattr(t, task_attr):
            setattr(t, task_attr, SimpleNamespace())

    loop._logfields_installed = True


def set_fields(task: asyncio.Task = None, task_attr='logging_fields', loop=None, **kwargs):
    """ This is a convenience function, whose main benefit is hiding the
    ``t`` reference to the task. Call it like this:

    .. code-block:: python

        aiologfields.set_fields(correlation_id=12345)

    - Raises RuntimeError if called with no loop in the current thread.
    - The new task factory should already have been set up, typically via
      ``aiologfields.install()``
    """
    t = task or get_current_task(loop=loop)
    if t and hasattr(t, task_attr):
        attr = getattr(t, task_attr)
        assert isinstance(attr, SimpleNamespace)
        for name, value in kwargs.items():
            setattr(attr, name, value)
