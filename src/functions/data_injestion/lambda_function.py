import os
import json
import boto3
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['DYNAMODB_EVENTS_TABLE']
table = dynamodb.Table(table_name)

def parse_cloudtrail_event(event):
    cloudtrail_event = event['detail']
    user_identity = cloudtrail_event['userIdentity']['principalId']
    event_time = cloudtrail_event['eventTime']
    event_name = cloudtrail_event['eventName']
    resource_type = cloudtrail_event['eventSource'].split('.')[0]
    region = cloudtrail_event['awsRegion']
    request_params = cloudtrail_event.get('requestParameters', {})

    # Structure the item properly
    item = {
        'userIdentity': user_identity,         # Partition Key
        'eventTime': event_time,              # Sort Key
        'eventName': event_name,
        'resourceType': resource_type,
        'region': region,
        'requestParameters': json.dumps(request_params)
    }
    return item

def write_to_dynamodb(item):
    try:
        table.put_item(Item=item)
        print(f"Successfully wrote item to DynamoDB: {item}")
    except Exception as e:
        print(f"Error writing to DynamoDB: {e}")
        raise e


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    item = parse_cloudtrail_event(event)
    write_to_dynamodb(item)

    return {
        'statusCode': 200,
        'body': json.dumps('Event processed successfully!')
    }
