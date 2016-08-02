FROM ubuntu:trusty
RUN apt-get update && \
    apt-get install -y curl python-minimal git make wget zip && \
    curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | python && \
    pip install pip==8.1.1 && \
    pip install --no-cache-dir virtualenv==15.0.1 && \
    apt-get autoremove -y && \
    apt-get clean
RUN mkdir -p /srv/lambda
RUN cd /srv/lambda && virtualenv venv
COPY setup.py /code/awseipext/setup.py
RUN mkdir -p /code/awseipext/awseipext
COPY awseipext/__about__.py /code/awseipext/awseipext/__about__.py
RUN /srv/lambda/venv/bin/pip install -U pip
RUN /srv/lambda/venv/bin/pip install -e file:///code/awseipext
RUN /srv/lambda/venv/bin/pip install "file:///code/awseipext/setup.py#egg=awseipext[tests]"
COPY . /code/awseipext
WORKDIR /code/awseipext
