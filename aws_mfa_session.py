import subprocess
import json
import os
import socket

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise Exception(result.stderr.decode('utf-8'))
        return result.stdout.decode('utf-8')
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

def get_mfa_arn_from_aws_config():
    # Get the MFA device ARN using AWS CLI
    command = 'aws configure get mfa_device_arn'
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print("MFA device ARN not found in the AWS configuration.")
            return None
        return result.stdout.decode('utf-8').strip()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
    

def store_mfa_arn_in_aws_config(mfa_device_arn):
    # Set the MFA ARN in the AWS configuration using AWS CLI
    command = f'aws configure set mfa_device_arn "{mfa_device_arn}"'
    run_command(command)
    print("MFA device ARN stored successfully in the AWS configuration.")

def get_temporary_credentials(mfa_device_arn, mfa_code):
    # Use the default profile to get session token
    command = f'aws sts get-session-token --serial-number {mfa_device_arn} --token-code {mfa_code} --profile default --output json'
    response = run_command(command)

    credentials = json.loads(response).get('Credentials')
    if not credentials:
        print("Error: Failed to retrieve temporary credentials.")
        exit(1)

    return credentials

def set_aws_credentials(access_key, secret_key, session_token):
    # Configure AWS CLI with temporary credentials using one line bash command
    command = f'aws configure set aws_access_key_id "{access_key}" --profile mfa && ' \
              f'aws configure set aws_secret_access_key "{secret_key}" --profile mfa && ' \
              f'aws configure set aws_session_token "{session_token}" --profile mfa &&' \
              f'aws configure set region us-east-2 --profile mfa'
    
    run_command(command)

    print("Temporary credentials have been set for the 'mfa' profile.")

def list_ec2_instances():
    # List EC2 instances the user has access to
    command = 'aws ec2 describe-instances --query "Reservations[*].Instances[*].[InstanceId,Tags[?Key==\'Name\'].Value|[0]]" --output json --profile mfa'
    response = run_command(command)
    instances = json.loads(response)

    if not instances:
        print("No instances available for this user.")
        return []

    # Display instance IDs and names (if present)
    for idx, instance in enumerate(instances, start=1):
        instance_id = instance[0][0] if instance[0] else 'Unknown'
        instance_name = instance[0][1] if instance[0] and len(instance[0]) > 1 else 'Unnamed'
        print(f"{idx}. Instance ID: {instance_id}, Name: {instance_name}")

    return instances


def is_port_available(port):
    """Check if a port is available on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('127.0.0.1', port)) != 0  # Returns 0 if the port is open, non-zero if closed

def start_ssm_session(instance_id):
    while True:
        # Prompt the user for the local port number
        local_port = input("Enter the local port number you want to use for the RDP session (1024-65535): ")

        # Validate the port number
        if not local_port.isdigit() or not (1024 <= int(local_port) <= 65535):
            print("Invalid input. Please enter a valid port number between 1024 and 65535.")
            continue  # Prompt again

        local_port = int(local_port)

        # Check if the port is available
        if not is_port_available(local_port):
            print(f"Port {local_port} is already in use. Please choose a different port.")
            continue  # Prompt again

        # Start an SSM session with port forwarding (RDP)
        command = f'aws ssm start-session --target {instance_id} --document-name AWS-StartPortForwardingSession --parameters "localPortNumber={local_port}, portNumber=3389" --region us-east-2 --profile mfa'

        # Run the command in a new terminal
        if os.name == 'nt':  # Windows
            subprocess.Popen(f'start cmd /k "{command}"', shell=True)
        else:  # Unix/Linux/Mac
            subprocess.Popen(f'gnome-terminal -- bash -c "{command}; exec bash"', shell=True)

        print(f"SSM session started for instance {instance_id}.")
        print(f"Use the following details to connect via RDP:")
        print(f"Host: 127.0.0.1")
        print(f"Local Port: {local_port}")
        print(f"Remote Port: 3389")
        print(f"In your RDP client, connect to localhost:{local_port}")
        break  # Exit the loop once a valid port is used

def main():
    # Try to get MFA device ARN from the AWS configuration
    mfa_device_arn = get_mfa_arn_from_aws_config()
    
    if not mfa_device_arn:
        # If not found, ask the user to input it and store it
        mfa_device_arn = input("Enter your MFA device ARN: ")
        store_mfa_arn_in_aws_config(mfa_device_arn)

    # Input MFA code
    mfa_code = input("Enter your MFA code: ")

    # Get temporary session credentials from AWS STS
    credentials = get_temporary_credentials(mfa_device_arn, mfa_code)

    access_key = credentials['AccessKeyId']
    secret_key = credentials['SecretAccessKey']
    session_token = credentials['SessionToken']
    expiration = credentials['Expiration']

    # Store the temporary credentials in the 'mfa' profile
    set_aws_credentials(access_key, secret_key, session_token)

    print(f"Credentials will expire on: {expiration}")

    # List EC2 instances the user can access
    instances = list_ec2_instances()

    if instances:
        # Let the user pick an instance
        choice = int(input(f"Enter the number of the instance you want to start an SSM session for (1-{len(instances)}): "))
        instance_id = instances[choice-1][0][0]

        # Start SSM session
        start_ssm_session(instance_id)

if __name__ == "__main__":
    main()
