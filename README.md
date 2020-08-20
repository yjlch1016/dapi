# dapi  
基于Django的轻量级接口测试平台  
dapi：即Django+API测试的缩写  
QQ群：529063263  
[部署文档](https://www.cnblogs.com/yjlch1016/category/1653648.html)  


***
# PyCharm图片  
![pycharm图片](https://github.com/yjlch1016/dapi/blob/master/static/img/pycharm.png)  


***
# 设计思想  
1、 模拟性能测试工具JMeter的思路，实现接口测试与性能测试的Web化；  
2、 计划有产品模块、接口测试用例模块、性能测试用例模块、任务队列模块、测试报告模块等；  
3、 前期采用Django+Bootstrap前后端不分离的模式实现功能，后期再严格按照RESTful的风格来编程。  


***
# 模型  
6张表   
产品线信息表一对多模块信息表  
用例组信息表一对多用例信息表  
压测信息表一对多压测结果表  

|  表  | 字段  |
|  ----  |  ----  |
| 产品线信息表 | 产品线名称、产品描述、产品经理、开发人员、测试人员、创建时间、修改时间 |
| 模块信息表 | 外键、模块名称、模块描述、创建时间、修改时间 |
| 用例组信息表 | 用例组名称、用例组描述、创建时间、修改时间 |
| 用例信息表 | 外键、用例名称、接口地址、请求方式、请求参数、请求头、请求体类型、请求体、预期结果、响应断言方式、等待时间、正则、变量名、模板、响应代码、实际结果、是否通过、创建时间、修改时间 |
| 压测信息表 | 脚本简介、相对路径、请求数、持续时间、创建时间、修改时间 |
| 压测结果表 | 外键、测试报告、jtl文件、Dashboard Report、运行时间 |


***
# 本地调试  
`python manage.py collectstatic`  
复制xadmin静态文件  

`python manage.py makemigrations`  
激活模型  

`python manage.py migrate`  
迁移  

`python manage.py createsuperuser`  
创建超级管理员账号  
输入账号：admin  
输入邮箱：123456789@qq.com  
输入密码：test123456  
二次确认  

`python manage.py runserver`  
启动服务 

后台  
http://127.0.0.1:8000/admin/  
用户名：admin  
密码：test123456

前台  
http://127.0.0.1:8000  
用户名：admin  
密码：test123456


***
# 本地打包  
`docker build -t dapi .`  
dapi为镜像名称，随便取  

`docker run -d --name dapi2020 -p 80:80 mock:latest`  
启动容器  
后台运行  
给容器取个别名dapi2020  
映射80端口  

后台  
http://x.x.x.x/admin/  
宿主机的IP地址  
账号：admin  
密码：test123456  

前台  
http://x.x.x.x/  
宿主机的IP地址  
账号：admin  
密码：test123456

`docker exec -it dapi2020 /bin/bash`  
进入容器内部

`exit`  
退出容器内部

`docker stop dapi2020`  
停止容器  

`docker rm dapi2020`  
删除容器  


***
# API  
http://127.0.0.1:8000/api/  
http://127.0.0.1:8000/redoc/  
http://127.0.0.1:8000/swagger/  
