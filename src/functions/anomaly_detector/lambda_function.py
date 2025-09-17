import os
import json
import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

sns_topic_name = os.environ['SNS_TOPIC_NAME']

events_table = dynamodb.Table(os.environ['DYNAMODB_EVENTS_TABLE'])
rules_table = dynamodb.Table(os.environ['DYNAMODB_RULES_TABLE'])

def lambda_handler(event, context):
    """
    Main function for the Lambda handler.

    This function orchestrates the anomaly detection process. It scans for active rules in the
    'rules_table' and, for each rule, triggers a check for anomalies based on events in the
    'events_table'. If an anomaly is detected, it publishes an alert message to an SNS topic.

    Args:
        event (dict): The event dictionary passed to the Lambda function.
        context (LambdaContext): The context object for the Lambda function.

    Returns:
        dict: A dictionary with a status code and a body message.
    """
    print("Starting anomaly detection analysis.")
    
    aws_region = context.invoked_function_arn.split(":")[3]
    aws_account_id = context.invoked_function_arn.split(":")[4]

    send_alert_with_context = lambda msg: send_alert(msg, aws_region, aws_account_id)

    # Get all active rules from the DynamoDB rules table.
    try:
        rules_response = rules_table.scan()
        rules = rules_response['Items']
    except Exception as e:
        print(f"Error scanning rules table: {e}")
        return

    if not rules:
        print("No anomaly rules found. Exiting.")
        return
        
    for rule in rules:
        try:
            # For each rule, query the resource events table.
            check_anomaly(rule, send_alert_with_context)
        except Exception as e:
            print(f"Error processing rule {rule.get('ruleId')}: {e}")

    print("Anomaly detection analysis complete.")
    return {
        'statusCode': 200,
        'body': json.dumps('Analysis complete.')
    }


def check_anomaly(rule, send_alert_function):
    """
    Checks for anomalies based on a specific rule.

    This function queries the 'events_table' for events matching a specific metric
    within a defined time window. It then compares the count of these events against
    the rule's threshold. If the count exceeds the threshold, an alert is sent.

    Args:
        rule (dict): A dictionary representing a single anomaly detection rule.
        send_alert_function (function): A callback function to send an alert message.
    """
    rule_id = rule['ruleId']
    rule_name = rule.get('ruleName', 'Unnamed Rule')
    rule_type = rule['ruleType']
    metric = rule['metric']
    threshold = int(rule['threshold'])
    time_window_minutes = int(rule['timeWindow'])

    time_format = "%Y-%m-%dT%H:%M:%SZ"
    current_time = datetime.utcnow().replace(microsecond=0)
    time_cutoff = current_time - timedelta(minutes=time_window_minutes)

    time_cutoff_str = time_cutoff.strftime(time_format)
    current_time_str = current_time.strftime(time_format)

    print(f"Querying events from {time_cutoff_str} to {current_time_str}")

    # Scan the events table to get all events in time window
    response = events_table.scan(
        FilterExpression='eventTime BETWEEN :start_time AND :end_time',
        ExpressionAttributeValues={
            ':start_time': time_cutoff_str,
            ':end_time': current_time_str
        }
    )

    events = response.get('Items', [])
    count = sum(1 for e in events if e['eventName'] == metric)

    print(f"[Rule: {rule_name}] Found {count} matching events for metric {metric}")

    if rule_type == 'count-based' and count > threshold:
        message = (
            f"ANOMALY DETECTED: {rule_name}\n"
            f"Rule ID: {rule_id}\n"
            f"Metric: {metric}\n"
            f"Count: {count}, Threshold: {threshold} in last {time_window_minutes} mins."
        )
        print(f"Anomaly detected! Sending alert: {message}")
        send_alert_function(message)
    else:
        print(f"No anomaly detected for rule {rule_name}.")

def send_alert(message, region, account_id):
    """
    Publishes a message to the specified SNS topic.

    This function is responsible for sending alert messages via Amazon SNS.
    It constructs the Topic ARN using the provided region and account ID
    and publishes the message with a predefined subject.

    Args:
        message (str): The message body of the alert.
        region (str): The AWS region of the SNS topic.
        account_id (str): The AWS account ID where the SNS topic resides.
    """
    try:
        sns_topic_arn = f"arn:aws:sns:{region}:{account_id}:{sns_topic_name}"

        sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject="Cloud Resource Anomaly Detected!"
        )
        print("Alert published to SNS topic.")
    except Exception as e:
        print(f"Failed to publish to SNS: {e}")