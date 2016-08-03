test: lint
	@echo "--> Running Python tests"
	./venv/bin/py.test tests || exit 1
	@echo ""

develop:
	@echo "--> Installing dependencies"
	virtualenv venv
	./venv/bin/pip install -e .
	./venv/bin/pip install "file://`pwd`#egg=awseipext[tests]"
	@echo ""

dev-docs:
	# todo the docs, so typical, right?

clean:
	@echo "--> Cleaning pyc files"
	find . -name "*.pyc" -delete
	rm -rf ./publish ./htmlcov ./awseipext.egg-info ./venv
	@echo ""

lint:
	@echo "--> Linting Python files"
	PYFLAKES_NODOCTEST=1 ./venv/bin/flake8 awseipext
	@echo ""

coverage:
	./venv/bin/coverage run --branch --source=awseipext -m py.test tests
	./venv/bin/coverage html

publish: clean develop
	# Ensure directory exists
	mkdir -p ./publish/awseipext_lambda
	# Copy in libs
	cp -r ./venv/lib/python2.7/site-packages/. ./publish/awseipext_lambda/
	# Copy in module code
	cp -r ./awseipext ./publish/awseipext_lambda/
	mv ./publish/awseipext_lambda/awseipext/aws_lambda/* ./publish/awseipext_lambda/
	# Copy in config
	cp -r ./lambda_configs/. ./publish/awseipext_lambda/
	# Zip it
	cd ./publish/awseipext_lambda && zip -q -r ../awseipext_lambda.zip .

.PHONY: develop dev-docs clean test lint coverage publsh
