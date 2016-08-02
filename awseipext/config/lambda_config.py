"""
.. module: awseipext.config.lambda_config
    :copyright: (c) 2016 by Lyft Inc.
    :license: Apache, see LICENSE for more details.
"""
import ConfigParser

SECTION = 'lambda_config'


class LambdaConfig(ConfigParser.RawConfigParser):
    def __init__(self, config_file):
        """
        Parses the lambda config file.

        The [lambda_config] section is required.

        :param config_file: Path to the config file.
        """
        defaults = {'kmsauth_user_key': None, 'logging_level_option': 'INFO'}
        ConfigParser.RawConfigParser.__init__(self, defaults=defaults)
        self.read(config_file)

        if not self.has_section(SECTION):
            raise ValueError(
                "Missing {0} configuration section.".format(SECTION)
            )

        for option in ['kmsauth_key', 'kmsauth_to_context']:
            if not self.has_option(SECTION, option):
                raise ValueError("{0} not set.".format(option))
