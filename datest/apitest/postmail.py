"""
@project: PyCharm
@author: MZM
@file: postmail.py
@ide: PyCharm
@time: 2021/4/2 10:34
@desc： 
"""

# !/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

from django.conf import settings
from django.urls import reverse


def postmail(host,sender,receiver,reportobj):
    sender = sender
    receiver = receiver  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    mail_msg = f'''
        <h1><center><font>以下是自动发送的邮件，请勿回复！</font><center></h1>
    <br>
    测试批次：{reportobj.testbatch.name}<br>
    测试时间：{reportobj.testtime}<br>
     用例数量：{reportobj.testnum}<br>
     成功用例数量：{reportobj.suc}<br>
     失败用例数量：{reportobj.fail}<br>
     运行结果: {reportobj.result}<br>
     测试报告：<A HREF="{host}{reportobj.file.url}">点击查看</a><br>
     <hr>
        '''
    message = MIMEText(mail_msg, 'html', 'utf-8')
    message['From'] = formataddr([sender,sender])
    message['To'] = formataddr([receiver,receiver])
    message['Subject'] = Header(reportobj.reportname, 'utf-8')

    try:
        server=smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(sender, 'snybyslezwoabbbd')
        server.sendmail(sender,[receiver,],message.as_string())
        server.quit()
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")

# if __name__ == "__main__":
#     subject = '自动化测试报告'
#     sender = '605662545@qq.com'
#     receiver = '605662545@qq.com'
#
#     postmail(subject, sender, receiver, mail_msg)