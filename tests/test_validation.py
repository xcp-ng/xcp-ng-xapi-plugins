import re

import pytest

from xcpngutils import validate_arg


def test_validate_arg_allowlist():
    assert validate_arg('a', 'service', allowed={'a', 'b'}) == 'a'
    with pytest.raises(ValueError):
        validate_arg('sshd', 'service', allowed={'a', 'b'})


def test_validate_arg_pattern_and_optional():
    pattern = re.compile(r'^[a-z]+\Z')
    assert validate_arg('abc', 'name', pattern=pattern) == 'abc'
    assert validate_arg(None, 'name', pattern=pattern, optional=True) is None
    with pytest.raises(ValueError):
        validate_arg(None, 'name', pattern=pattern)
    with pytest.raises(ValueError):
        validate_arg('123', 'name', pattern=pattern)
