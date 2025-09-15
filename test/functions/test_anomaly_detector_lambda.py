import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Set environment variables.
os.environ.setdefault('DYNAMODB_EVENTS_TABLE', 'dummy')
os.environ.setdefault('DYNAMODB_RULES_TABLE', 'dummy')
os.environ.setdefault('SNS_TOPIC_NAME', 'dummy')

# Import the functions after setting environment variables.
from src.functions.anomaly_detector.lambda_function import lambda_handler, check_anomaly, send_alert

# Mock boto3 and its dependencies.
sys.modules['boto3'] = MagicMock()
sys.modules['botocore'] = MagicMock()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

class TestAnomalyDetectorLambda(unittest.TestCase):
    # Create a mock context object to simulate Lambda execution.
    def setUp(self):
        self.mock_context = MagicMock()
        self.mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:anomaly-detector"

    @patch('src.functions.anomaly_detector.lambda_function.rules_table')
    @patch('src.functions.anomaly_detector.lambda_function.check_anomaly')
    def test_lambda_handler_with_rules(self, mock_check, mock_rules_table):
        mock_rules_table.scan.return_value = {'Items': [{'ruleId': '1', 'ruleType': 'count-based', 'metric': 'RunInstances', 'threshold': 1, 'timeWindow': 5, 'target': 'user123'}]}
        mock_check.return_value = None
        event = {}
        response = lambda_handler(event, self.mock_context)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Analysis complete', response['body'])
        mock_check.assert_called_once()

    @patch('src.functions.anomaly_detector.lambda_function.rules_table')
    def test_lambda_handler_no_rules(self, mock_rules_table):
        mock_rules_table.scan.return_value = {'Items': []}
        event = {}
        response = lambda_handler(event, self.mock_context)
        self.assertIsNone(response)

    @patch('src.functions.anomaly_detector.lambda_function.rules_table')
    def test_lambda_handler_exception(self, mock_rules_table):
        mock_rules_table.scan.side_effect = Exception('DB error')
        event = {}
        response = lambda_handler(event, self.mock_context)
        self.assertIsNone(response)

    @patch('src.functions.anomaly_detector.lambda_function.events_table')
    @patch('src.functions.anomaly_detector.lambda_function.send_alert')
    def test_check_anomaly_count_based(self, mock_send_alert, mock_events_table):
        rule = {
            'ruleId': '1',
            'ruleType': 'count-based',
            'metric': 'RunInstances',
            'threshold': 1,
            'timeWindow': 5,
            'target': 'user123',
            'ruleName': 'Test Rule'
        }
        # The original code uses `scan`, so the mock should be for `scan`, not `query`.
        mock_events_table.scan.return_value = {'Items': [{'eventName': 'RunInstances'}, {'eventName': 'RunInstances'}]}
        
        mock_send_alert_function = MagicMock()
        check_anomaly(rule, mock_send_alert_function)
        
        # Now this assertion will pass because the mock provides events that meet the threshold.
        mock_send_alert_function.assert_called_once()

    @patch('src.functions.anomaly_detector.lambda_function.sns')
    def test_send_alert_success(self, mock_sns):
        mock_sns.publish.return_value = None
        send_alert('Test message', 'us-east-1', '123456789012')
        mock_sns.publish.assert_called_once_with(
            TopicArn='arn:aws:sns:us-east-1:123456789012:dummy',
            Message='Test message',
            Subject='Cloud Resource Anomaly Detected!'
        )

    @patch('src.functions.anomaly_detector.lambda_function.sns')
    def test_send_alert_exception(self, mock_sns):
        mock_sns.publish.side_effect = Exception('SNS error')
        send_alert('Test message', 'us-east-1', '123456789012')
        # The function now handles the exception, so we just check that no exception is raised.
        
if __name__ == '__main__':
    unittest.main()