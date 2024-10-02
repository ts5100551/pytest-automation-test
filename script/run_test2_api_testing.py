import os
import sys

from dotenv import load_dotenv

o_path = os.getcwd()
sys.path.append(o_path)

from common.common import get_test_result
from common.run_file_action import *

load_dotenv()
DEBUG = os.getenv("debug")  # use env variables - debug
PROJECT = "Test2API"
ENV = str(sys.argv[1])


def main():
    # Get log path
    log_path = get_log_path(env=ENV, project=PROJECT)

    # Initialize logger
    init_logger(log_path=log_path)

    # Run pytest testing
    run_pytest(log_path=log_path, env=ENV, project=PROJECT)

    # Generate Allure report
    run_allure(log_path=log_path, env=ENV, project=PROJECT)

    # Get test results
    test_result = get_test_result(project=PROJECT, env=ENV)

    # Process and insert fail case data to AWS DynamoDB and S3
    run_failure_processor(
        log_path=log_path, env=ENV, project=PROJECT, test_result=test_result
    )

    # Send message to Teams group
    run_notify_sender(
        log_path=log_path,
        env=ENV,
        project=PROJECT,
        debug=DEBUG,
        test_result=test_result,
    )

    # Send email report
    run_mail_sender(
        log_path=log_path, env=ENV, project=PROJECT, test_result=test_result
    )

    # Update report file of navbar
    run_update_report(env=ENV, project=PROJECT)


if __name__ == "__main__":
    main()
