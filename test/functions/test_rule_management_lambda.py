import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json
from src.functions.rule_management.lambda_function import create_rule, get_all_rules, get_rule_by_id, delete_rule

# Set a dummy environment variable for the test environment.
os.environ.setdefault('DYNAMODB_RULES_TABLE', 'dummy')

# Mock boto3 and botocore to prevent actual AWS calls.
sys.modules['boto3'] = MagicMock()
sys.modules['botocore'] = MagicMock()

# Add the project root to the system path for correct imports.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

class TestRuleManagementLambda(unittest.TestCase):
    """
    Test suite for the Rule Management Lambda function.

    This suite contains unit tests for the functions that handle CRUD operations
    for anomaly detection rules via an API Gateway. It uses mocked AWS services
    to ensure tests are isolated and do not make real API calls.
    """

    @patch('src.functions.rule_management.lambda_function.table')
    def test_create_rule_success(self, mock_table):
        """
        Test successful rule creation.

        This test verifies that `create_rule` correctly processes a valid
        request body, calls `put_item` on the DynamoDB table, and returns a
        201 status code with a success message.
        """
        event = {
            'body': json.dumps({
                'ruleType': 'count-based',  
                'metric': 'cpu',
                'threshold': 80,
                'timeWindow': 5,
                'target': 'user-123'  
            })
        }
        mock_table.put_item.return_value = None
        response = create_rule(event)
        self.assertEqual(response['statusCode'], 201)
        self.assertIn('Rule created successfully', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_create_rule_missing_fields(self, mock_table):
        """
        Test rule creation with a missing required field.

        This test ensures that `create_rule` returns a 400 status code and
        an informative error message if the request body is missing any
        of the required fields.
        """
        event = {
            'body': json.dumps({
                'ruleType': 'anomaly',
                'metric': 'cpu'
            })
        }
        response = create_rule(event)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Missing required fields', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_get_all_rules_success(self, mock_table):
        """
        Test successful retrieval of all rules.

        This test verifies that `get_all_rules` performs a successful DynamoDB
        scan and returns a 200 status code with a list of items in the body.
        """
        mock_table.scan.return_value = {'Items': [{'ruleId': '1', 'ruleType': 'anomaly'}]}
        response = get_all_rules()
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('ruleType', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_get_all_rules_exception(self, mock_table):
        """
        Test exception handling during `get_all_rules`.

        This test checks that if a `scan` operation on the DynamoDB table
        raises an exception, the function handles it gracefully by returning
        a 500 status code.
        """
        mock_table.scan.side_effect = Exception('DB error')
        response = get_all_rules()
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('DB error', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_get_rule_by_id_found(self, mock_table):
        """
        Test successful retrieval of a single rule by ID.

        This test simulates a successful `get_item` call and ensures that
        the function returns a 200 status code with the rule's details.
        """
        event = {'pathParameters': {'ruleId': '1'}}
        mock_table.get_item.return_value = {'Item': {'ruleId': '1', 'ruleType': 'anomaly'}}
        response = get_rule_by_id(event)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('ruleType', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_get_rule_by_id_not_found(self, mock_table):
        """
        Test retrieval of a non-existent rule by ID.

        This test verifies that if `get_item` returns no item, the function
        responds with a 404 status code and a "not found" message.
        """
        event = {'pathParameters': {'ruleId': '2'}}
        mock_table.get_item.return_value = {}
        response = get_rule_by_id(event)
        self.assertEqual(response['statusCode'], 404)
        self.assertIn('Rule not found', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_get_rule_by_id_exception(self, mock_table):
        """
        Test exception handling during `get_rule_by_id`.

        This test ensures that a `get_item` exception is caught and the function
        returns a 500 status code.
        """
        event = {'pathParameters': {'ruleId': '3'}}
        mock_table.get_item.side_effect = Exception('DB error')
        response = get_rule_by_id(event)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('DB error', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_delete_rule_success(self, mock_table):
        """
        Test successful rule deletion.

        This test verifies that `delete_rule` correctly calls `delete_item` and
        returns a 200 status code when the rule is successfully removed.
        """
        event = {'pathParameters': {'ruleId': '1'}}
        mock_table.delete_item.return_value = {'Attributes': {'ruleId': '1'}} 
        response = delete_rule(event)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Rule deleted successfully', response['body'])

    @patch('src.functions.rule_management.lambda_function.table')
    def test_delete_rule_exception(self, mock_table):
        """
        Test exception handling during `delete_rule`.

        This test confirms that the function returns a 500 status code if
        a `delete_item` operation fails unexpectedly.
        """
        event = {'pathParameters': {'ruleId': '2'}}
        mock_table.delete_item.side_effect = Exception('DB error')
        response = delete_rule(event)
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Internal server error', response['body'])

if __name__ == '__main__':
    unittest.main()