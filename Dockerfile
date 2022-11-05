FROM python:3.9 as requirements-stage

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir nb-cli && \
    pip install --no-cache-dir -r /tmp/requirements.txt
RUN nb plugin install nonebot_plugin_apscheduler && \
    nb plugin install nonebot_plugin_gocqhttp && \
    nb driver install websockets

WORKDIR /app

ENTRYPOINT ["nb", "run"]
