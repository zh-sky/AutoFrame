import configparser
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from Common import logger


class Mail:
    """
    发送邮件 邮件相关配置从配置文件读取
    """
    def __init__(self, path):
        config = configparser.ConfigParser()
        config.read(path)
        mail_config = config['Mail']
        # 邮件信息
        self.mail_info = {}
        # 发件人
        self.mail_info['from'] = mail_config['mail']
        self.mail_info['user'] = mail_config['mail']
        # 服务器域名
        self.mail_info['host'] = 'SMTP.' + mail_config['mail'][mail_config['mail'].find('@')+1:]
        # 发件人的密码
        self.mail_info['password'] = mail_config['pwd']
        # 收件人
        self.mail_info['to'] = str(mail_config['mailto']).split(',')
        # 抄送人
        self.mail_info['cc'] = str(mail_config['mailcopy']).split(',')
        # 邮件标题
        self.mail_info['mail_subject'] = mail_config['mailtitle']
        self.mail_info['mail_encoding'] = mail_config['mail_encoding']
        # 附件内容
        self.mail_info['filepaths'] = []
        self.mail_info['filenames'] = []

    def send(self, text):
        # SMTP_SSL默认使用465端口，如果发送失败，可以使用587
        print(self.mail_info['host'])
        smtp = SMTP_SSL(self.mail_info['host'], port=587)
        # 发送邮件时根据设置的等级打印日志
        smtp.set_debuglevel(0)

        ''' SMTP 'ehlo' command.
        Hostname to send for this command defaults to the FQDN of the local
        host.
        '''
        smtp.ehlo(self.mail_info['host'])
        smtp.login(self.mail_info['user'], self.mail_info['password'])


        # 普通HTML邮件
        # msg = MIMEText(text, 'html', self.mail_info['mail_encoding'])

        # 支持附件的邮件
        msg = MIMEMultipart()
        msg.attach(MIMEText(text, 'html', self.mail_info['mail_encoding']))
        msg['Subject'] = Header(self.mail_info['mail_subject'], self.mail_info['mail_encoding'])
        msg['from'] = self.mail_info['from']

        logger.debug(self.mail_info)
        # logger.debug(text)
        msg['to'] = ','.join(self.mail_info['to'])
        msg['cc'] = ','.join(self.mail_info['cc'])
        receive = self.mail_info['to']
        receive += self.mail_info['cc']

        # 添加附件
        # for i in range(len(self.mail_info['filepaths'])):
        #     att1 = MIMEText(open(self.mail_info['filepaths'][i], 'rb').read(), 'base64', 'utf-8')
        #     att1['Content-Type'] = 'application/octet-stream'
        #     att1['Content-Disposition'] = 'attachment; filename= "'+self.mail_info['filenames'][i]+'"'
        #     msg.attach(att1)
        #
        try:
            smtp.sendmail(self.mail_info['from'], receive, msg.as_string())
            smtp.quit()
            logger.info('邮件发送成功')
        except Exception as e:
            logger.error('邮件发送失败：')
            logger.exception(e)

if __name__ == '__main__':
    mail = Mail()
