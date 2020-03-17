FROM python:3.7-alpine

# 使用清华镜像源
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories

WORKDIR /root

COPY . .

# 设置默认环境变量
ENV SEMESTER_START=2020-2-24 PORT=3000

RUN apk add --no-cache gcc musl-dev libxml2-dev libxslt-dev \
    && cp info.example.py info.py \
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 清理库和缓存
RUN apk del --no-cache gcc musl-dev libxml2-dev libxslt-dev \
    && rm -rf /tmp/* /var/cache/apk/*

ENTRYPOINT [ "python", "server.py" ]