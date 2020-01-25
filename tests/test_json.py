from datetime import datetime
from typing import Any

import pytest

import hypothesis.strategies as strategies
from hypothesis import given
from quart.app import Quart
from quart.json import dumps, htmlsafe_dumps
from quart.json.tag import TaggedJSONSerializer


def test_htmlsafe_dumps() -> None:
    script = htmlsafe_dumps("</script>")
    assert script != "</script>"
    assert script == '"</script>"'  # Has unicode characters
    escape = htmlsafe_dumps("&'")
    assert escape != "&'"
    assert escape == '"&\'"'  # Has unicode characters


@pytest.mark.parametrize("as_ascii, expected", [(True, '"\\ud83c\\udf8a"'), (False, '"🎊"')])
@pytest.mark.asyncio
async def test_ascii_dumps(as_ascii: bool, expected: str) -> None:
    app = Quart(__name__)
    async with app.app_context():
        app.config["JSON_AS_ASCII"] = as_ascii
        assert dumps("🎊") == expected


@given(
    value=strategies.one_of(
        strategies.datetimes(min_value=datetime(1900, 1, 1)),
        strategies.uuids(),
        strategies.binary(),
        strategies.tuples(strategies.integers()),
    )
)
def test_jsonserializer(value: Any) -> None:
    serializer = TaggedJSONSerializer()
    if isinstance(value, datetime):
        # The serializer is not precise to microseconds
        value = value.replace(microsecond=0)
    assert serializer.loads(serializer.dumps(value)) == value
