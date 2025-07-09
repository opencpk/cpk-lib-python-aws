# -*- coding: utf-8 -*-
"""CPK Python AWS Library - Comprehensive AWS utilities and tools."""

from cpk_lib_python_aws.aws_access_auditor import AWSSSOAuditor
from cpk_lib_python_aws.aws_access_auditor import Config as SSOConfig
from cpk_lib_python_aws.shared import AWSBaseClient, AWSError, OutputSink

__version__ = "1.0.0"
__all__ = [
    "AWSSSOAuditor",
    "SSOConfig",
    "OutputSink",
    "AWSBaseClient",
    "AWSError",
]
