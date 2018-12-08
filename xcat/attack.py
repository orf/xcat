import enum
from collections import defaultdict, Counter
from typing import NamedTuple, Dict, Callable, Optional, Iterable, Tuple, Union, List
from aiohttp import ClientSession, TCPConnector
import copy
from contextlib import asynccontextmanager


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
    session: ClientSession = None
    features: Dict[str, bool] = defaultdict(bool)
    common_strings = Counter()
    common_characters = Counter()
    injection: Injection = None

    @asynccontextmanager
    async def start(self, injection: Injection = None) -> 'AttackContext':
        if self.session:
            yield self.session
            return

        connector = TCPConnector(ssl=False, limit=self.concurrency)
        async with ClientSession(headers=self.headers, connector=connector) as sesh:
            new_ctx = copy.deepcopy(self)
            yield new_ctx._replace(session=sesh, injection=injection)

    @property
    def target_parameter_value(self):
        return self.parameters[self.target_parameter]


async def check(context: AttackContext, payload: str):
    if not context.session:
        raise ValueError('AttackContext has no session. Use with_session()')

    parameters = context.parameters.copy()
    if context.injection:
        payload = context.injection(context.target_parameter_value, payload)
    parameters[context.target_parameter] = str(payload)
    if context.encoding == Encoding.URL:
        args = {'params': parameters, 'data': context.body}
    else:
        args = {'data': parameters}

    async with context.session.request(context.method, context.url, **args) as resp:
        body = await resp.text()
        return context.match_function(resp.status, body)
