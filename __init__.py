# -*- coding: utf-8 -*-
"""CPK Python AWS Library - Comprehensive AWS utilities and tools."""

from .aws_sso_auditor import AWSSSOAuditor
from .aws_sso_auditor import Config as SSOConfig
from .shared import AWSBaseClient, AWSError, OutputSink

__version__ = "1.0.0"
__all__ = [
    "AWSSSOAuditor",
    "SSOConfig",
    "OutputSink",
    "AWSBaseClient",
    "AWSError",
]
