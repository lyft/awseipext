⚠️ This repository has been archived and is no longer accepting contributions ⚠️

# awseipext

AWS Lambda that extends the EC2 Elastic IP API

## Configure

First make a lambda\_configs directory:

```bash
mkdir ./lambda_configs
```

Next, add a lambda\_configs/lambda\_deploy.cfg file:

```ini
[lambda_config]
# KMS auth key to use
kmsauth_key = awseipext-production
# The 'to' context for kmsauth
kmsauth_to_context = awseipext-production
```

## Build zip

To build the zip file for publishing:

```bash
make publish
```

This will write the zip file into:

```
./publish/awseipext_lambda.zip
```

## Development

To install the virtualenv and run tests:

```bash
make develop
make test
```

## TODO

This lambda doesn't require any binary dependencies at this point, so it's
possible to use a virtualenv from basically anywhere, but it's a lot saner to
use a docker image like [docker lambda](https://github.com/lambci/docker-lambda)
to build this instead.
