# Cirrus ☁️

Cirrus is a proactive, serverless AWS anomaly detection tool that helps cloud teams improve security and operational awareness. It monitors your AWS environment for suspicious or unexpected changes in resource provisioning by applying customizable, behavior-based rules and alerting you in real time.

---

## Overview

Cirrus helps cloud teams detect anomalies in AWS environments, improving security and operational awareness through behavior-based rules.

---

## Why Use Cirrus? 🕵️‍♂️

In today's dynamic cloud environments, identifying unauthorized or accidental changes is critical. Cirrus fills this gap by providing real-time visibility into your AWS provisioning events. It's not just another logging tool; it actively analyzes behavior and helps you answer critical questions like:

- Is someone provisioning resources in an unusual region?
- Is a new IAM user suddenly creating multiple S3 buckets?
- Has an EC2 instance been created with an unexpected type?

By focusing on these behavioral anomalies, Cirrus helps you detect potential security threats and prevent operational misconfigurations before they escalate. Its serverless architecture ensures it scales automatically with your needs and is highly cost-effective, so you only pay for what you use.

---

## Key Features

- **Serverless Architecture:** Built with AWS Lambda, DynamoDB, SNS, and EventBridge.
- **Behavior-Based Detection:** Monitors AWS resource provisioning events.
- **Real-Time Alerts:** Notifications via email, Slack, or SNS.
- **Customizable Rules:** Define your own anomaly detection rules.
- **Easy Integration:** Works seamlessly with existing AWS accounts.

---

## Terraform-Branch-Deploy in CI/CD

Cirrus uses [terraform-branch-deploy](https://github.com/scarowar/terraform-branch-deploy) to automate Terraform deployments safely and efficiently. It enables branch-based infrastructure deployments, ensures Terraform plans are previewed before apply, and integrates seamlessly with our GitHub Actions workflow for CI/CD.

## Quick Links

- [Full Documentation](docs/index.md)
- [License](https://github.com/rivhar/cirrus/blob/develop/LICENSE)

---
