# cirrus

Cirrus is a proactive, serverless AWS anomaly detection tool designed to monitor resource provisioning patterns and alert on unusual behavior using behavior-based rules. It helps cloud teams identify suspicious or unexpected changes in their AWS environment, improving security and operational awareness.

## Features

- **Serverless Architecture:** Built using AWS Lambda and other serverless services for scalability and cost efficiency.
- **Behavior-Based Detection:** Monitors AWS resource provisioning events and applies customizable rules to detect anomalies.
- **Real-Time Alerts:** Sends notifications via email, Slack, or other channels when unusual activity is detected.
- **Easy Integration:** Works with existing AWS accounts and integrates with CloudWatch, SNS, and other AWS services.
- **Customizable Rules:** Users can define their own anomaly detection rules based on organizational needs.

## How It Works

1. Cirrus listens to AWS resource provisioning events (e.g., EC2, S3, IAM changes) via CloudWatch Events or EventBridge.
2. Events are processed by Python-based Lambda functions, which apply behavior-based rules to identify anomalies.
3. When an anomaly is detected, Cirrus sends an alert to configured notification channels.
4. All events and alerts are logged for auditing and analysis.

## Infrastructure & Deployment

- **Terraform:** Infrastructure is managed using Terraform modules located in the `terraform/modules` directory. These modules provision AWS resources such as Lambda, CloudWatch, EventBridge, IAM, SNS, DynamoDB, and API Gateway.
- **CI/CD:** Automated deployment is handled via GitHub Actions (`.github/workflows/terraform_deploy.yml`). The workflow builds and uploads Lambda functions and Lambda layers to S3, then initializes and applies Terraform to deploy the stack to AWS. OIDC is used for secure role assumption.
- **Lambda Packaging:** Lambda functions and layers are packaged and uploaded to S3 using the `build_and_upload_lambda_functions.sh` and `build_and_upload_lambda_layers.sh` scripts before deployment. Terraform references the code in S3 using `s3_bucket` and `s3_key`.

## Getting Started

### Prerequisites

- AWS account with permissions to deploy Lambda, CloudWatch, SNS, and related resources.
- Python 3.9 or higher (ensure consistency with Lambda runtime).
- AWS CLI configured with your credentials.
- Terraform installed locally (if deploying manually).

### Installation & Deployment

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/cirrus.git
   cd cirrus
   ```
2. Install Python dependencies:
   ```bash
   pip install -r src/packages/requirement.txt
   ```
3. Configure AWS credentials (using AWS CLI or environment variables).
4. Build and upload Lambda functions and layers to S3:
   ```bash
   cd terraform/config/modules
   ./build_and_upload_lambda_layers.sh [ENV]
   ./build_and_upload_lambda_functions.sh [ENV]
   ```
   - Replace `[ENV]` with your environment (e.g., dev, prod). These scripts will package each Lambda function and layer and upload them to the configured S3 bucket.
5. Deploy infrastructure using Terraform:
   ```bash
   cd terraform/modules
   terraform init
   terraform plan
   terraform apply
   ```
6. Alternatively, push changes to the `main` branch to trigger the GitHub Actions workflow for automated deployment. The workflow will build, upload, and deploy Lambda functions and layers automatically using OIDC and the IAM role.

### Configuration

- Edit configuration files in `terraform/config` or Lambda environment variables to customize detection rules and notification settings.
- Set up notification channels (e.g., email, Slack webhook) in the AWS SNS topic or Lambda environment variables.
- For team collaboration, configure a remote S3 backend for Terraform state.

## Usage

- Cirrus runs automatically after deployment, monitoring AWS events in real time.
- Check the logs and alert channels for notifications about detected anomalies.
- Update rules and configuration as needed to refine detection.

## Testing

Unit tests are provided for all Lambda functions in the `test/functions` directory. Tests use `unittest`, `pytest`, and mocking for AWS resources.

To run all tests:

```bash
pytest test/functions
```

- `test/functions/test_rule_management_lambda.py`: Tests for rule management Lambda.
- `test/functions/test_data_injestion_lambda.py`: Tests for data ingestion Lambda.
- `test/functions/test_anomaly_detector_lambda.py`: Tests for anomaly detector Lambda.

## Project Structure

- `src/functions/anomaly_detector/lambda_function.py`: Core anomaly detection logic.
- `src/functions/data_injestion/lambda_function.py`: Handles data ingestion from AWS events.
- `src/functions/rule_management/lambda_function.py`: Manages behavior-based rules for anomaly detection.
- `src/packages/requirement.txt`: Python dependencies for Lambda functions and testing.
- `test/functions/`: Unit tests for all Lambda modules.
- `terraform/config/modules/`: Build and upload scripts for Lambda functions and layers.
- `terraform/modules/`: Terraform modules for AWS infrastructure.
- `.github/workflows/terraform_deploy.yml`: GitHub Actions workflow for CI/CD.
- `LICENSE`: MIT License.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository and create a new branch.
2. Make your changes and add tests if applicable.
3. Submit a pull request with a clear description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, open an issue on GitHub or contact the maintainers at [your-email@example.com].
