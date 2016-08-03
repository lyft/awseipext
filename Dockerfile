FROM ubuntu:trusty
WORKDIR /code/awseipext
RUN apt-get update && \
    apt-get install -y curl python-minimal git make wget zip && \
    curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | python && \
    pip install pip==8.1.1 && \
    pip install --no-cache-dir virtualenv==15.0.1 && \
    apt-get autoremove -y && \
    apt-get clean
RUN virtualenv venv
COPY setup.py /code/awseipext/setup.py
RUN mkdir -p /code/awseipext/awseipext
COPY awseipext/__about__.py /code/awseipext/awseipext/__about__.py
COPY Makefile /code/awseipext/Makefile
RUN make develop
COPY . /code/awseipext
