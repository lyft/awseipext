"""
.. module: awseipext.request.lambda_request
    :copyright: (c) 2016 by Lyft Inc.
    :license: Apache, see LICENSE for more details.
"""
from marshmallow import Schema, fields, post_load


class LambdaSchema(Schema):
    action = fields.Str()
    resource = fields.Str()
    instance_id = fields.Str()
    username = fields.Str()
    token = fields.Str()

    @post_load
    def make_lambda_request(self, data):
        return LambdaRequest(**data)


class LambdaRequest:
    def __init__(self, action, resource, instance_id, username, token):
        """
        A LambdaRequest must have the following key value pairs to be valid.
        :param action: The eip action to take.
        :param resource: The eip resource to manage.
        :param username: The KMS auth username.
        :param kmsauth_token: The KMS auth token.
        """
        self.action = action
        self.resource = resource
        self.instance_id = instance_id
        self.username = username
        self.token = token

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
