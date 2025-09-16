import os
import json
import boto3
import uuid
from decimal import Decimal


dynamodb = boto3.resource('dynamodb')
table_name = os.environ['DYNAMODB_RULES_TABLE']
table = dynamodb.Table(table_name)

def decimal_default(obj):
    """
    Helper function to serialize Decimal objects to float for JSON encoding.
    
    DynamoDB returns numbers as Decimal objects, which are not directly
    JSON serializable. This function converts them to floats, allowing
    them to be included in the JSON response body.
    """
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    """
    Main Lambda handler for the anomaly rules API.

    This function acts as a dispatcher, routing incoming API Gateway requests
    to the appropriate function based on the HTTP method and path. It supports
    CRUD (Create, Read, Update, Delete) operations for anomaly detection rules.

    Args:
        event (dict): The API Gateway event payload, including HTTP method, path, and body.
        context (LambdaContext): The context object for the Lambda function.
    
    Returns:
        dict: An API Gateway-compatible response dictionary with a status code and body.
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
    """
    Validates the request body for creating a new rule.
    
    This function checks if all required fields are present and if their values
    meet the specified criteria, such as a positive integer for 'threshold' and
    a supported value for 'ruleType'.
    
    Args:
        body (dict): The parsed JSON body of the API request.
        
    Returns:
        tuple: A tuple containing a boolean (True if valid, False otherwise) and
               a string with an error message (or None if valid).
    """
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
    """
    Creates a new anomaly detection rule in DynamoDB.
    
    This function handles POST requests to the API. It validates the request body,
    generates a unique `ruleId`, and stores the new rule as an item in the
    DynamoDB rules table.
    
    Args:
        event (dict): The API Gateway event payload.
        
    Returns:
        dict: An API Gateway-compatible response indicating success or failure.
    """
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
    """
    Retrieves all anomaly detection rules from DynamoDB.
    
    This function handles GET requests to the /rules endpoint. It performs a
    scan operation on the DynamoDB rules table and returns all items found.
    """
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
    """
    Retrieves a single rule by its unique ID from DynamoDB.
    
    This function handles GET requests to a specific rule endpoint (e.g., /rules/{ruleId}).
    It uses a `get_item` operation with the provided `ruleId` to fetch the specific rule.
    """
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
    """
    Deletes a rule by its unique ID from DynamoDB.
    
    This function handles DELETE requests to a specific rule endpoint. It attempts
    to delete the item from the DynamoDB table using the provided `ruleId`.
    It returns a success message if the item was deleted, or a 'not found'
    message if the rule did not exist.
    """
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