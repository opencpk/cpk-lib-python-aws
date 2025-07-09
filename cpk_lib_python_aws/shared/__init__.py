# -*- coding: utf-8 -*-
"""Shared AWS utilities and base classes."""

from .aws_base import AWSBaseClient
from .exceptions import AWSError, CredentialsError, PermissionsError, RegionError
from .output_sink import OutputSink
from .utils import get_aws_regions, validate_account_id

__all__ = [
    "AWSBaseClient",
    "AWSError",
    "CredentialsError",
    "RegionError",
    "PermissionsError",  # This matches your exceptions.py
    "validate_account_id",
    "get_aws_regions",
    "OutputSink",
]
