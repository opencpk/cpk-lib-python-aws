"""Custom exceptions for AWS SSO Auditor."""

from ..shared.exceptions import AWSError


class AWSSSOAuditorError(AWSError):
    """Base exception for AWS SSO Auditor."""
    pass


class PermissionError(AWSSSOAuditorError):
    """Raised when insufficient AWS permissions."""
    pass


class ConfigurationError(AWSSSOAuditorError):
    """Raised when configuration is invalid."""
    pass


class SSOInstanceNotFoundError(AWSSSOAuditorError):
    """Raised when no SSO instance is found."""
    pass


class AWSClientError(AWSSSOAuditorError):
    """Raised when AWS client initialization fails."""
    pass