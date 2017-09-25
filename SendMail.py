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
	print "脚本名：%s,缺少参数"%sys.argv[0]
	sys.exit(1)  ##非正常退出

send_msg = sys.argv[1]

# 第三方 SMTP 服务
mail_host="smtp.mxhichina.com"  #设置服务器
mail_user=base64.decodestring("xxxx") 
mail_pass= base64.decodestring("xxxx") 
 
sender = 'xxxx'
receivers = ['xxxx']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

message = MIMEText(send_msg, 'html','gbk')
#message = MIMEText('Python ...', 'plain', 'utf-8')
message['From'] = Header(sender)
message['To'] =  Header(','.join(receivers))
 
curDate = time.strftime('%Y-%m-%d',time.localtime(time.time()))
subject = '[' + curDate + ']' + '系统磁盘统计'
message['Subject'] = Header(subject, 'gbk')
    
try:
    smtpObj = smtplib.SMTP_SSL(mail_host,465)
    smtpObj.login(mail_user,mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print "邮件发送成功"
except smtplib.SMTPException:
    print "Error: 无法发送邮件"
