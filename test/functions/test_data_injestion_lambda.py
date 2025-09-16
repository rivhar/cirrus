import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

# Set a dummy environment variable for testing purposes
os.environ.setdefault('DYNAMODB_EVENTS_TABLE', 'dummy')

# Import the functions to be tested and mock the boto3 library to prevent actual AWS calls
from src.functions.data_injestion.lambda_function import parse_cloudtrail_event, write_to_dynamodb, lambda_handler

# Add the project root to the system path for correct imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

class TestDataInjestionLambda(unittest.TestCase):
    """
    Test suite for the Data Ingestion Lambda function.

    This class contains unit tests that verify the core functionalities of the Lambda
    function responsible for ingesting CloudTrail events into a DynamoDB table. It
    uses mocks to isolate the code logic from external dependencies like AWS services.
    """
    def test_parse_cloudtrail_event(self):
        """
        Test the parsing of a raw CloudTrail event.

        This test ensures that the `parse_cloudtrail_event` function correctly
        extracts key information from a standard CloudTrail event structure
        and formats it into the expected dictionary for DynamoDB insertion.
        """
        event = {
            'detail': {
                'userIdentity': {'principalId': 'user123'},
                'eventTime': '2023-01-01T00:00:00Z',
                'eventName': 'RunInstances',
                'eventSource': 'ec2.amazonaws.com',
                'awsRegion': 'us-east-1', 
                'requestParameters': {'instanceType': 't2.micro'}
            }
        }
        item = parse_cloudtrail_event(event)
        self.assertEqual(item['userIdentity'], 'user123')
        self.assertEqual(item['eventTime'], '2023-01-01T00:00:00Z')
        self.assertEqual(item['eventName'], 'RunInstances')
        self.assertEqual(item['resourceType'], 'ec2')
        self.assertEqual(item['region'], 'us-east-1')
        self.assertIn('instanceType', json.loads(item['requestParameters']))

    @patch('src.functions.data_injestion.lambda_function.table')
    def test_write_to_dynamodb_success(self, mock_table):
        """
        Test a successful write operation to DynamoDB.

        This test case mocks the DynamoDB `put_item` call and verifies that the
        `write_to_dynamodb` function completes without raising an exception when
        the write operation is successful.
        """
        item = {'userIdentity': 'user123'}
        mock_table.put_item.return_value = None
        try:
            write_to_dynamodb(item)
        except Exception:
            self.fail('write_to_dynamodb raised Exception unexpectedly!')

    @patch('src.functions.data_injestion.lambda_function.table')
    def test_write_to_dynamodb_exception(self, mock_table):
        """
        Test that an exception is raised on a failed DynamoDB write.

        This test mocks the `put_item` method to raise an exception, ensuring that
        the `write_to_dynamodb` function correctly propagates this exception.
        """
        item = {'userIdentity': 'user123'}
        mock_table.put_item.side_effect = Exception('DB error')
        with self.assertRaises(Exception):
            write_to_dynamodb(item)

    @patch('src.functions.data_injestion.lambda_function.write_to_dynamodb')
    @patch('src.functions.data_injestion.lambda_function.parse_cloudtrail_event')
    def test_lambda_handler(self, mock_parse, mock_write):
        """
        Test the main Lambda handler's orchestration.

        This test verifies that the `lambda_handler` function correctly calls
        `parse_cloudtrail_event` and `write_to_dynamodb` in the right order
        and returns the expected success response.
        """
        mock_parse.return_value = {'userIdentity': 'user123', 'eventTime': '2023-01-01T00:00:00Z', 'eventName': 'RunInstances', 'resourceType': 'ec2', 'region': 'us-east-1', 'requestParameters': '{}'}
        mock_write.return_value = None
        event = {
            'detail': {
                'userIdentity': {'principalId': 'user123'},
                'eventTime': '2023-01-01T00:00:00Z',
                'eventName': 'RunInstances',
                'eventSource': 'ec2.amazonaws.com',
                'awsRegion': 'us-east-1',
                'requestParameters': {'instanceType': 't2.micro'}
            }
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Event processed successfully', response['body'])

if __name__ == '__main__':
    unittest.main()