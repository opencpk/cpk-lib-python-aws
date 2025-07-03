"""Shared AWS utility functions."""

import re
from typing import List


def validate_account_id(account_id: str) -> bool:
    """Validate AWS account ID format."""
    if not account_id:
        return False
    
    # AWS account IDs are 12-digit numbers
    pattern = r'^\d{12}$'
    return bool(re.match(pattern, account_id))


def get_aws_regions() -> List[str]:
    """Get list of AWS regions."""
    import boto3
    
    try:
        ec2 = boto3.client('ec2', region_name='us-east-1')
        response = ec2.describe_regions()
        return [region['RegionName'] for region in response['Regions']]
    except Exception:
        # Fallback to common regions if API call fails
        return [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-west-2', 'eu-central-1',
            'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1'
        ]


def format_arn(service: str, region: str, account_id: str, resource: str) -> str:
    """Format AWS ARN."""
    return f"arn:aws:{service}:{region}:{account_id}:{resource}"