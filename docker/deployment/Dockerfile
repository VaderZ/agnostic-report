FROM node:18 as ui

ADD /agnostic-web-ui /opt/deploy/agnostic-web-ui

RUN cd /opt/deploy/agnostic-web-ui && npm install && npm run build

FROM python:3.11.4 as fat

ADD /agnostic-core /opt/deploy/agnostic-core
ADD /agnostic-web /opt/deploy/agnostic-web
COPY --from=ui /opt/deploy/agnostic-web-ui/dist /opt/deploy/agnostic-web/src/agnostic/web/ui

RUN python3 -m pip install -U pip
RUN cd /opt/deploy && pip install ./agnostic-web
RUN rm -rf /opt/deploy

FROM fat as slim

ENV AGNOSTIC_PRODUCTION=True
ENV AGNOSTIC_WEB_HOST=0.0.0.0
ENV AGNOSTIC_WEB_PORT=8000

ENTRYPOINT uvicorn agnostic.web.api:app --host $AGNOSTIC_WEB_HOST --port $AGNOSTIC_WEB_PORT
