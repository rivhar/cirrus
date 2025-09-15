import os
import json
import boto3
import uuid
from decimal import Decimal


# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['DYNAMODB_RULES_TABLE']
table = dynamodb.Table(table_name)

def decimal_default(obj):
    if isinstance(obj, Decimal):
        # Convert Decimal to float (you could also use int if appropriate)
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    """
    Handles CRUD operations for anomaly detection rules via API Gateway.
    """
    http_method = event['httpMethod']
    path = event['path']

    if http_method == 'POST':
        return create_rule(event)
    elif http_method == 'GET':
        if path == '/rules':
            return get_all_rules()
        else:
            return get_rule_by_id(event)
    elif http_method == 'DELETE':
        return delete_rule(event)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid HTTP method'})
        }


def validate_rule_body(body):
    required_fields = ['ruleType', 'metric', 'threshold', 'timeWindow', 'target']
    missing_fields = [k for k in required_fields if k not in body]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    if body['ruleType'] not in ['count-based']:
        return False, "Unsupported ruleType. Supported values: count-based"
    
    if not isinstance(body['threshold'], int) or body['threshold'] <= 0:
        return False, "threshold must be a positive integer"
    
    if not isinstance(body['timeWindow'], int) or body['timeWindow'] <= 0:
        return False, "timeWindow must be a positive integer (minutes)"
    
    return True, None


def create_rule(event):
    """Creates a new anomaly detection rule in DynamoDB."""
    try:
        body = json.loads(event['body'])
        rule_id = str(uuid.uuid4())
        body['ruleId'] = rule_id

        is_valid, error_msg = validate_rule_body(body)
        if not is_valid:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': error_msg})
            }

        # Ensure consistent field naming
        body['timeWindow'] = body.pop('timeWindow')

        table.put_item(Item=body)

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Rule created successfully', 'ruleId': rule_id})
        }

    except Exception as e:
        print(f"Error in create_rule: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error'})
        }

def get_all_rules():
    try:
        response = table.scan()
        return {
            'statusCode': 200,
            'body': json.dumps(response['Items'], default=decimal_default)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }

def get_rule_by_id(event):
    rule_id = event['pathParameters']['ruleId']
    try:
        response = table.get_item(Key={'ruleId': rule_id})
        if 'Item' in response:
            return {
                'statusCode': 200,
                'body': json.dumps(response['Item'], default=decimal_default)
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Rule not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }

def delete_rule(event):
    """Deletes a rule by ruleId."""
    rule_id = event['pathParameters']['ruleId']
    try:
        response = table.delete_item(
            Key={'ruleId': rule_id},
            ReturnValues='ALL_OLD'
        )

        if 'Attributes' in response:
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Rule deleted successfully'})
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Rule not found'})
            }

    except Exception as e:
        print(f"Error in delete_rule: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error'})
        }
