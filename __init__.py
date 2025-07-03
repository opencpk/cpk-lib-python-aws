"""CPK Python AWS Library - Collection of AWS tools and utilities."""

# AWS SSO Auditor Package
from .aws_sso_auditor import AWSSSOAuditor
from .aws_sso_auditor.config import Config as SSOConfig
from .aws_sso_auditor.exceptions import AWSSSOAuditorError

# Shared utilities
from .shared import AWSBaseClient, AWSError

__version__ = "1.0.0"

# Package exports
__all__ = [
    # AWS SSO Auditor
    "AWSSSOAuditor",
    "SSOConfig", 
    "AWSSSOAuditorError",
    
    # Shared utilities
    "AWSBaseClient",
    "AWSError",
]