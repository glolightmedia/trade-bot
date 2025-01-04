import os
import logging
from datetime import datetime


class ErrorReporter:
    """
    Class for summarizing errors and generating daily error reports.
    """

    def __init__(self, log_dir="data/logs", report_file="daily_error_report.txt"):
        """
        Initialize the error reporter.
        :param log_dir: Directory where logs are stored.
        :param report_file: File name for the error report.
        """
        self.log_dir = log_dir
        self.report_file = os.path.join(log_dir, report_file)
        os.makedirs(log_dir, exist_ok=True)

    def summarize_errors(self):
        """
        Summarizes errors from the error log and writes a report.
        """
        error_log_path = os.path.join(self.log_dir, "errors.log")
        if not os.path.exists(error_log_path):
            logging.warning("No error log found to summarize.")
            return

        summary = {}
        try:
            with open(error_log_path, "r") as error_log:
                for line in error_log:
                    if "ERROR" in line:
                        error_type = line.split(":")[0]
                        summary[error_type] = summary.get(error_type, 0) + 1

            self.write_report(summary)
        except Exception as e:
            logging.error(f"Failed to summarize errors: {e}")

    def write_report(self, summary):
        """
        Writes a summary report of the errors.
        :param summary: Dictionary with error types and their counts.
        """
        try:
            with open(self.report_file, "w") as report:
                report.write(f"Daily Error Report - {datetime.now().strftime('%Y-%m-%d')}\n")
                report.write("=" * 40 + "\n")
                for error_type, count in summary.items():
                    report.write(f"{error_type}: {count} occurrences\n")
                report.write("=" * 40 + "\n")
            logging.info(f"Error report written to {self.report_file}")
        except Exception as e:
            logging.error(f"Failed to write error report: {e}")
    
    def email_report(self, email_address):
        """
        Placeholder for emailing the error report to an administrator.
        :param email_address: Email address to send the report.
        """
        # Add email logic (e.g., using smtplib or an external service)
        logging.info(f"Error report sent to {email_address} (placeholder implementation).")


if __name__ == "__main__":
    reporter = ErrorReporter()
    reporter.summarize_errors()
    print(f"Daily error report written to {reporter.report_file}")
