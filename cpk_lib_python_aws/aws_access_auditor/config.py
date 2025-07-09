# -*- coding: utf-8 -*-
"""Configuration management for AWS SSO Auditor."""

import os
from dataclasses import dataclass
from typing import List, Optional

from .exceptions import ConfigurationError


@dataclass
class Config:
    """Configuration for AWS SSO Auditor."""

    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_profile: Optional[str] = None
    timeout: int = 30

    # Output Configuration
    output_formats: List[str] = None
    output_directory: str = "."
    include_timestamp: bool = True

    # Behavior Configuration
    debug: bool = False
    quiet: bool = False

    def __post_init__(self):
        """Initialize configuration from environment variables."""
        if self.output_formats is None:
            self.output_formats = ["json", "yaml"]

        # Override with environment variables
        self.aws_region = os.getenv("AWS_REGION", self.aws_region)
        self.aws_profile = os.getenv("AWS_PROFILE", self.aws_profile)

        self.output_directory = os.getenv("AWS_ACCESS_AUDITOR_OUTPUT_DIR", self.output_directory)
        if os.getenv("AWS_ACCESS_AUDITOR_DEBUG", "").lower() == "true":
            self.debug = True
        if os.getenv("AWS_ACCESS_AUDITOR_QUIET", "").lower() == "true":
            self.quiet = True

    def validate(self) -> None:
        """Validate configuration settings."""
        valid_formats = ["json", "yaml", "both"]
        for fmt in self.output_formats:
            if fmt not in valid_formats:
                raise ConfigurationError(
                    f"Invalid output format: {fmt}. Must be one of {valid_formats}"
                )

        if self.timeout <= 0:
            raise ConfigurationError("Timeout must be greater than 0")
