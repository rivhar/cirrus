# Cirrus Setup Guide

This document provides a comprehensive guide to set up the Cirrus project, including backend configuration, manual deployment, and CI/CD deployment.

---

## 1. Backend Configuration

**Why it is important:**

- Terraform requires a backend to store state files, which keeps track of resources provisioned.
- Using a remote backend (e.g., S3 with DynamoDB for locking) ensures collaboration, state consistency, and prevents accidental resource overwrites.

**Recommended Approach:**

- It's better to create backend resources (S3 bucket and DynamoDB table) using Terraform itself.
- After creating the backend resources, migrate the state to S3 to centralize and secure it.

**Short Steps for Backend Setup using Terraform:**

1. Create a local Terraform configuration to provision S3 bucket and DynamoDB table.
2. Apply the configuration locally:

```bash
terraform init -backend=false   # Paths can be changed, relative paths from current working directory should be used
terraform apply -var-file="../config/terraform_backend.tfvars"  # Adjust path as needed
```

3. Update your main Terraform configuration to use remote backend (`backend.tf`) pointing to the S3 bucket and DynamoDB table.
4. Migrate the local state to remote backend:

```bash
terraform init -backend-config="../config/terraform_backend.conf"  # Path can be changed relative to current working directory
terraform plan -var-file="../config/terraform_config.tfvars"  # Path can be changed relative to current working directory
terraform apply -var-file="../config/terraform_config.tfvars"  # Path can be changed relative to current working directory
```

**Significance of files:**

- **`backend.tf`**: Defines the remote backend where Terraform state will be stored.
- **`backend.config`**: Provides backend-specific parameters such as bucket name, key, region, and DynamoDB table.
- **`*.tfvars` files**: Contain environment-specific variables like region, prefixes, and other configurable parameters, enabling flexible deployments across environments.

---

## 2. Manual Deployment

**Use Case:** Useful for testing, debugging, or one-off deployments without invoking CI/CD.

**Steps:**

1. Navigate to Terraform modules:

```bash
cd terraform/modules   # Path can be changed depending on project structure
```

2. Initialize Terraform with backend config:

```bash
terraform init -backend-config="../config/terraform_backend.conf"  # Relative path from current working directory
```

3. Apply Terraform configuration using variable file:

```bash
terraform apply -var-file="../config/terraform_config.tfvars"  # Relative path from current working directory
```

4. Optionally, build and upload Lambda functions and layers manually:

```bash
cd terraform/config/modules
./build_and_upload_lambda_layers.sh {environment}
./build_and_upload_lambda_functions.sh {environment}
```

---

For detailed CI/CD configuration and branch-based deployment instructions, refer to the [Cirrus CI/CD Documentation](workflows.md).
