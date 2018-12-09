import re
import urllib.request
from typing import Callable, Tuple

import click

from .features import features


def get_ip():
    with urllib.request.urlopen('https://api.ipify.org') as content:
        return re.search(r'[0-9]+(?:\.[0-9]+){3}', str(content.read())).group(0)


class FeatureChoice(click.types.StringParamType):
    def convert(self, value, param, ctx):
        value = super().convert(value, param, ctx)
        feature_names = {feature.name for feature in features}
        given_names = set(value.split(','))
        unknown_features = given_names - feature_names
        if unknown_features:
            self.fail(f'Unknown features: {", ".join(unknown_features)}.')
        return given_names


class EnumType(click.Choice):
    def __init__(self, enum):
        self._enum = enum
        super().__init__(enum.__members__)

    def convert(self, value, param, ctx):
        if isinstance(value, self._enum):
            return value
        value = value.upper()
        return self._enum[super().convert(value, param, ctx)]


class HeaderFile(click.File):
    def __init__(self):
        super().__init__(mode='r')

    def convert(self, value, param, ctx):
        open_file = super().convert(value, param, ctx)

        # ToDO: replace this with the new aiohttp header parser
        #  https://github.com/aio-libs/aiohttp/blob/15857de31e57574be595ac3fda673852eef64b63/aiohttp/http_parser.py#L76

        with open_file as fd:
            lines = (line.strip() for line in open_file)
            headers = {}
            for line in lines:
                if not line:
                    continue
                try:
                    key, value = line.split(':', 1)
                except ValueError:
                    self.fail(f'Not a valid header line: {line}')

                headers[key] = value.strip()

            return headers


class DictParameters(click.ParamType):
    def convert(self, value, param, ctx):
        try:
            key, value = value.split('=', 1)
        except ValueError:
            self.fail(f'Argument "{value}" must be in a key=value format')

        return key, value


class Negatable(click.ParamType):
    def convert(self, value, param, ctx):
        negate = False
        if value.startswith('!'):
            negate = True
            value = value[1:]

        return negate, self.validate(value)

    def validate(self, value):
        raise NotImplementedError()


class NegatableInt(Negatable):
    name = 'str'

    def validate(self, value):
        try:
            return int(value)
        except ValueError:
            self.fail(f'{value} is not an integer.')


class NegatableString(Negatable):
    name = 'str'

    def validate(self, value):
        return value


def make_match_function(true_code: Tuple[bool, int], true_string: Tuple[bool, str]) -> Callable[[int, str], bool]:
    def check_code(response_code: int):
        if true_code is None:
            return True

        negate_code, expected_code = true_code
        if negate_code:
            return response_code != expected_code

        return response_code == expected_code

    def check_content(content: str):
        if true_string is None:
            return True

        negate_string, expected_string = true_string
        if negate_string:
            return expected_string not in content

        return expected_string in content

    return lambda code, content: check_code(code) and check_content(content)
