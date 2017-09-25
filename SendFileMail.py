#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import base64
import time
import sys
import os

if(len(sys.argv) < 2):
	print "脚本名：%s,缺少参数", sys.argv[0]
	sys.exit(1)  ##非正常退出

send_file = sys.argv

# 第三方 SMTP 服务
mail_host="smtp.mxhichina.com"  #设置服务器
mail_user=base64.decodestring("xxx") 
mail_pass= base64.decodestring("xxx") 
 
sender = 'xxx'
receivers = ['504299929@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

message = MIMEMultipart()
#message = MIMEText('Python ...', 'plain', 'utf-8')
message['From'] = Header(sender)
message['To'] =  Header(','.join(receivers))
 
curDate = time.strftime('%Y-%m-%d',time.localtime(time.time()))
subject = '[' + curDate + ']' + '文件'
message['Subject'] = Header(subject, 'gbk')

 
#邮件正文内容
message.attach(MIMEText('文件见附件', 'plain'))

# 构造附件1，传送当前目录下的 test.txt 文件
#att1 = MIMEText(open(send_file, 'rb').read(), 'base64', 'utf-8')
#att1["Content-Type"] = 'application/octet-stream'
# 这里的filename可以任意写，写什么名字，邮件中显示什么名字
#att1["Content-Disposition"] = 'attachment; filename='+ curDate + '.csv'
#message.attach(att1)
		
for index,value in enumerate(send_file):
    if(index == 0):
    		continue
    print index,value
    part = MIMEApplication(open(value,'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename="%s"%os.path.basename(value))
    message.attach(part) 
    
try:
    smtpObj = smtplib.SMTP_SSL(mail_host,465)
    #smtpObj.connect(mail_host, 25)
    smtpObj.login(mail_user,mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print "邮件发送成功"
except smtplib.SMTPException:
    print "Error: 无法发送邮件"
