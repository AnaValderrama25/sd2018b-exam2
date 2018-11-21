FROM python:3.6

COPY . /endpoint

WORKDIR /endpoint

RUN pip3.6 install connexion[swagger-ui]
RUN pip3.6 install --trusted-host pypi.python.org  -r requirements.txt

CMD ./deploy.sh
