FROM python:2
MAINTAINER Igor Scabini <furester@gmail.com>

WORKDIR /application

COPY requirements.txt /application/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /application
RUN python setup.py install

RUN pip install -e .

CMD [ "/usr/local/bin/pimp" ]
