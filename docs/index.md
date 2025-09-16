# Cirrus Documentation

**Cirrus** is a proactive, serverless AWS anomaly detection tool for monitoring AWS resource provisioning and alerting on unusual behavior.

---

## Overview

Cirrus helps cloud teams:

- Detect unexpected or suspicious changes in AWS environments.
- Improve operational awareness and security posture.
- Enforce behavior-based rules on resource provisioning events.

---

## Key Features

- **Serverless Architecture:** Fully serverless and cost-efficient, built with Lambda, DynamoDB, SNS, EventBridge, and API Gateway.
- **Behavior-Based Detection:** Create count-based anomaly detection rules.
- **Real-Time Alerts:** Sends notifications via SNS to email, Slack, or other channels.
- **Customizable Rules:** Add, update, and delete rules according to organizational needs.
- **Easy Integration:** Works with existing AWS accounts with minimal configuration.

---

# Core Components

Cirrus consists of three main Lambda functions:

## Data Ingestion Lambda

- Collects CloudTrail events.
- Parses user identity, event time, event name, resource type, region, and request parameters.
- Writes structured events to DynamoDB.

## Anomaly Detector Lambda

- Scans DynamoDB for events.
- Applies count-based rules to detect anomalies.
- Sends alerts via SNS to email, Slack, or other channels.
- Dynamically constructs SNS topic ARN from AWS account and region.

## Rule Management Lambda

- Provides CRUD operations for rules through API Gateway.
- Supports `count-based` rules.
- Enables creating, updating, retrieving, and deleting rules in DynamoDB.

---

## Next Steps

- [Rule Management API](RuleAPI.md): Explore API endpoints to manage anomaly detection rules.
- [Setup Guide](setup.md): Learn how to configure backend, deploy manually, and start the project.
- [CI/CD & Unit Testing](workflows.md): Understand automated deployment pipelines and unit testing workflows.
