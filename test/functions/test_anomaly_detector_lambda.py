import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Set dummy environment variables for the test environment
os.environ.setdefault('DYNAMODB_EVENTS_TABLE', 'dummy')
os.environ.setdefault('DYNAMODB_RULES_TABLE', 'dummy')
os.environ.setdefault('SNS_TOPIC_NAME', 'dummy')

# Import the functions to be tested and mock AWS services
from src.functions.anomaly_detector.lambda_function import lambda_handler, check_anomaly, send_alert

# Mock boto3 and botocore to prevent actual AWS calls
sys.modules['boto3'] = MagicMock()
sys.modules['botocore'] = MagicMock()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

class TestAnomalyDetectorLambda(unittest.TestCase):
    """
    Test suite for the Anomaly Detector Lambda function.

    This suite contains unit tests for the main `lambda_handler` function and its
    helper functions `check_anomaly` and `send_alert`. It uses a mocked AWS environment
    to test the logic without making real API calls.
    """
    def setUp(self):
        """
        Set up the test environment before each test.

        Initializes a mock context object that mimics the AWS Lambda context.
        """
        self.mock_context = MagicMock()
        self.mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:anomaly-detector"

    @patch('src.functions.anomaly_detector.lambda_function.rules_table')
    @patch('src.functions.anomaly_detector.lambda_function.check_anomaly')
    def test_lambda_handler_with_rules(self, mock_check, mock_rules_table):
        """
        Test the main handler when rules are present.

        This test verifies that the `lambda_handler` correctly scans for rules
        and calls `check_anomaly` for each rule found. It asserts that the
        function returns a 200 status code and calls the helper function as expected.
        """
        mock_rules_table.scan.return_value = {'Items': [{'ruleId': '1', 'ruleType': 'count-based', 'metric': 'RunInstances', 'threshold': 1, 'timeWindow': 5, 'target': 'user123'}]}
        mock_check.return_value = None
        event = {}
        response = lambda_handler(event, self.mock_context)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Analysis complete', response['body'])
        mock_check.assert_called_once()

    @patch('src.functions.anomaly_detector.lambda_function.rules_table')
    def test_lambda_handler_no_rules(self, mock_rules_table):
        """
        Test the main handler when no rules are found.

        Verifies that if the rules table scan returns no items, the handler
        exits gracefully and returns a None response.
        """
        mock_rules_table.scan.return_value = {'Items': []}
        event = {}
        response = lambda_handler(event, self.mock_context)
        self.assertIsNone(response)

    @patch('src.functions.anomaly_detector.lambda_function.rules_table')
    def test_lambda_handler_exception(self, mock_rules_table):
        """
        Test the main handler when an exception occurs during rule scanning.

        Ensures that the function handles exceptions gracefully and exits
        without crashing if it fails to scan the rules table.
        """
        mock_rules_table.scan.side_effect = Exception('DB error')
        event = {}
        response = lambda_handler(event, self.mock_context)
        self.assertIsNone(response)

    @patch('src.functions.anomaly_detector.lambda_function.events_table')
    @patch('src.functions.anomaly_detector.lambda_function.send_alert')
    def test_check_anomaly_count_based(self, mock_send_alert, mock_events_table):
        """
        Test anomaly detection with a count-based rule.

        This test simulates a scenario where the number of events exceeds the
        rule's threshold. It verifies that `check_anomaly` correctly identifies
        the anomaly and calls the `send_alert` function.
        """
        rule = {
            'ruleId': '1',
            'ruleType': 'count-based',
            'metric': 'RunInstances',
            'threshold': 1,
            'timeWindow': 5,
            'target': 'user123',
            'ruleName': 'Test Rule'
        }
        mock_events_table.scan.return_value = {'Items': [{'eventName': 'RunInstances'}, {'eventName': 'RunInstances'}]}
        
        mock_send_alert_function = MagicMock()
        check_anomaly(rule, mock_send_alert_function)
        
        mock_send_alert_function.assert_called_once()

    @patch('src.functions.anomaly_detector.lambda_function.sns')
    def test_send_alert_success(self, mock_sns):
        """
        Test successful alert publishing.

        Verifies that the `send_alert` function correctly calls the SNS
        `publish` method with the right topic ARN, message, and subject.
        """
        mock_sns.publish.return_value = None
        send_alert('Test message', 'us-east-1', '123456789012')
        mock_sns.publish.assert_called_once_with(
            TopicArn='arn:aws:sns:us-east-1:123456789012:dummy',
            Message='Test message',
            Subject='Cloud Resource Anomaly Detected!'
        )

    @patch('src.functions.anomaly_detector.lambda_function.sns')
    def test_send_alert_exception(self, mock_sns):
        """
        Test exception handling during alert publishing.

        Ensures that the `send_alert` function handles publication errors
        gracefully without raising an unhandled exception.
        """
        mock_sns.publish.side_effect = Exception('SNS error')
        send_alert('Test message', 'us-east-1', '123456789012')
        # The test passes if no exception is raised.
        
if __name__ == '__main__':
    unittest.main()