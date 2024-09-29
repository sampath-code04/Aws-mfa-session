# AWS MFA Session Management

This Python script allows you to manage AWS sessions using Multi-Factor Authentication (MFA). It retrieves temporary credentials and enables you to start a session with an EC2 instance via AWS Systems Manager (SSM) with port forwarding for RDP access.

## Features

- Retrieve and store MFA device ARN from AWS CLI configuration.
- Get temporary AWS credentials using the MFA device.
- Store temporary credentials in a dedicated AWS CLI profile.
- List EC2 instances accessible to the user.
- Start an SSM session with port forwarding to connect via RDP.

## Requirements

- Python 3.x
- AWS CLI installed and configured with necessary permissions
- `boto3` (optional for other integrations)
- Access to an AWS account with EC2 instances and SSM enabled
- Multi-Factor Authentication device configured in AWS IAM

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sampath-code04/Aws-mfa-session.git
   cd Aws-mfa-session
   ```

2. **Install dependencies** (if any):
   ```bash
   pip install boto3
   ```

## Usage

1. **Run the script**:
   ```bash
   python aws_mfa_session.py
   ```

2. **Follow the prompts**:
   - If the MFA ARN is not found in the AWS configuration, you will be prompted to enter it.
   - Enter the MFA code from your authentication device.
   - Temporary credentials will be retrieved and stored in the `mfa` profile.
   - A list of accessible EC2 instances will be displayed. Select one to start an SSM session.

3. **Connect via RDP**:
   - You will be given instructions on how to connect via RDP using the local port specified.

## Configuration

### AWS Configuration

Before using the script, ensure that your AWS CLI is configured with a profile that has permission to call STS and describe EC2 instances:

```bash
aws configure
```

### MFA Device ARN

The script looks for the `mfa_device_arn` in your AWS CLI configuration. If it's not set, you will be prompted to enter it.

## Notes

- Ensure that your EC2 instances have the SSM agent installed and running.
- The script assumes that the default AWS CLI profile is set up correctly.
- The local port must be free; choose a port between 1024 and 65535.
- The session will only work if the instance has a public IP or is accessible via an SSM endpoint.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Feel free to fork the repository, make changes, and create pull requests. Any contributions are welcome!

## Support

For issues or questions, please open an issue in the repository.