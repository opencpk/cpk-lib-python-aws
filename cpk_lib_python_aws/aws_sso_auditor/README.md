# 🔍 AWS SSO Auditor

A powerful CLI tool for auditing AWS Single Sign-On (SSO) configurations, analyzing permission sets, groups, and assignments across AWS accounts. This tool simplifies AWS SSO compliance and security audits by providing comprehensive reporting and analysis capabilities.

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Examples](#-usage-examples)
- [Command Reference](#-command-reference)
- [Environment Variables](#-environment-variables)
- [Sample Outputs](#-sample-outputs)
- [Common Use Cases](#-common-use-cases)
- [Configuration](#-configuration)
- [Python Usage](#-python-usage)

## ✨ Features

- 🔍 **Comprehensive SSO Auditing**: Analyze AWS SSO groups, permission sets, and account assignments
- 👥 **Group Analysis**: Detailed group membership and permission mapping
- 🔐 **Permission Set Analysis**: In-depth analysis of AWS managed, customer managed, and inline policies
- 📊 **Multi-format Output**: Support for JSON and YAML output formats
- 🎯 **Account-specific Auditing**: Focus audits on specific AWS accounts
- 📁 **Flexible Output Management**: Configurable output directories with timestamp support
- 🌍 **Environment Variables**: Full support for environment-based configuration
- 🎨 **Rich Console Output**: Colorized, well-formatted output with progress indicators
- 📝 **Debug Mode**: Detailed logging for troubleshooting
- 🏗️ **Professional Architecture**: Modular design with proper error handling

## 🚀 Installation

### Prerequisites

- AWS SSO enabled in your AWS organization
- AWS credentials with appropriate SSO permissions:
  - `sso-admin:*` permissions
  - `identitystore:*` permissions 
  - `organizations:ListAccounts` permission

### Install from Source

```bash
pip install git+https://github.com/opencpk/cpk-lib-python-aws.git@main
```

### Verify Installation

```bash
aws-sso-auditor --help
```

## 🎯 Quick Start

### 1. Set up AWS Credentials

```bash
# Using AWS CLI profiles
export AWS_PROFILE=sso-admin

# Or using environment variables
export AWS_REGION=us-east-1
```

### 2. Run Your First Audit

```bash
aws-sso-auditor 123456789012 --output-format json
```

### 3. Generate Comprehensive Reports

```bash
aws-sso-auditor 123456789012 --output-format both --output-dir ./audit-reports
```

## 📖 Usage Examples

### 🔍 Basic Auditing

#### Audit a specific AWS account:
```bash
aws-sso-auditor 123456789012
```

#### Audit with JSON output only:
```bash
aws-sso-auditor 123456789012 --output-format json
```

#### Audit with YAML output only:
```bash
aws-sso-auditor 123456789012 --output-format yaml
```

#### Audit with both formats:
```bash
aws-sso-auditor 123456789012 --output-format both
```

### 📁 Output Management

#### Custom output directory:
```bash
aws-sso-auditor 123456789012 --output-dir ./my-audit-reports
```

#### Disable timestamps in filenames:
```bash
aws-sso-auditor 123456789012 --no-timestamp
```

### 🌍 Region and Profile Configuration

#### Specify AWS region:
```bash
aws-sso-auditor 123456789012 --aws-region us-west-2
```

#### Use specific AWS profile:
```bash
aws-sso-auditor 123456789012 --aws-profile sso-admin-profile
```

### 🔇 Quiet and Debug Modes

#### Quiet mode (no console output):
```bash
aws-sso-auditor 123456789012 --quiet
```

#### Debug mode (detailed logging):
```bash
aws-sso-auditor 123456789012 --debug
```

### 🐛 Debug & Help

#### Show help:
```bash
aws-sso-auditor --help
```

## 📚 Command Reference

| Argument | Description | Default |
|----------|-------------|---------|
| `account_id` | AWS Account ID to audit (required) | - |
| `--output-format` | Output format: `json`, `yaml`, or `both` | `both` |
| `--output-dir` | Output directory path | `./aws-sso-audit-results` |
| `--aws-region` | AWS region | `us-east-1` |
| `--aws-profile` | AWS profile to use | None |
| `--quiet` `-q` | Suppress console output and logging, only save files | `False` |
| `--debug` | Enable debug logging | `False` |
| `--no-timestamp` | Don't include timestamp in filenames | `False` |
| `--help` | Show help message | - |

## 🌍 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_REGION` | AWS region | `us-east-1` |
| `AWS_PROFILE` | AWS profile to use | `sso-admin` |
| `AWS_SSO_AUDITOR_OUTPUT_DIR` | Default output directory | `./audit-reports` |
| `AWS_SSO_AUDITOR_DEBUG` | Enable debug mode | `true` |
| `AWS_SSO_AUDITOR_QUIET` | Enable quiet mode | `true` |

### Setting Environment Variables

```bash
# Basic configuration
export AWS_REGION=us-east-1

# Advanced configuration
export AWS_SSO_AUDITOR_OUTPUT_DIR=./audit-reports
export AWS_SSO_AUDITOR_DEBUG=true

# Then use shorter commands
aws-sso-auditor 123456789012
```

## 🎨 Sample Outputs

### 📊 Successful Audit Output

```bash
$ aws-sso-auditor 123456789012 --output-format json --debug
```

**Console Output:**
```
⏳ Initializing AWS clients...
⏳ Starting audit for account: 123456789012
⏳ Retrieving account assignments...
🔍 Found 13 assignments
⏳ Processing assignments...
⏳ Processing group: 90967fb4-d4e1-7019-c6a2-3b4d2a8c7e5f
⏳ Processing permission set: arn:aws:sso:::permissionSet/ssoins-1234567890abcdef/ps-1234567890abcdef
⏳ Finalizing audit results...
✅ Results saved to: ./aws-sso-audit-results/aws_sso_audit_123456789012_20250107_124443.json

📊 AWS SSO Audit Summary
🆔 Account: 123456789012
📅 Generated: 2025-01-07T12:44:43.717
👥 Groups: 3
🔐 Permission Sets: 5
🔗 Assignments: 13
```

### 📋 Sample JSON Output Structure

```json
{
  "metadata": {
    "generated_at": "2025-01-07T12:44:43.717",
    "account_id": "123456789012",
    "sso_instance_arn": "arn:aws:sso:::instance/ssoins-1234567890abcdef",
    "identity_store_id": "d-1234567890",
    "auditor_version": "1.0.0",
    "config": {
      "aws_region": "us-east-1",
      "output_formats": ["json"]
    }
  },
  "sso_groups_summary": [
    "Developers",
    "Administrators", 
    "ReadOnlyUsers"
  ],
  "sso_permission_sets_summary": [
    "AdministratorAccess",
    "DeveloperAccess",
    "ReadOnlyAccess",
    "PowerUserAccess",
    "CustomDataAccess"
  ],
  "sso_groups": [
    {
      "GroupId": "90967fb4-d4e1-7019-c6a2-3b4d2a8c7e5f",
      "DisplayName": "Developers",
      "Description": "Development team members",
      "Members": [
        {
          "UserId": "90967fb4-b2c1-70a8-b8a2-1b2c3d4e5f6g",
          "UserName": "john.doe",
          "DisplayName": "John Doe",
          "Email": "john.doe@company.com"
        }
      ],
      "PermissionSets": [
        {
          "Name": "DeveloperAccess",
          "Description": "Developer permissions",
          "Policies": {
            "managed_policies": [
              {
                "Name": "PowerUserAccess",
                "Arn": "arn:aws:iam::aws:policy/PowerUserAccess"
              }
            ],
            "customer_managed_policies": [],
            "inline_policy": null
          }
        }
      ]
    }
  ],
  "permission_sets": [
    {
      "Name": "DeveloperAccess",
      "Description": "Developer permissions",
      "CreatedDate": "2024-01-15T10:30:00Z",
      "SessionDuration": "PT8H",
      "Policies": {
        "managed_policies": [
          {
            "Name": "PowerUserAccess",
            "Arn": "arn:aws:iam::aws:policy/PowerUserAccess"
          }
        ],
        "customer_managed_policies": [],
        "inline_policy": {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": "s3:GetObject",
              "Resource": "arn:aws:s3:::company-dev-bucket/*"
            }
          ]
        }
      },
      "AssignedGroups": [
        "90967fb4-d4e1-7019-c6a2-3b4d2a8c7e5f"
      ]
    }
  ],
  "summary": {
    "total_groups": 3,
    "total_permission_sets": 5,
    "total_assignments": 13
  }
}
```

### ❌ Error Output Examples

#### Account not found:
```bash
$ aws-sso-auditor 999999999999
```
**Output:**
```
❌ AWS SSO Auditor Error: No permission sets found for account 999999999999
```

#### Invalid credentials:
```bash
$ aws-sso-auditor 123456789012
```
**Output:**
```
❌ Unexpected error: Unable to locate credentials
```

### 🔇 Quiet Mode Output

```bash
$ aws-sso-auditor 123456789012 --quiet
```
**Output:** (No console output, only files generated)

### 🐛 Debug Mode Output

```bash
$ aws-sso-auditor 123456789012 --debug
```


## 🐍 Python Usage

If you prefer to use this tool as a Python library in your scripts:

### Programmatic Usage

```python -c "
from cpk_lib_python_aws.aws_sso_auditor import AWSSSOAuditor, Config, OutputFormatter
from cpk_lib_python_aws.shared import OutputSink

config = Config(
    output_directory='./test-results-1',
    include_timestamp=False,
    quiet=False
)

output_sink = OutputSink(quiet=True)
auditor = AWSSSOAuditor(config, output_sink)
formatter = OutputFormatter(config, output_sink)

results = auditor.audit_account('123456789012')
formatter.save_results(results, '123456789012')
"
```


### Without Timestamps

```
./aws-sso-audit-results/
├── aws_sso_audit_123456789012.json
└── aws_sso_audit_123456789012.yaml
```

## 📄 License

This project is licensed under the GPLv3 License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
