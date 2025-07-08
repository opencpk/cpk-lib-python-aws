import pytest
import argparse
import logging
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import sys

from cpk_lib_python_aws.aws_access_auditor.cli import (
    setup_logging,
    create_parser,
    main
)
from cpk_lib_python_aws.aws_access_auditor.config import Config
from cpk_lib_python_aws.aws_access_auditor.exceptions import AWSSSOAuditorError


class TestSetupLogging:
    """Test the setup_logging function."""
    
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.logging.basicConfig')
    def test_setup_logging_default(self, mock_basic_config):
        """Test setup_logging with default parameters."""
        setup_logging()
        
        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args
        assert call_args[1]['level'] == logging.INFO
        assert "%(asctime)s - %(name)s - %(levelname)s - %(message)s" in call_args[1]['format']
    
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.logging.basicConfig')
    def test_setup_logging_debug(self, mock_basic_config):
        """Test setup_logging with debug enabled."""
        setup_logging(debug=True)
        
        call_args = mock_basic_config.call_args
        assert call_args[1]['level'] == logging.DEBUG
    
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.logging.basicConfig')
    def test_setup_logging_quiet(self, mock_basic_config):
        """Test setup_logging with quiet enabled."""
        setup_logging(quiet=True)
        
        call_args = mock_basic_config.call_args
        assert call_args[1]['level'] == logging.ERROR


class TestCreateParser:
    """Test the create_parser function."""
    
    def test_create_parser_basic(self):
        """Test that parser is created with correct structure."""
        parser = create_parser()
        
        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.prog == "aws-access-auditor"
    
    def test_parser_required_arguments(self):
        """Test parsing with required arguments only."""
        parser = create_parser()
        args = parser.parse_args(["123456789012"])
        
        assert args.account_id == "123456789012"
        assert args.output_format == "both"
        assert args.output_dir == "./aws-sso-audit-results"
        assert args.aws_region == "us-east-1"
        assert args.aws_profile is None
        assert args.quiet is False
        assert args.debug is False
        assert args.no_timestamp is False
    
    def test_parser_all_arguments(self):
        """Test parsing with all arguments provided."""
        parser = create_parser()
        args = parser.parse_args([
            "123456789012",
            "--output-format", "json",
            "--output-dir", "/tmp/results",
            "--aws-region", "us-west-2",
            "--aws-profile", "my-profile",
            "--quiet",
            "--debug",
            "--no-timestamp"
        ])
        
        assert args.account_id == "123456789012"
        assert args.output_format == "json"
        assert args.output_dir == "/tmp/results"
        assert args.aws_region == "us-west-2"
        assert args.aws_profile == "my-profile"
        assert args.quiet is True
        assert args.debug is True
        assert args.no_timestamp is True
    
    def test_parser_invalid_output_format(self):
        """Test parser rejects invalid output format."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(["123456789012", "--output-format", "invalid"])
    
    def test_parser_missing_account_id(self):
        """Test parser requires account_id."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args([])


