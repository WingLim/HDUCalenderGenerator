FROM python:3.7-alpine

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories

WORKDIR /root

COPY . .

ENV SEMESTER_START=2020-2-24 PORT=9898

RUN apk add --no-cache gcc musl-dev libxml2-dev libxslt-dev \
    && cp info.example.py info.py \
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ENTRYPOINT [ "python", "server.py" ]