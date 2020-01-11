import enum
from collections import defaultdict, Counter
from typing import NamedTuple, Dict, Callable, Optional, Iterable, Tuple, Union, List

from contextlib import asynccontextmanager
from asyncio import BoundedSemaphore

from aiohttp import ClientSession, TCPConnector, web
from xcat.oob import create_app


class Encoding(enum.Enum):
    URL = 'url'
    FORM = 'form'


class Injection(NamedTuple):
    name: str
    example: str
    test_template_payloads: Iterable[Tuple[str, bool]]
    payload: Union[str, Callable[[str, str], str]]

    def __call__(self, working, expression) -> str:
        if callable(self.payload):
            return self.payload(working, expression)
        return self.payload.format(working=working, expression=expression)

    def test_payloads(self, working_value) -> List[Tuple[str, bool]]:
        return [
            (template.format(working=working_value), expected_result)
            for template, expected_result in self.test_template_payloads
        ]


class AttackContext(NamedTuple):
    url: str
    method: str
    target_parameter: str
    parameters: Dict[str, str]
    match_function: Callable[[int, str], bool]
    concurrency: int
    fast_mode: bool
    body: Optional[bytes]
    headers: Dict[str, str]
    encoding: Encoding
    oob_details: str
    tamper_function: Callable[[], None]

    session: ClientSession = None
    features: Dict[str, bool] = defaultdict(bool)
    common_strings = Counter()
    common_characters = Counter()
    injection: Injection = None
    # Limiting aiohttp concurrency at the TCPConnector level seems to not work
    # and leads to weird deadlocks. Use a semaphore here.
    semaphore: BoundedSemaphore = None
    oob_host: str = None
    oob_app: web.Application = None

    @asynccontextmanager
    async def start(self, injection: Injection = None) -> 'AttackContext':
        if self.session:
            raise RuntimeError('already has a session')

        semaphore = BoundedSemaphore(self.concurrency)
        connector = TCPConnector(ssl=False, limit=None)
        async with ClientSession(headers=self.headers, connector=connector) as sesh:
            yield self._replace(session=sesh, injection=injection, semaphore=semaphore)

    @asynccontextmanager
    async def start_oob_server(self) -> 'AttackContext':
        if self.oob_app:
            raise RuntimeError('OOB server has already been started')

        host, port = self.oob_details.split(':', 1)

        app = create_app()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', int(port))
        await site.start()

        new_ctx = self._replace(oob_host=f'http://{host}:{port}', oob_app=app)

        try:
            yield new_ctx
        finally:
            await runner.cleanup()

    @asynccontextmanager
    async def null_context(self) -> 'AttackContext':
        yield self

    @property
    def target_parameter_value(self):
        return self.parameters[self.target_parameter]


async def check(context: AttackContext, payload: str):
    if not context.session:
        raise ValueError('AttackContext has no session. Use start()')

    parameters = context.parameters.copy()
    if context.injection:
        payload = context.injection(context.target_parameter_value, payload)
    parameters[context.target_parameter] = str(payload)
    if context.encoding == Encoding.URL:
        args = {'params': parameters, 'data': context.body}
    else:
        args = {'data': parameters}
    if context.tamper_function:
        context.tamper_function(context, args)

    async with context.semaphore:
        async with context.session.request(context.method, context.url, **args) as resp:
            body = await resp.text()
            return context.match_function(resp.status, body)