class TestMain:
    """Test the main function."""
    
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.OutputFormatter')
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.AWSSSOAuditor')
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.OutputSink')
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.setup_logging')
    def test_main_success(self, mock_setup_logging, mock_output_sink, mock_auditor, mock_formatter):
        """Test successful main execution."""
        # Setup mocks
        mock_output_instance = Mock()
        mock_output_sink.return_value = mock_output_instance
        
        mock_auditor_instance = Mock()
        mock_auditor_instance.audit_account.return_value = {
            "metadata": {"account_id": "123456789012"},
            "summary": {"total_groups": 5, "total_permission_sets": 3}
        }
        mock_auditor.return_value = mock_auditor_instance
        
        mock_formatter_instance = Mock()
        mock_formatter_instance.save_results.return_value = ["file1.json", "file2.yaml"]
        mock_formatter.return_value = mock_formatter_instance
        
        # Run main
        result = main(["123456789012"])
        
        # Verify success
        assert result == 0
        mock_setup_logging.assert_called_once()
        mock_auditor_instance.audit_account.assert_called_once_with("123456789012")
        mock_formatter_instance.save_results.assert_called_once()
        mock_formatter_instance.display_results.assert_called_once()
    
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.OutputFormatter')
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.AWSSSOAuditor')
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.OutputSink')
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.setup_logging')
    def test_main_with_custom_args(self, mock_setup_logging, mock_output_sink, mock_auditor, mock_formatter):
        """Test main with custom arguments."""
        # Setup mocks
        mock_output_instance = Mock()
        mock_output_sink.return_value = mock_output_instance
        
        mock_auditor_instance = Mock()
        mock_auditor_instance.audit_account.return_value = {"metadata": {"account_id": "123456789012"}, "summary": {}}
        mock_auditor.return_value = mock_auditor_instance
        
        mock_formatter_instance = Mock()
        mock_formatter_instance.save_results.return_value = ["file1.json"]
        mock_formatter.return_value = mock_formatter_instance
        
        # Run main with custom args
        result = main([
            "123456789012",
            "--output-format", "json",
            "--aws-region", "eu-west-1",
            "--debug"
        ])
        
        # Verify
        assert result == 0
        mock_setup_logging.assert_called_once_with(True, False)  # debug=True, quiet=False
    
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.AWSSSOAuditor')
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.OutputSink')
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.setup_logging')
    def test_main_aws_access_auditor_error(self, mock_setup_logging, mock_output_sink, mock_auditor):
        """Test main handling AWSSSOAuditorError."""
        mock_output_instance = Mock()
        mock_output_sink.return_value = mock_output_instance
        
        mock_auditor.side_effect = AWSSSOAuditorError("Test error")
        
        result = main(["123456789012"])
        
        assert result == 1
        mock_output_instance.error.assert_called_with("AWS SSO Auditor Error: Test error")
    
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.AWSSSOAuditor')
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.OutputSink')
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.setup_logging')
    def test_main_unexpected_error(self, mock_setup_logging, mock_output_sink, mock_auditor):
        """Test main handling unexpected errors."""
        mock_output_instance = Mock()
        mock_output_sink.return_value = mock_output_instance
        
        mock_auditor.side_effect = Exception("Unexpected error")
        
        result = main(["123456789012"])
        
        assert result == 1
        mock_output_instance.error.assert_called_with("Unexpected error: Unexpected error")
    
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.OutputFormatter')
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.AWSSSOAuditor')
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.OutputSink')
    @patch('cpk_lib_python_aws.aws_access_auditor.cli.setup_logging')
    def test_main_config_creation(self, mock_setup_logging, mock_output_sink, mock_auditor, mock_formatter):
        """Test that Config is created correctly from CLI args."""
        mock_output_instance = Mock()
        mock_output_sink.return_value = mock_output_instance
        
        mock_auditor_instance = Mock()
        mock_auditor_instance.audit_account.return_value = {"metadata": {"account_id": "123456789012"}, "summary": {}}
        mock_auditor.return_value = mock_auditor_instance
        
        mock_formatter_instance = Mock()
        mock_formatter_instance.save_results.return_value = ["file1.json"]
        mock_formatter.return_value = mock_formatter_instance
        
        result = main([
            "123456789012",
            "--output-format", "yaml",
            "--output-dir", "/custom/dir",
            "--aws-region", "ap-southeast-1",
            "--aws-profile", "test-profile",
            "--no-timestamp",
            "--quiet"
        ])
        
        # Verify Config was created with correct parameters
        assert result == 0
        
        # Check that auditor was called with a config
        call_args = mock_auditor.call_args
        config = call_args[0][0]  # First argument should be config
        
        assert isinstance(config, Config)
        assert config.aws_region == "ap-southeast-1"
        assert config.aws_profile == "test-profile"
        assert config.output_formats == ["yaml"]
        assert config.output_directory == "/custom/dir"
        assert config.include_timestamp is False  # no-timestamp flag
        assert config.quiet is True
    
    def test_main_both_output_format(self):
        """Test that 'both' output format expands to json and yaml."""
        with patch('cpk_lib_python_aws.aws_access_auditor.cli.setup_logging'), \
             patch('cpk_lib_python_aws.aws_access_auditor.cli.OutputSink') as mock_output_sink, \
             patch('cpk_lib_python_aws.aws_access_auditor.cli.AWSSSOAuditor') as mock_auditor, \
             patch('cpk_lib_python_aws.aws_access_auditor.cli.OutputFormatter') as mock_formatter:
            
            mock_output_instance = Mock()
            mock_output_sink.return_value = mock_output_instance
            
            mock_auditor_instance = Mock()
            mock_auditor_instance.audit_account.return_value = {"metadata": {"account_id": "123456789012"}, "summary": {}}
            mock_auditor.return_value = mock_auditor_instance
            
            mock_formatter_instance = Mock()
            mock_formatter_instance.save_results.return_value = ["file1.json", "file2.yaml"]
            mock_formatter.return_value = mock_formatter_instance
            
            result = main(["123456789012", "--output-format", "both"])
            
            assert result == 0
            
            # Verify config has both formats
            call_args = mock_auditor.call_args
            config = call_args[0][0]
            assert set(config.output_formats) == {"json", "yaml"}
    
    def test_main_invalid_args(self):
        """Test main with invalid arguments."""
        # This should exit due to argparse error
        with pytest.raises(SystemExit):
            main(["123456789012", "--invalid-arg"])


# Integration-style test
class TestCLIIntegration:
    """Integration-style tests for CLI components."""
    
    def test_config_from_parser_args(self):
        """Test creating Config from parsed arguments."""
        parser = create_parser()
        args = parser.parse_args([
            "123456789012",
            "--output-format", "json",
            "--output-dir", "/test/dir",
            "--aws-region", "us-west-2",
            "--debug",
            "--no-timestamp"
        ])
        
        # This mimics what main() does with the args
        output_formats = [args.output_format] if args.output_format != "both" else ["json", "yaml"]
        
        config = Config(
            aws_region=args.aws_region,
            aws_profile=args.aws_profile,
            output_formats=output_formats,
            output_directory=args.output_dir,
            include_timestamp=not args.no_timestamp,
            debug=args.debug,
            quiet=args.quiet,
        )
        
        assert config.aws_region == "us-west-2"
        assert config.output_formats == ["json"]
        assert config.output_directory == "/test/dir"
        assert config.include_timestamp is False
        assert config.debug is True
        assert config.quiet is False