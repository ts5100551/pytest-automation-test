import os
import smtplib
from datetime import date, timedelta, timezone
from email.mime.multipart import MIMEMultipart


class BaseMailSender:

    def __init__(self) -> None:
        # 設定寄件人、密碼、時區、日期等變數
        self._acc = os.getenv("mail_acc")
        self._password = os.getenv("mail_password")
        self._tz = timezone(timedelta(hours=+8))
        self._today = str(date.today()).replace("-", "/")

        # 設定 SMTP 伺服器相關變數
        self._host_server = "smtp-mail.outlook.com"
        self._port = 587

        # 設定信件內容相關變數
        self._mail = MIMEMultipart()
        self._mail["From"] = self._acc
        self._mail["To"] = os.getenv("mail_to")

    def _send_mail(self) -> None:
        try:
            # 連接 SMTP 伺服器、登入並發送信件
            server = smtplib.SMTP(host=self._host_server, port=self._port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user=self._acc, password=self._password)
            server.send_message(msg=self._mail)
            server.close()
        except Exception as e:
            # 若有例外發生則 raise Exception
            raise Exception(e)
