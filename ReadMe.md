#windows平台安装环境
----
*[anoconda(python3)](https://www.anaconda.com/download/)
下载安装包并安装。
*python3
创作一个新的环境：打开cmd工具，输入指令:
```dos
conda create -n python3 python=3.6 anaconda
```
面对是否继续的提示，输入回车或者y，继续安装
```dos
Proceed ([y]/n)?
```
激活这个环境
```dos
activate python3
```
[更多信息](https://conda.io/docs/user-guide/tasks/manage-python.html)
*scarpy
使用pip安装:
```dos
pip install Scrapy
```
[更多信息](https://scrapy-chs.readthedocs.io/zh_CN/0.24/intro/install.html)
*安装Mysql数据库
下载[Mysql数据库服务端](https://dev.mysql.com/downloads/mysql/),[安装](http://www.cnblogs.com/pengyan5945/p/9863721.html)。
*配置Mysql数据库：
导入数据库eastmoney.sql，可以使用[SQLyog工具](https://sqlyog.en.softonic.com/)快捷导入数据库。不过这个是个付费工具。

#配置文件
----
文件名：config.ini
配置内容：
[email]
sender = 发送者的邮箱 ，比如xxxx@sina.com
password = 发送邮箱的密码，xxxx
receiver = 接收邮件的邮箱比如 xx@qq.com
smtp = 发送邮箱的smtp服务器，比如smtp.sina.com
port = 发送邮箱登录端口，默认465
[mysql]
host = mysql数据库主机地址，比如 127.0.0.1
user = 数据库用户名，比如admin
password = 数据库密码，比如xxx
database = 数据库名称，本例为eastmoney
port = 数据库端口，默认3306
charset = 数据库字体集，默认utf8
#文件结构
----
─┬─mySpider─┬─figure
 │			├─config──config.ini #配置mysql，email等信息
 │			├─spiders─┬─__init__.py 
 │			│		  └─easymoney.py 
 │			├─__init__.py
 │			├─Configure.py #读取配置文件
 │			├─eastmoney.sql #数据库结构文件
 │			├─FundTactics.py #分析基金数据
 │			├─items.py
 │			├─middlewares.py
 │			├─ParseOfflineHtml.py #解析html文件，抽取数据
 │			├─pipelines.py
 │			└─settings.py #爬虫配置文件
 ├─ReadMe.md #本文档
 └─scrapy.cfg #爬虫配置文件

#执行命令
----
cd mySpider
scrapy crawl easymoney 