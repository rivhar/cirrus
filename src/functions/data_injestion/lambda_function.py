import os
import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['DYNAMODB_EVENTS_TABLE']
table = dynamodb.Table(table_name)

def parse_cloudtrail_event(event):
    """
    Parses a CloudTrail event and extracts key information.

    This function takes a raw AWS CloudTrail event (received from services like EventBridge)
    and processes it to extract relevant details such as the user identity, event time,
    event name, resource type, and region. These details are then formatted into a
    dictionary suitable for storage in a DynamoDB table.

    Args:
        event (dict): The raw CloudTrail event dictionary.

    Returns:
        dict: A dictionary containing parsed event data.
    """
    cloudtrail_event = event['detail']
    user_identity = cloudtrail_event['userIdentity']['principalId']
    event_time = cloudtrail_event['eventTime']
    event_name = cloudtrail_event['eventName']
    resource_type = cloudtrail_event['eventSource'].split('.')[0]
    region = cloudtrail_event['awsRegion']
    request_params = cloudtrail_event.get('requestParameters', {})

    item = {
        'userIdentity': user_identity,        
        'eventTime': event_time,           
        'eventName': event_name,
        'resourceType': resource_type,
        'region': region,
        'requestParameters': json.dumps(request_params)
    }
    return item

def write_to_dynamodb(item):
    """
    Writes a formatted item to the DynamoDB table.

    This function attempts to store a single item (a dictionary of event data)
    into the configured DynamoDB table. It logs the success or failure of the
    write operation, including any exceptions that occur.

    Args:
        item (dict): The dictionary of event data to be written to DynamoDB.
    """
    try:
        table.put_item(Item=item)
        print(f"Successfully wrote item to DynamoDB: {item}")
    except Exception as e:
        print(f"Error writing to DynamoDB: {e}")
        raise e


def lambda_handler(event, context):
    """
    Main handler for the Lambda function.

    This function is triggered by an event from a source like EventBridge, typically
    with a CloudTrail event payload. It calls `parse_cloudtrail_event` to extract
    the necessary data and then `write_to_dynamodb` to persist that data.
    It logs the incoming event and provides a status response.

    Args:
        event (dict): The event dictionary passed to the Lambda function.
        context (LambdaContext): The context object for the Lambda function.

    Returns:
        dict: A dictionary with a status code and a body message.
    """
    print("Received event: " + json.dumps(event, indent=2))
    item = parse_cloudtrail_event(event)
    write_to_dynamodb(item)

    return {
        'statusCode': 200,
        'body': json.dumps('Event processed successfully!')
    } 