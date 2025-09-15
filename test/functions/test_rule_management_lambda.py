import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json
from src.functions.rule_management.lambda_function import create_rule, get_all_rules, get_rule_by_id, delete_rule

# Set the environment variable required by the lambda function.
os.environ.setdefault('DYNAMODB_RULES_TABLE', 'dummy')

# Mock boto3 and its resources to prevent real API calls.
sys.modules['boto3'] = MagicMock()
sys.modules['botocore'] = MagicMock()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

class TestRuleManagementLambda(unittest.TestCase):

    @patch('src.functions.rule_management.lambda_function.table')
    def test_create_rule_success(self, mock_table):
        # Add the 'target' field as required by the validate_rule_body function
        event = {
            'body': json.dumps({
                'ruleType': 'count-based',  # Changed to 'count-based' to pass validation
                'metric': 'cpu',
                'threshold': 80,
                'timeWindow': 5,
                'target': 'user-123'  # Added the required 'target' field
            })
        }
        mock_table.put_item.return_value = None
        response = create_rule(event)
        self.assertEqual(response['statusCode'], 201)
        self.assertIn('Rule created successfully', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_create_rule_missing_fields(self, mock_table):
        event = {
            'body': json.dumps({
                'ruleType': 'anomaly',
                'metric': 'cpu'
            })
        }
        response = create_rule(event)
        self.assertEqual(response['statusCode'], 400)
        # The expected message has changed based on the `validate_rule_body` function
        self.assertIn('Missing required fields', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_get_all_rules_success(self, mock_table):
        mock_table.scan.return_value = {'Items': [{'ruleId': '1', 'ruleType': 'anomaly'}]}
        response = get_all_rules()
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('ruleType', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_get_all_rules_exception(self, mock_table):
        mock_table.scan.side_effect = Exception('DB error')
        response = get_all_rules()
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('DB error', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_get_rule_by_id_found(self, mock_table):
        event = {'pathParameters': {'ruleId': '1'}}
        mock_table.get_item.return_value = {'Item': {'ruleId': '1', 'ruleType': 'anomaly'}}
        response = get_rule_by_id(event)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('ruleType', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_get_rule_by_id_not_found(self, mock_table):
        event = {'pathParameters': {'ruleId': '2'}}
        mock_table.get_item.return_value = {}
        response = get_rule_by_id(event)
        self.assertEqual(response['statusCode'], 404)
        self.assertIn('Rule not found', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_get_rule_by_id_exception(self, mock_table):
        event = {'pathParameters': {'ruleId': '3'}}
        mock_table.get_item.side_effect = Exception('DB error')
        response = get_rule_by_id(event)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('DB error', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_delete_rule_success(self, mock_table):
        event = {'pathParameters': {'ruleId': '1'}}
        # Mock the delete_item response to include 'Attributes' to pass the check
        mock_table.delete_item.return_value = {'Attributes': {'ruleId': '1'}} 
        response = delete_rule(event)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Rule deleted successfully', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_delete_rule_exception(self, mock_table):
        event = {'pathParameters': {'ruleId': '2'}}
        mock_table.delete_item.side_effect = Exception('DB error')
        response = delete_rule(event)
        self.assertEqual(response['statusCode'], 500)
        # The lambda function returns a generic error message, not the specific exception.
        self.assertIn('Internal server error', response['body'])

if __name__ == '__main__':
    unittest.main()