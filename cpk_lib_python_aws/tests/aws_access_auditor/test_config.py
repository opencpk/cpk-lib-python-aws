# -*- coding: utf-8 -*-
"""Tests for AWS Access Auditor configuration module."""
import os

import pytest

from cpk_lib_python_aws.aws_access_auditor.config import Config
from cpk_lib_python_aws.aws_access_auditor.exceptions import ConfigurationError


def test_default_config_values():
    """Test that default configuration values are set correctly."""
    config = Config()
    assert config.aws_region == "us-east-1"
    assert config.output_formats == ["json", "yaml"]
    assert config.output_directory == "."
    assert config.include_timestamp is True
    assert config.debug is False
    assert config.quiet is False
    assert config.timeout == 30
    assert config.aws_profile is None


def test_config_validation_valid_formats():
    """Test that valid output formats pass validation."""
    config = Config(output_formats=["json"])
    config.validate()

    config = Config(output_formats=["yaml"])
    config.validate()

    config = Config(output_formats=["both"])
    config.validate()


def test_config_validation_invalid_format():
    """Test that invalid output formats raise ConfigurationError."""
    config = Config(output_formats=["invalid"])
    with pytest.raises(ConfigurationError, match="Invalid output format: invalid"):
        config.validate()


def test_environment_variable_override():
    """Test that environment variables override default values."""
    # Set environment variables
    os.environ["AWS_REGION"] = "eu-west-1"
    os.environ["AWS_ACCESS_AUDITOR_DEBUG"] = "true"
    os.environ["AWS_ACCESS_AUDITOR_QUIET"] = "true"

    try:
        config = Config()
        assert config.aws_region == "eu-west-1"
        assert config.debug is True
        assert config.quiet is True
    finally:
        # Clean up environment variables
        os.environ.pop("AWS_REGION", None)
        os.environ.pop("AWS_ACCESS_AUDITOR_DEBUG", None)
        os.environ.pop("AWS_ACCESS_AUDITOR_QUIET", None)


def test_constructor_overrides():
    """Test that constructor parameters override defaults."""
    config = Config(
        aws_region="ap-southeast-1", output_directory="/tmp/test", debug=True, timeout=60
    )
    assert config.aws_region == "ap-southeast-1"
    assert config.output_directory == "/tmp/test"
    assert config.debug is True
    assert config.timeout == 60
