"""Utility functions for AWS SSO Auditor."""

from typing import Dict, Any, List
from ..shared.utils import validate_account_id as base_validate_account_id


def validate_account_id(account_id: str) -> bool:
    """Validate AWS account ID format (wrapper for shared function)."""
    return base_validate_account_id(account_id)


def format_permission_set_arn(instance_arn: str, permission_set_name: str) -> str:
    """Format permission set ARN from instance ARN and name."""
    parts = instance_arn.split(':')
    if len(parts) >= 6:
        region = parts[3]
        account = parts[4]
        return f"arn:aws:sso:::{account}:permissionSet/{instance_arn.split('/')[-1]}/{permission_set_name}"
    return permission_set_name


def safe_get_nested(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """Safely get nested dictionary value."""
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def clean_aws_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Clean AWS API response by removing metadata."""
    cleaned = response.copy()
    # Remove common AWS metadata keys
    metadata_keys = ['ResponseMetadata', 'NextToken', 'IsTruncated']
    for key in metadata_keys:
        cleaned.pop(key, None)
    return cleaned


def format_timestamp(timestamp) -> str:
    """Format AWS timestamp for display."""
    if hasattr(timestamp, 'isoformat'):
        return timestamp.isoformat()
    return str(timestamp)