# -*- coding: utf-8 -*-
"""Custom exceptions for AWS SSO Auditor."""

from ..shared.exceptions import AWSError


class AWSSSOAuditorError(AWSError):
    """Base exception for AWS SSO Auditor."""


class InsufficientPermissionsError(AWSSSOAuditorError):
    """Raised when insufficient AWS permissions."""


class ConfigurationError(AWSSSOAuditorError):
    """Raised when configuration is invalid."""


class SSOInstanceNotFoundError(AWSSSOAuditorError):
    """Raised when no SSO instance is found."""


class AWSClientError(AWSSSOAuditorError):
    """Raised when AWS client initialization fails."""
