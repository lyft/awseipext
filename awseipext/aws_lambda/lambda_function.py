"""
.. module: awseipext.aws_lambda.lambda_function
    :copyright: (c) 2016 by Lyft Inc.
    :license: Apache, see LICENSE for more details.
"""
import logging

import boto3
import botocore
import kmsauth
import os
from awseipext.config.lambda_config import LambdaConfig, SECTION
from awseipext.request.lambda_request import LambdaSchema

ec2_resource = boto3.resource('ec2')
ec2_client = boto3.client('ec2')
logger = None


def get_role_name(instance_id):
    instance = ec2_resource.Instance(instance_id)
    try:
        role = instance.iam_instance_profile['Arn'].split('/')[1]
    except botocore.exceptions.ClientError:
        logger.exception('Could not find instance {0}.'.format(instance_id))
        role = None
    except IndexError:
        logger.error(
            'Could not find the role associated with {0}.'.format(instance_id)
        )
        role = None
    except Exception:
        logger.exception(
            'Failed to lookup role for instance id {0}.'.format(instance_id)
        )
        role = None
    return role


def get_instance_id(resource):
    addr = ec2_resource.ClassicAddress(resource)
    try:
        instance_id = addr.instance_id
    except botocore.exceptions.ClientError:
        logger.exception('Could not lookup ip {0}.'.format(resource))
        instance_id = None
    return instance_id


def get_allocation_id(resource):
    try:
        addrs = ec2_client.describe_addresses(PublicIps=[resource])
        addr = addrs['Addresses'][0]
        allocation_id = addr['AllocationId']
    except botocore.exceptions.ClientError:
        logger.exception('Could not lookup ip {0}.'.format(resource))
        allocation_id = None
    return allocation_id


def get_association_id(resource):
    try:
        addrs = ec2_client.describe_addresses(PublicIps=[resource])
        addr = addrs['Addresses'][0]
        association_id = addr['AssociationId']
    except botocore.exceptions.ClientError:
        logger.exception('Could not lookup ip {0}.'.format(resource))
        association_id = None
    return association_id


def lambda_handler(
        event, context=None,
        config_file=os.path.join(
            os.path.dirname(__file__),
            'lambda_deploy.cfg'
        )
        ):
    """
    This is the function that will be called when the lambda function starts.
    :param event: Dictionary of the json request.
    :param context: AWS LambdaContext Object
    http://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
    :param config_file: The config file to load additional settings.
    :return: A dict with success or error information.
    """
    global logger

    # AWS Region determines configs related to KMS
    region = os.environ['AWS_REGION']

    # Load the deployment config values
    config = LambdaConfig(config_file=config_file)
    kmsauth_key = config.get(SECTION, 'kmsauth_key')
    kmsauth_user_key = config.get(SECTION, 'kmsauth_user_key')
    kmsauth_to_context = config.get(SECTION, 'kmsauth_to_context')

    logging_level = config.get(SECTION, 'logging_level_option')
    numeric_level = getattr(logging, logging_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}'.format(logging_level))

    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Process request
    schema = LambdaSchema(strict=True)
    request = schema.load(event).data

    # Authenticate the user with KMS, if key is setup
    extra_context = {
        'action': request.action,
        'resource': request.resource
    }
    validator = kmsauth.KMSTokenValidator(
        kmsauth_key,
        kmsauth_user_key,
        kmsauth_to_context,
        region,
        extra_context=extra_context
    )
    try:
        # decrypt_token will raise a TokenValidationError if token
        # doesn't match
        validator.decrypt_token(request.username, request.token)
    except kmsauth.TokenValidationError:
        logger.error(
            'KMS auth info: {0} {1} {2} {3} {4}'.format(
                kmsauth_key,
                kmsauth_user_key,
                kmsauth_to_context,
                region,
                extra_context
            )
        )
        return {
            'result': False,
            'error': 'Authentication failed.'
        }

    role = get_role_name(request.instance_id)
    if role is None:
        return {
            'result': False,
            'error': 'Could not find instance id.'
        }
    if role != validator.extract_username_field(request.username, 'from'):
        msg = 'Instance is not in role ({0}) associated with kms token ({1}).'
        msg = msg.format(
            role,
            request.username
        )
        logger.error(msg)
        return {
            'result': False,
            'error': msg
        }

    instance_id = get_instance_id(request.resource)
    if request.action == 'associate':
        if instance_id:
            if instance_id == request.instance_id:
                logger.info(
                    'IP already associated with {0}.'.format(
                        request.instance_id
                    )
                )
                return {'result': True}
            else:
                return {
                    'result': False,
                    'error': 'IP is already associated with another instance.'
                }
        allocation_id = get_allocation_id(request.resource)
        if allocation_id is None:
            return {
                'result': False,
                'error': 'Could not get allocation id for IP.'
            }
        logger.info(
            'associating {0} to {1}.'.format(
                request.resource,
                request.instance_id
            )
        )
        try:
            ec2_client.associate_address(
                InstanceId=request.instance_id,
                AllocationId=allocation_id
            )
        except botocore.exceptions.ClientError:
            msg = 'Failed to associate IP address with instance.'
            logger.exception(msg)
            return {
                'result': False,
                'error': msg
            }
    elif request.action == 'disassociate':
        if instance_id:
            if instance_id != request.instance_id:
                return {
                    'result': False,
                    'error': 'IP is not associated with this instance id.'
                }
            association_id = get_association_id(request.resource)
            if association_id is None:
                return {
                    'result': False,
                    'error': 'Could not get association id for IP.'
                }
            logger.info(
                'disassociating {0} from {1}.'.format(
                    request.resource,
                    request.instance_id
                )
            )
            try:
                ec2_client.disassociate_address(
                    AssociationId=association_id
                )
            except botocore.exceptions.ClientError:
                msg = 'Failed to disassociate IP address from instance.'
                logger.exception(msg)
                return {
                    'result': False,
                    'error': msg
                }
        else:
            logger.info(
                'No IP associated with {0}.'.format(request.instance_id)
            )
            return {'result': True}
    else:
        return {
            'result': False,
            'error': '{0} is not a valid action.'.format(request.action)
        }
    return {
        'result': True
    }
