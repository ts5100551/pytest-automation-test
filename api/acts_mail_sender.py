import os
from datetime import datetime
from email.mime.text import MIMEText

import pandas as pd

from api.base_mail_sender import BaseMailSender
from common.convert import env_convert_for_mail


class ActsMailSender(BaseMailSender):

    def __init__(self) -> None:
        super().__init__()


    def _count_test_cases(self, project: str, env: str) -> int:
        df = pd.read_excel(f'testdata/env-{env}/{project}_TestData.xlsx')
        df = df.dropna(how='all')
        api_list = []
        for i in df['case_id'].values:
            api_list.append(i)
        count = len(set(api_list))

        return count


    def _set_content(self, data: dict, project: str, env: str) -> None:
        start_time = datetime.fromtimestamp(data['time']['start'] / 1000.0, tz=self._tz).strftime('%Y/%m/%d %H:%M:%S')
        end_time = datetime.fromtimestamp(data['time']['stop'] / 1000.0, tz=self._tz).strftime('%Y/%m/%d %H:%M:%S')
        cost_time = f"{data['time']['duration'] / 1000.0:.2f}"
        count_cases = self._count_test_cases(project=project, env=env)
        site = env_convert_for_mail(project=project, env=env)

        if (data['statistic']['failed'] != 0 or data['statistic']['broken'] != 0 or data['statistic']['unknown'] != 0):
            subject_test_result = 'FAIL'
            result_string_color = '#FF0000'
        else:
            subject_test_result = 'PASS'
            result_string_color = '#32CD32'

        count_total = data["statistic"]["total"]
        count_pass = data["statistic"]["passed"]
        count_fail = int(data["statistic"]["failed"]) + int(data["statistic"]["broken"])
        count_skip = data["statistic"]["skipped"]

        content = ''

        content += f'<p>Hi all,</p>'
        content += f'<p>ACTS User Case Test Result for <font color="#1E90FF"><b>{site} {project}</b></font>: <font color="{result_string_color}"><b>{subject_test_result}</b></font></p>'
        content += f'<p><font color="#1E90FF"><b>Total test user cases:</b></font> {count_cases} </p>'
        content += f'<p>'
        content += f'<font color="#1E90FF"><b>Total cases:</b></font> {count_total} '
        content += f' &nbsp;&nbsp;&nbsp;&nbsp; <font color="#32CD32"><b>PASS:</b></font> {count_pass} '
        content += f' &nbsp;&nbsp;&nbsp;&nbsp; <font color="#FF0000"><b>FAIL:</b></font> {count_fail} '
        content += f' &nbsp;&nbsp;&nbsp;&nbsp; <font color="#F9A825"><b>SKIP:</b></font> {count_skip} '
        content += f'</p>'
        content += f'<p><font color="#1E90FF"><b>Testing Cost Time:</b></font> {cost_time} sec.</p>'
        content += f'<p><font color="#1E90FF"><b>Testing Duration:</b></font> {start_time} ~ {end_time}</p>'
        content += f'<p><font color="#47B0A6"><b>Testing Report:</b></font> <a target="_blank" href="http://{os.getenv('web_host')}/{project}/{env}/index.html">Allure Test Report</a></p>'
        content += f'<p>Thanks!</p>'


        self._mail.attach(MIMEText(_text=content, _subtype='html', _charset='utf-8'))
        self._mail['Subject'] = f'[{project}][Test Report][{site}][{subject_test_result}] ACTS Automation Testing - {self._today}'
