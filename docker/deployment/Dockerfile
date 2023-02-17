FROM node:14 as ui

ADD /src/agnostic_report/ui /opt/deploy/ui

RUN cd /opt/deploy/ui && npm install && npm run build

FROM python:3.11.1 as fat

ADD / /opt/deploy
COPY --from=ui /opt/deploy/ui/dist /opt/deploy/src/agnostic_report/ui/dist

RUN python3 -m pip install -U pip
RUN cd /opt/deploy && pip install .
RUN rm -rf /opt/deploy

FROM fat as slim

ENV AGNOSTIC_PRODUCTION=True
ENV AGNOSTIC_WEB_HOST=0.0.0.0
ENV AGNOSTIC_WEB_PORT=8000

ENTRYPOINT uvicorn agnostic_report:app --host $AGNOSTIC_WEB_HOST --port $AGNOSTIC_WEB_PORT
