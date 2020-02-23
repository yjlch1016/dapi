FROM ubuntu:18.04
# 基础镜像

MAINTAINER yangjianliang <526861348@qq.com>
# 作者

RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
# 设置apt源为阿里云源

RUN apt-get clean && \
    apt-get update && \
    apt-get upgrade -y
# 检查软件包并升级

RUN apt-get install -y \
	git \
	python3 && \
	apt-get update && \
	apt-get install -y \
	python3-dev \
	python3-setuptools && \
	apt-get update && \
	apt-get install -y \
	python3-pip && \
	apt-get update && \
	apt-get install -y \
	nginx \
	supervisor &&\
	apt-get update && \
	ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
	apt-get install -y \
	tzdata && \
	rm -rf /var/lib/apt/lists/*
# 安装软件

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY deploy_conf/nginx-app.conf /etc/nginx/sites-available/default
COPY deploy_conf/supervisor-app.conf /etc/supervisor/conf.d/
COPY deploy_conf/pip.conf /root/.pip/pip.conf
# 复制配置文件

RUN pip3 install https://codeload.github.com/sshwsfc/xadmin/zip/django2
COPY requirements.txt /django/dapi/
RUN pip3 install -r /django/dapi/requirements.txt
# 安装Python依赖库

COPY . /django/dapi/
RUN sed -i '35,36d' /usr/local/lib/python3.6/dist-packages/django/db/backends/mysql/base.py && \
sed -i '145,146d' /usr/local/lib/python3.6/dist-packages/django/db/backends/mysql/operations.py && \
sed -i '93d' /usr/local/lib/python3.6/dist-packages/django/forms/boundfield.py
# 复制其余代码并修改Django源码

EXPOSE 80
# 暴露80端口

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisor-app.conf"]
# 启动supervisor并加载配置文件
