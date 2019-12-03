from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr, make_msgid

import smtplib

from_addr = 'nvwa@3songshu.com'
password = 'Songshu619'
smtp_url = 'smtp.3songshu.com'
pop_url = 'pop3.3songshu.com'


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send(subject, body, to, cc=None):
     msg_id = make_msgid()
     msg = MIMEText(body, 'plain', 'utf-8')
     msg['From'] = _format_addr('女娲<%s>' % from_addr)
     msg['To'] = ','.join(to)
     msg['Subject'] = Header(subject, 'utf-8').encode()
     if cc:
         msg['Cc'] = _format_addr(cc)
         to += cc

     msg['Message-ID'] = msg_id

     server = smtplib.SMTP(smtp_url, 25)
     server.set_debuglevel(1)
     server.login(from_addr, password)
     server.sendmail(from_addr, to, msg.as_string())
     server.quit()
     return msg_id



if __name__ == '__main__':
    print(send('测试邮件', '来自女娲的测试邮件6', ['n_sdhan@3songshu.com', 'n_sdman@3songshu.com']))

    # print(','.join(['2', '3']))


