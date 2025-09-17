# Terraform Branch Deploy & CI/CD Overview

Terraform Branch Deploy extends branch-deploy with first-class support for Terraform infrastructure automation and integrates seamlessly with the Cirrus CI/CD pipeline.

## Deployment Pipeline

- Builds Lambda layers and functions.
- Uploads artifacts to S3.
- Applies Terraform to provision/update AWS resources.
- Uses OIDC for secure AWS role assumption.
- Supports branch-based deployments (dev, prod) via `terraform-branch-deploy`.

**Usage of `terraform-branch-deploy`:**

- **PR-driven automation:** Trigger plan and apply by commenting on pull requests.
- **Environment targeting:** Define environments (dev, staging, prod, etc.) in `.tf-branch-deploy.yml` with per-environment config, variable files, and working directories.
- **Safe deployments:** Preview every change with a Terraform plan before apply and support instant rollbacks to a stable branch.
- **Environment locking:** Prevent concurrent or conflicting deployments with automatic and manual environment locks.
- **Custom arguments:** Pass extra Terraform CLI arguments from PR comments and fine-tune behavior per environment or globally via `.tf-branch-deploy.yml`.
- **Enterprise ready:** Works with GitHub Enterprise Server (GHES) and public GitHub, with automated GHES release tagging.
- **Workflow integration:** Use the skip input to extract environment context for advanced, multi-step workflows without running Terraform operations.
- **Repository:** [terraform-branch-deploy](https://github.com/scarowar/terraform-branch-deploy)

## CI/CD Deployment

**Why use CI/CD deployment:**

- Automates deployment and reduces human errors.
- Integrates with branch-based environments (dev, staging, prod).
- Ensures consistent infrastructure provisioning across environments.
- Allows safe, PR-driven Terraform plan and apply using `terraform-branch-deploy`.

**Workflow:**

1. Code changes pushed to `develop` or `main` branch.
2. CI/CD pipeline builds artifacts, uploads to S3, and triggers Terraform deployments.
3. Terraform operations are executed safely with environment-specific configurations and locking.

**Benefits:**

- Faster and repeatable deployments.
- Enforces environment isolation.
- Integrates unit testing to prevent broken changes from reaching production.
- Maintains audit trail of deployments.

---

## Unit Testing Pipeline

- Runs automatically on pull requests to `main` and `develop`.
- Sets up Python virtual environment and installs dependencies.
- Executes all unit tests using `pytest`.
- Ensures that new changes do not break existing functionality.

Run tests manually:

```bash
PYTHONPATH=. pytest
```
