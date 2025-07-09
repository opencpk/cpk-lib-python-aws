# -*- coding: utf-8 -*-
"""Shared AWS exceptions."""


class AWSError(Exception):
    """Base AWS error for all AWS-related exceptions."""


class CredentialsError(AWSError):
    """Raised when AWS credentials are invalid or missing."""


class RegionError(AWSError):
    """Raised when AWS region is invalid or unsupported."""


class PermissionsError(AWSError):
    """Raised when insufficient AWS permissions."""
