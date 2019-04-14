# -*- coding:utf-8 -*-
__author__ = 'Administrator'
import os
import configparser

configPath = "./config"
fileName = "config.ini"
filePathName = "./config"+"/"+fileName
# 写入默认配置
defaultConfig = \
'''
[email]
sender = sender@sina.com
password = xxx
receiver = receiver@qq.com
smtp = smtp.sina.com
port = 465
[mysql]
host = 138.68.41.40
user = xxx
password = xxx
database = eastmoney
port = 3306
charset = utf8
[sms]
appid = 1400009099
appkey = 9ff91d87c2cd7cd0ea762f141975d1df37481d48700d70ac37470aefc60f9bad
phone_number = 12345678
template_id = 7839
sign = 腾讯云
'''
#判断路径是否存在，没有就新建
if os.path.isdir(configPath) == False :
    os.mkdir(configPath)
#判断配置文件是否存在，没有就新建
if os.path.exists(filePathName) == False:
    with open(filePathName, "w+") as f:
        f.write(defaultConfig)
# 获取config.ini的路径
cf = configparser.ConfigParser()
# print("filePathName:",filePathName)
cf.read(filePathName,encoding="utf-8")
emailSender = cf.get("email", "sender")  # 发信人邮箱地址
emailPassword = cf.get("email", "password")  # 发信人邮箱密码
emailReceiver = cf.get("email", "receiver")  # 收信人地址
emailSmtp = cf.get("email", "smtp")  # 发信人smtp服务器地址 比如smtp.sina.com
emailPort = cf.getint("email", "port")  # 发信邮箱登录端口 ssl对应465 这里使用465
mysqlHost = cf.get("mysql", "host")  # mysql 主机IP地址
mysqlUser = cf.get("mysql", "user")  # mysql 用户名
mysqlPassword = cf.get("mysql","password")  # mysql 密码
mysqlDatabase = cf.get("mysql","database")  # mysql 数据库名
mysqlPort = cf.getint("mysql","port")  # mysql 端口号 默认3306
mysqlCharset = cf.get("mysql","charset")  # mysql 编解码方式 默认utf8
sms_appid = cf.get("sms","appid")  # 短信应用SDK AppID
sms_appkey = cf.get("sms","appkey")  # 短信应用SDK AppKey
sms_phone_number = cf.get("sms","phone_number")  # 需要发送短信的手机号码
sms_template_id  = cf.get("sms","template_id")  # 短信模板ID，需要在短信应用中申请
sms_sign = cf.get("sms","sign")  # 签名
