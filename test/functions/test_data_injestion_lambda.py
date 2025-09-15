import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

os.environ.setdefault('DYNAMODB_EVENTS_TABLE', 'dummy')

from src.functions.data_injestion.lambda_function import parse_cloudtrail_event, write_to_dynamodb, lambda_handler

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

class TestDataInjestionLambda(unittest.TestCase):
    def test_parse_cloudtrail_event(self):
        event = {
            'detail': {
                'userIdentity': {'principalId': 'user123'},
                'eventTime': '2023-01-01T00:00:00Z',
                'eventName': 'RunInstances',
                'eventSource': 'ec2.amazonaws.com',
                'awsRegion': 'us-east-1',  # Added the missing 'awsRegion' key
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
        item = {'userIdentity': 'user123'}
        mock_table.put_item.return_value = None
        try:
            write_to_dynamodb(item)
        except Exception:
            self.fail('write_to_dynamodb raised Exception unexpectedly!')

    @patch('src.functions.data_injestion.lambda_function.table')
    def test_write_to_dynamodb_exception(self, mock_table):
        item = {'userIdentity': 'user123'}
        mock_table.put_item.side_effect = Exception('DB error')
        with self.assertRaises(Exception):
            write_to_dynamodb(item)

    @patch('src.functions.data_injestion.lambda_function.write_to_dynamodb')
    @patch('src.functions.data_injestion.lambda_function.parse_cloudtrail_event')
    def test_lambda_handler(self, mock_parse, mock_write):
        mock_parse.return_value = {'userIdentity': 'user123', 'eventTime': '2023-01-01T00:00:00Z', 'eventName': 'RunInstances', 'resourceType': 'ec2', 'region': 'us-east-1', 'requestParameters': '{}'}
        mock_write.return_value = None
        event = {
            'detail': {
                'userIdentity': {'principalId': 'user123'},
                'eventTime': '2023-01-01T00:00:00Z',
                'eventName': 'RunInstances',
                'eventSource': 'ec2.amazonaws.com',
                'awsRegion': 'us-east-1', # Added the missing 'awsRegion'
                'requestParameters': {'instanceType': 't2.micro'}
            }
        }
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('Event processed successfully', response['body'])

if __name__ == '__main__':
    unittest.main()