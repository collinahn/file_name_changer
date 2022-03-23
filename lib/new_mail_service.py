# 이메일 발송 클래스

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from lib.log_gongik import Logger
from lib.json_parser import ValueParser

CREDENTIALS = "__classified/private.json"

class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SendNewMail(metaclass=MetaSingleton):

    def __init__(self) -> None:
        self.log = Logger()

        self.session = smtplib.SMTP('smtp.gmail.com', 587)
        self.session.starttls()

        self.gmail_id = ValueParser(CREDENTIALS, "gmail_id")
        gmail_pw = ValueParser(CREDENTIALS, "gmail_app_pw")

        self.mail_content: MIMEMultipart = MIMEMultipart('alternative')

        try:
            self.session.login(self.gmail_id.value, gmail_pw.value)
        except smtplib.SMTPAuthenticationError as se:
            self.log.ERROR(se, '/ login failure, init fail')

    def __del__(self) -> None:
        if self.session:
            self.session.close()

    def create_mail(self, *, title: str = None, plain_text: str = None, html_contents: str = None) -> MIMEMultipart:
        if not title:
            title = "제목 없는 메일"
        if not plain_text:
            plain_text = "이 메일은 본문이 없습니다."
        if not html_contents:
            html_contents = plain_text

        html_contents = f"""
        <!DOCTYPE html>
        <html lang="kor">
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
            </head>
            <body>
                {html_contents}
            </body>
        </html>"""

        mail_content: MIMEMultipart = MIMEMultipart('alternative')
        mail_content["Subject"] = f'[GongikNC] {title}'
        mail_content.attach(MIMEText(html_contents, "html"))

        return mail_content

    def send_mail(self, content: MIMEMultipart, receiver: str, bcc: list):
        if not self.session:
            self.log.ERROR("cannot send email - session lost")
            self.__init__()
        if not bcc:
            bcc = []

        content["To"] = receiver
        allocatee = [receiver] + bcc if receiver else bcc

        try:
            self.session.sendmail(self.gmail_id.value, allocatee,
                                  content.as_string())
            self.log.INFO(f"email sent to {allocatee}, title: {content.get('Subject', '오류')}")
        except Exception as e:
            self.log.CRITICAL(f"Cannot Send Email / {e}")


class SendMail2Subscribers(SendNewMail):
    def __init__(self) -> None:
        super().__init__()

    def create_mail(self, *, title: str = None, plain_text: str = None, html_contents: str = None) -> MIMEMultipart:
        return super().create_mail(title=title, plain_text=plain_text, html_contents=html_contents)

    def send_mail(self, content: MIMEMultipart, receivers: str=None, bcc: list=None):
        return super().send_mail(content, receivers, bcc)


class SendMail2Admin(SendNewMail):
    def __init__(self) -> None:
        super().__init__()

        self.admin_id = ValueParser(CREDENTIALS, "admin_gmail_id")

    def create_mail(self, *, title: str = None, plain_text: str = None, html_contents: str = None) -> MIMEMultipart:
        return super().create_mail(title=title, plain_text=plain_text, html_contents=html_contents)

    def send_mail(self, content: MIMEMultipart, receivers: str=None, bcc: list=None):
        return super().send_mail(content, self.admin_id.value, bcc)


if __name__ == '__main__':

    a= SendMail2Subscribers()
    b= SendMail2Subscribers()
    c= SendMail2Admin()
    d= SendMail2Admin()

    content = a.create_mail(
        title='알림',
        plain_text='테스트용 메일입니다'
    )
    b.send_mail(content, '', ['collinahn@kakao.com'])
    c.send_mail(c.create_mail(
        title='일반',
        plain_text='테스트입니다'
    ))