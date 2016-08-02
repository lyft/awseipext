import logging
import json
import argparse
import sys

import boto3
import kmsauth


class AwseipextClient(object):
    """A class that represents a awseipext client."""

    def __init__(
            self,
            function_name,
            kmsauth_key,
            from_context,
            to_context,
            user_type_context
            ):
        """Create an AwseipextClient object."""
        self.function_name = function_name
        self.kmsauth_key = kmsauth_key
        self.from_context = from_context
        self.to_context = to_context
        self.user_type_context = user_type_context

    def _get_generator(self, action, resource):
        generator = kmsauth.KMSTokenGenerator(
            # KMS key to use for authentication to the lambda
            self.kmsauth_key,
            # Encryption context to use
            {
                # We're authenticating to this service
                'to': self.to_context,
                # It's from this IAM role
                'from': self.from_context,
                # This token is for a service
                'user_type': self.user_type_context,
                # This is an association action
                'action': action,
                'resource': resource
            },
            # Find the KMS key in this region
            'us-east-1'
        )
        return generator

    def associate(self, resource, instance_id):
        generator = self._get_generator('associate', resource)
        username = generator.get_username()
        token = generator.get_token()
        payload = {
            'action': 'associate',
            'resource': resource,
            'instance_id': instance_id,
            'username': username,
            'token': token
        }
        payload_json = json.dumps(payload)
        client = boto3.client('lambda')
        response = client.invoke(
            FunctionName=self.function_name,
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=payload_json
        )
        return response['Payload'].read()

    def disassociate(self, resource, instance_id):
        generator = self._get_generator('disassociate', resource)
        username = generator.get_username()
        token = generator.get_token()
        payload = {
            'action': 'disassociate',
            'resource': resource,
            'instance_id': instance_id,
            'username': username,
            'token': token
        }
        payload_json = json.dumps(payload)
        client = boto3.client('lambda')
        response = client.invoke(
            FunctionName=self.function_name,
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=payload_json
        )
        return response['Payload'].read()


def main():
    """Entrypoint function for confidant cli."""
    parser = argparse.ArgumentParser(
        description='A client for associating and disassociating EIPs.'
    )

    parser.add_argument(
        '--action',
        choices=['associate', 'disassociate'],
        required=True,
        help='Action to take (associate or disassociate).'
    )
    parser.add_argument(
        '--resource',
        required=True,
        help='IP address to associate or disassociate.'
    )
    parser.add_argument(
        '--instance-id',
        required=True,
        help='Instance ID to target.'
    )
    parser.add_argument(
        '--function-name',
        required=True,
        help='lambda function name to call.'
    )
    parser.add_argument(
        '--to',
        required=True,
        dest='_to',
        help='"to" kmsauth context.'
    )
    parser.add_argument(
        '--from',
        required=True,
        dest='_from',
        help='"from" kmsauthcontext.'
    )
    parser.add_argument(
        '--user-type',
        help='"user_type" context. Default: service',
        default='service'
    )
    parser.add_argument(
        '--kmsauth-key',
        required=True,
        help='KMS key to use for auth.'
    )
    parser.add_argument(
        '--log-level',
        help='Logging verbosity.',
        default='info'
    )
    args = parser.parse_args()

    numeric_loglevel = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_loglevel, int):
        raise ValueError('Invalid log level: {0}'.format(args.loglevel))
    logging.basicConfig(
        level=numeric_loglevel,
        format='%(asctime)s %(name)s: %(levelname)s %(message)s',
        stream=sys.stderr
    )

    client = AwseipextClient(
        args.function_name,
        args.kmsauth_key,
        args._from,
        args._to,
        args.user_type
    )
    if args.action == 'associate':
        print client.associate(args.resource, args.instance_id)
    elif args.action == 'disassociate':
        print client.disassociate(args.resource, args.instance_id)


if __name__ == '__main__':
    main()
