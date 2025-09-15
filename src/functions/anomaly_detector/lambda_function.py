import os
import json
import boto3
from datetime import datetime, timedelta

# Boto3 clients and resources are initialized here.
# You can keep these as they are.
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# 1. Get only the SNS topic NAME from the environment variable.
#    We are no longer expecting the full ARN.
sns_topic_name = os.environ['SNS_TOPIC_NAME']

events_table = dynamodb.Table(os.environ['DYNAMODB_EVENTS_TABLE'])
rules_table = dynamodb.Table(os.environ['DYNAMODB_RULES_TABLE'])

def lambda_handler(event, context):
    """
    Scans for anomaly rules, queries resource events, and sends alerts.
    """
    print("Starting anomaly detection analysis.")
    
    # 2. Get the AWS region and account ID dynamically from the Lambda context object.
    #    This is a secure way to get this information at runtime.
    aws_region = context.invoked_function_arn.split(":")[3]
    aws_account_id = context.invoked_function_arn.split(":")[4]

    # Pass the dynamically retrieved account ID and region to the alert function.
    send_alert_with_context = lambda msg: send_alert(msg, aws_region, aws_account_id)

    # 1. Get all active rules from the DynamoDB rules table.
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
            # 2. For each rule, query the resource events table.
            check_anomaly(rule, send_alert_with_context)
        except Exception as e:
            print(f"Error processing rule {rule.get('ruleId')}: {e}")

    print("Anomaly detection analysis complete.")
    return {
        'statusCode': 200,
        'body': json.dumps('Analysis complete.')
    }


def check_anomaly(rule, send_alert_function):
    rule_id = rule['ruleId']
    rule_name = rule.get('ruleName', 'Unnamed Rule')
    rule_type = rule['ruleType']
    metric = rule['metric']
    threshold = int(rule['threshold'])
    time_window_minutes = int(rule['timeWindow'])

    # Timestamp formatting (no microseconds)
    time_format = "%Y-%m-%dT%H:%M:%SZ"
    current_time = datetime.utcnow().replace(microsecond=0)
    time_cutoff = current_time - timedelta(minutes=time_window_minutes)

    time_cutoff_str = time_cutoff.strftime(time_format)
    current_time_str = current_time.strftime(time_format)

    print(f"Querying events from {time_cutoff_str} to {current_time_str}")

    # Scan the events table to get all events in time window
    # Note: We have to use scan now because partition key (userIdentity) is not known.
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
    """Publishes a message to the SNS topic."""
    try:
        # 3. Construct the full ARN with the dynamic account ID and region.
        sns_topic_arn = f"arn:aws:sns:{region}:{account_id}:{sns_topic_name}"

        sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject="Cloud Resource Anomaly Detected!"
        )
        print("Alert published to SNS topic.")
    except Exception as e:
        print(f"Failed to publish to SNS: {e}")