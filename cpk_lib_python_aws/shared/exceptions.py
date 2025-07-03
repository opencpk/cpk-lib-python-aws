"""Shared AWS exceptions."""


class AWSError(Exception):
    """Base AWS error for all AWS-related exceptions."""
    pass


class CredentialsError(AWSError):
    """Raised when AWS credentials are invalid or missing."""
    pass


class RegionError(AWSError):
    """Raised when AWS region is invalid or unsupported."""
    pass


class PermissionsError(AWSError):
    """Raised when insufficient AWS permissions."""
    pass