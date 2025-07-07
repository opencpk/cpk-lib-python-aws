# -*- coding: utf-8 -*-
"""AWS SSO Auditor - Professional AWS SSO auditing and compliance tool."""

from ..shared import OutputSink
from .auditor import AWSSSOAuditor
from .aws_client_manager import AWSClientManager
from .config import Config
from .exceptions import (
    AWSSSOAuditorError,
    ConfigurationError,
    InsufficientPermissionsError,
)
from .formatters import OutputFormatter

__version__ = "1.0.0"
__all__ = [
    "AWSSSOAuditor",
    "Config",
    "AWSSSOAuditorError",
    "InsufficientPermissionsError",  # Keep this as is since it's defined in your local exceptions
    "ConfigurationError",
    "OutputFormatter",
    "AWSClientManager",
    "OutputSink",
]
