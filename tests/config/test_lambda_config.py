import os

import pytest

from awseipext.config.lambda_config import LambdaConfig


def test_empty_config():
    with pytest.raises(ValueError):
        LambdaConfig(config_file='')


def test_config_no_section():
    with pytest.raises(ValueError) as e:
        LambdaConfig(
            os.path.join(os.path.dirname(__file__), 'empty.cfg')
        )
    assert 'Missing lambda_config configuration section.' == e.value.message


def test_config_no_kmsauth_options():
    with pytest.raises(ValueError) as e:
        LambdaConfig(
            os.path.join(os.path.dirname(__file__), 'missing-1.cfg')
        )
    assert 'kmsauth_key not set.' == e.value.message

    with pytest.raises(ValueError) as e:
        LambdaConfig(
            os.path.join(os.path.dirname(__file__), 'missing-2.cfg')
        )
    assert 'kmsauth_to_context not set.' == e.value.message
