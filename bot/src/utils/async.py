import asyncio

from .logging import logger

def run_async(*futures):
    tasks = asyncio.gather(
        *map(asyncio.ensure_future, futures),
        return_exceptions=True
    )

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(tasks)
    except KeyboardInterrupt:
        logger.warning('Shutting down...')
    finally:
        logger.warning('MAIN EVEN LOOP STOPPED')
        exit()
        cancel_tasks(loop)
        loop.close()


def cancel_tasks(loop):
    all_tasks = asyncio.gather(*asyncio.Task.all_tasks())
    all_tasks.cancel()

    # should stop right away as all tasks are cancelled
    loop.run_forever()

    exception = all_tasks.exception()
    if exception.args:
        logger.warn(
            'Got the following exception after cancelling all tasks:\n{}'
            .format(exception)
        )
