FROM python:3.6

COPY . /handler_endpoint

WORKDIR /handler_endpoint

RUN pip3.6 install connexion[swagger-ui]
RUN pip3.6 install --trusted-host pypi.python.org

CMD ./deploy.sh
