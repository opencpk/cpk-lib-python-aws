"""AWS SSO Auditor - Professional AWS SSO auditing and compliance tool."""

from .auditor import AWSSSOAuditor
from .config import Config
from .exceptions import AWSSSOAuditorError, PermissionError, ConfigurationError
from .formatters import OutputFormatter
from .aws_client_manager import AWSClientManager

__version__ = "1.0.0"
__all__ = [
    "AWSSSOAuditor",
    "Config", 
    "AWSSSOAuditorError",
    "PermissionError",
    "ConfigurationError", 
    "OutputFormatter",
    "AWSClientManager",
]