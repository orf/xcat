import asyncio

from lib.features.xpath_version import XPathVersionFeature

@asyncio.coroutine
def detect_version(future):
    yield from asyncio.sleep(1)
    future.set_result(True)


loop = asyncio.get_event_loop()

future = asyncio.Future()
asyncio.Task(detect_version(future))
loop.run_until_complete(future)
print(future.result())
loop.close()