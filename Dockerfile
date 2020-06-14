FROM registry.cn-hangzhou.aliyuncs.com/yangjianliang/django_xadmin:0.0.1
# 基础镜像

COPY deploy_conf/nginx-app.conf /etc/nginx/sites-available/default
COPY deploy_conf/supervisor-app.conf /etc/supervisor/conf.d/
# 复制配置文件

COPY . /django/dapi/
# 拷贝代码
RUN pip3 install -r /django/dapi/requirements.txt
# 安装Python第三方依赖库

RUN sed -i '38,40c <h4 align="center">轻量级测试平台</h4><p align="center"><img src="http://attach.sogi.com.tw/upload/200611/200611101824320.gif" alt="雷达"></p>' /usr/local/lib/python3.6/dist-packages/xadmin/templates/xadmin/views/login.html && \
    sed -i '30,31c <style type="text/css">table {table-layout: inherit;}td {white-space: nowrap;overflow: hidden;text-overflow: ellipsis;}</style>' /usr/local/lib/python3.6/dist-packages/xadmin/templates/xadmin/base.html && \
    sed -i '35,36d' /usr/local/lib/python3.6/dist-packages/django/db/backends/mysql/base.py && \
    sed -i '145,146d' /usr/local/lib/python3.6/dist-packages/django/db/backends/mysql/operations.py && \
    sed -i '93d' /usr/local/lib/python3.6/dist-packages/django/forms/boundfield.py
# 修改Django源码

RUN mkdir /django/dapi/media/
# 创建/django/dapi/media目录

EXPOSE 80
# 暴露80端口

ENTRYPOINT ["supervisord", "-c", "/etc/supervisor/conf.d/supervisor-app.conf"]
# 启动supervisor并加载配置文件
