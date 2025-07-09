# -*- coding: utf-8 -*-
"""CPK Python AWS Library - Comprehensive AWS utilities and tools."""

# Import SSO Auditor components
from .aws_access_auditor import AWSSSOAuditor
from .aws_access_auditor import Config as SSOConfig

# Import shared components
from .shared import AWSBaseClient, AWSError, OutputSink

__version__ = "1.0.0"
__all__ = [
    # Shared components
    "OutputSink",
    "AWSBaseClient",
    "AWSError",
    # SSO Auditor components
    "AWSSSOAuditor",
    "SSOConfig",
]
