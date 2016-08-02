import os

import pytest
from mock import patch
from mock import MagicMock

from awseipext.aws_lambda.lambda_function import lambda_handler


class Context(object):
    aws_request_id = 'bogus aws_request_id'
    invoked_function_arn = 'bogus invoked_function_arn'


ASSOCIATE_TEST_REQUEST = {
    "action": "associate",
    "resource": "10.0.0.1",
    "instance_id": "i-12345",
    "username": "2/service/test-development-iad",
    "token": "faketoken"
}
DISASSOCIATE_TEST_REQUEST = {
    "action": "disassociate",
    "resource": "10.0.0.1",
    "instance_id": "i-12345",
    "username": "2/service/test-development-iad",
    "token": "faketoken"
}
INVALID_TEST_REQUEST = {
    "action": "invalid",
    "resource": "10.0.0.1",
    "instance_id": "i-12345",
    "username": "2/service/test-development-iad",
    "token": "faketoken"
}

GOOD_TOKEN = {'payload': 'test', 'key_alias': 'authnz'}

os.environ['AWS_REGION'] = 'us-west-2'


@patch(
    'awseipext.aws_lambda.lambda_function.get_role_name',
    MagicMock(return_value='test-development-iad')
)
@patch(
    'kmsauth.KMSTokenValidator.decrypt_token',
    MagicMock(return_value=GOOD_TOKEN)
)
@patch(
    'awseipext.aws_lambda.lambda_function.get_instance_id',
    MagicMock(return_value='i-12345')
)
def test_basic_associate_request_already_done():
    # Already associated
    ret = lambda_handler(
        ASSOCIATE_TEST_REQUEST, context=Context,
        config_file=os.path.join(
            os.path.dirname(__file__),
            'lambda-test.cfg'
        )
    )
    assert ret['result']


@patch(
    'awseipext.aws_lambda.lambda_function.get_role_name',
    MagicMock(return_value='test-development-iad')
)
@patch(
    'kmsauth.KMSTokenValidator.decrypt_token',
    MagicMock(return_value=GOOD_TOKEN)
)
@patch(
    'awseipext.aws_lambda.lambda_function.get_instance_id',
    MagicMock(return_value=None)
)
@patch(
    'awseipext.aws_lambda.lambda_function.ec2_client',
    MagicMock()
)
def test_basic_associate_request_to_associate():
    # Associated
    ret = lambda_handler(
        ASSOCIATE_TEST_REQUEST, context=Context,
        config_file=os.path.join(
            os.path.dirname(__file__),
            'lambda-test.cfg'
        )
    )
    assert ret['result']


@patch(
    'awseipext.aws_lambda.lambda_function.get_role_name',
    MagicMock(return_value='test-development-iad')
)
@patch(
    'kmsauth.KMSTokenValidator.decrypt_token',
    MagicMock(return_value=GOOD_TOKEN)
)
@patch(
    'awseipext.aws_lambda.lambda_function.get_instance_id',
    MagicMock(return_value='i-56790')
)
def test_invalid_associate_request():
    ret = lambda_handler(
        ASSOCIATE_TEST_REQUEST, context=Context,
        config_file=os.path.join(
            os.path.dirname(__file__),
            'lambda-test.cfg'
        )
    )
    assert not ret['result']
    assert ret['error'] == 'IP is already associated with another instance.'


@patch(
    'awseipext.aws_lambda.lambda_function.get_role_name',
    MagicMock(return_value='test-development-iad')
)
@patch(
    'kmsauth.KMSTokenValidator.decrypt_token',
    MagicMock(return_value=GOOD_TOKEN)
)
@patch(
    'awseipext.aws_lambda.lambda_function.get_instance_id',
    MagicMock(return_value=None)
)
@patch(
    'awseipext.aws_lambda.lambda_function.ec2_client',
    MagicMock()
)
def test_basic_disassociate_request_already_done():
    # Already disassociated
    ret = lambda_handler(
        DISASSOCIATE_TEST_REQUEST, context=Context,
        config_file=os.path.join(
            os.path.dirname(__file__),
            'lambda-test.cfg'
        )
    )
    assert ret['result']


@patch(
    'awseipext.aws_lambda.lambda_function.get_role_name',
    MagicMock(return_value='test-development-iad')
)
@patch(
    'kmsauth.KMSTokenValidator.decrypt_token',
    MagicMock(return_value=GOOD_TOKEN)
)
@patch(
    'awseipext.aws_lambda.lambda_function.get_instance_id',
    MagicMock(return_value='i-12345')
)
@patch(
    'awseipext.aws_lambda.lambda_function.ec2_client',
    MagicMock()
)
def test_basic_disassociate_request_disassociated():
    # Disassociated
    ret = lambda_handler(
        DISASSOCIATE_TEST_REQUEST, context=Context,
        config_file=os.path.join(
            os.path.dirname(__file__),
            'lambda-test.cfg'
        )
    )
    assert ret['result']


@patch(
    'awseipext.aws_lambda.lambda_function.get_role_name',
    MagicMock(return_value='test-development-iad')
)
@patch(
    'kmsauth.KMSTokenValidator.decrypt_token',
    MagicMock(return_value=GOOD_TOKEN)
)
@patch(
    'awseipext.aws_lambda.lambda_function.get_instance_id',
    MagicMock(return_value='i-56789')
)
@patch(
    'awseipext.aws_lambda.lambda_function.ec2_client',
    MagicMock()
)
def test_invalid_disassociate_request():
    ret = lambda_handler(
        DISASSOCIATE_TEST_REQUEST, context=Context,
        config_file=os.path.join(
            os.path.dirname(__file__),
            'lambda-test.cfg'
        )
    )
    assert not ret['result']
    assert ret['error'] == 'IP is not associated with this instance id.'


@patch(
    'awseipext.aws_lambda.lambda_function.get_role_name',
    MagicMock(return_value='test-development-iad')
)
@patch(
    'kmsauth.KMSTokenValidator.decrypt_token',
    MagicMock(return_value=GOOD_TOKEN)
)
@patch(
    'awseipext.aws_lambda.lambda_function.get_instance_id',
    MagicMock(return_value='i-12345')
)
@patch(
    'awseipext.aws_lambda.lambda_function.ec2_client',
    MagicMock()
)
def test_invalid_action_request():
    ret = lambda_handler(
        INVALID_TEST_REQUEST, context=Context,
        config_file=os.path.join(
            os.path.dirname(__file__),
            'lambda-test.cfg'
        )
    )
    assert not ret['result']
    assert ret['error'] == 'invalid is not a valid action.'


def test_local_request_config_not_found():
    with pytest.raises(ValueError):
        lambda_handler(
            ASSOCIATE_TEST_REQUEST, context=Context,
            config_file=os.path.join(os.path.dirname(__file__), 'none')
        )


@patch(
    'awseipext.aws_lambda.lambda_function.get_role_name',
    MagicMock(return_value='test-development-iad')
)
@patch(
    'kmsauth.KMSTokenValidator.extract_username_field',
    MagicMock(return_value='invalid-development-iad')
)
@patch(
    'kmsauth.KMSTokenValidator.decrypt_token',
    MagicMock(return_value=GOOD_TOKEN)
)
def test_invalid_from_request():
    ret = lambda_handler(
        ASSOCIATE_TEST_REQUEST, context=Context,
        config_file=os.path.join(
            os.path.dirname(__file__),
            'lambda-test.cfg'
        )
    )
    assert not ret['result']
    msg = ('Instance is not in role (test-development-iad) associated'
           ' with kms token (2/service/test-development-iad).')
    assert ret['error'] == msg
