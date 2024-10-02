import os

from loguru import logger

from api.teams_message_sender import TeamsMessageSender
from api.toolset_mail_sender import ToolsetMailSender
from common.common import check_has_fail_case, get_datetime
from common.process_fail_case import process_fail_data


def get_log_path(env: str, project: str) -> str:
    file_datetime = get_datetime(type="datetime_s")
    log_path = f"./report/{project}/{env}/log/{file_datetime}.log"
    return log_path


def init_logger(log_path: str) -> None:
    logger.add(
        log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        encoding="utf-8",
    )


def run_pytest(log_path: str, env: str, project: str, worker: int = 1) -> None:
    logger.info(f"Starting {project} test on {env} site...")

    os.system(
        f"python3 -m pytest tests/{project}/ --env {env} -m {env} -n {worker} --cache-clear --alluredir=report/{project}/{env}/json >> {log_path} 2>&1"
    )

    logger.info("Test done!")


def run_allure(log_path: str, env: str, project: str) -> None:
    logger.info(f"Generating {env} site test report...")
    try:
        os.system(
            f"cp report/{project}/{env}/html/history/* report/{project}/{env}/json/history/ >> {log_path} 2>&1"
        )
        os.system(
            f"cp configurations/test/{project}_environment.properties report/{project}/{env}/json/environment.properties >> {log_path} 2>&1"
        )
        os.system(
            f"allure generate report/{project}/{env}/json -o report/{project}/{env}/html --clean >> {log_path} 2>&1"
        )
    except Exception as e:
        logger.error("Generate report error!")
        os.system(f"echo {e} >> {log_path}")
    else:
        logger.info("Generate report done!")
    # 建立 .gitkeep 回去 html 資料夾，避免被 git 追蹤到檔案遺失
    os.system(f"touch report/{project}/{env}/html/.gitkeep")


def run_failure_processor(
    log_path: str, env: str, project: str, test_result: dict
) -> None:
    if check_has_fail_case(data=test_result):
        logger.info(f"Process and insert fail case data to AWS DynamoDB and S3...")
        try:
            process_fail_data(project=project, env=env)
        except Exception as e:
            logger.error("Process and insert fail case data error!")
            os.system(f"echo {e} >> {log_path}")
        else:
            logger.info("Insert data to AWS done!")


def run_notify_sender(
    log_path: str,
    env: str,
    project: str,
    debug: str,
    test_result: dict,
    test_data_type: str = "api",
) -> None:
    logger.info(f"Sending test report to Teams...")
    try:
        teams_msg = TeamsMessageSender(
            project=project, env=env, debug=debug, test_data_type=test_data_type
        )
        teams_msg.set_content(data=test_result)
        teams_msg.send()
    except Exception as e:
        logger.error(f"Send message error!")
        os.system(f"echo {e} >> {log_path}")
    else:
        logger.info(f"Send message to Teams group done!")


def run_mail_sender(log_path: str, env: str, project: str, test_result: dict) -> None:
    logger.info(f"Sending email report...")
    try:
        mail = ToolsetMailSender()
        mail._set_content(data=test_result, project=project, env=env)
        mail._send_mail()
    except Exception as e:
        logger.error(f"Send email error!")
        os.system(f"echo {e} >> {log_path}")
    else:
        logger.info(f"Send email done!")


def run_update_report(env: str, project: str) -> None:
    logger.info(f"Moving test report to Web Server...")
    if not os.path.isdir(f"./web/report/{project}/{env}"):
        os.system(f"sudo mkdir -p ./web/report/{project}/{env}/")
    os.system(f"sudo rm -rf ./web/report/{project}/{env}/*")
    os.system(
        f"sudo cp -r ./report/{project}/{env}/html/* ./web/report/{project}/{env}/"
    )
    logger.info("Done!")
