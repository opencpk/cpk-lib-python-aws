"""CLI interface for AWS SSO Auditor."""

import argparse
import sys
import logging
from typing import List
from .auditor import AWSSSOAuditor
from .config import Config
from .formatters import OutputFormatter
from .exceptions import AWSSSOAuditorError


def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('aws_sso_auditor.log'),
            logging.StreamHandler()
        ]
    )


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        description='Audit AWS SSO Groups and Permission Sets for an account',
        prog='aws-sso-auditor'
    )
    
    parser.add_argument(
        'account_id', 
        help='AWS Account ID to audit'
    )
    
    parser.add_argument(
        '--output-format',
        choices=['json', 'yaml', 'both'],
        default='both',
        help='Output format (default: both)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='.',
        help='Output directory (default: current directory)'
    )
    
    parser.add_argument(
        '--aws-region',
        default='us-east-1',
        help='AWS region (default: us-east-1)'
    )
    
    parser.add_argument(
        '--aws-profile',
        help='AWS profile to use'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress console output, only save files'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--no-timestamp',
        action='store_true',
        help='Don\'t include timestamp in filenames'
    )
    
    return parser


def main(args: List[str] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # Setup logging
    setup_logging(parsed_args.debug)
    logger = logging.getLogger(__name__)
    
    # Create configuration
    output_formats = [parsed_args.output_format] if parsed_args.output_format != 'both' else ['json', 'yaml']
    
    config = Config(
        aws_region=parsed_args.aws_region,
        aws_profile=parsed_args.aws_profile,
        output_formats=output_formats,
        output_directory=parsed_args.output_dir,
        include_timestamp=not parsed_args.no_timestamp,
        debug=parsed_args.debug,
        quiet=parsed_args.quiet
    )
    
    try:
        # Initialize auditor and formatter
        auditor = AWSSSOAuditor(config)
        formatter = OutputFormatter(config)
        
        # Run audit
        logger.info(f"Starting audit for account: {parsed_args.account_id}")
        results = auditor.audit_account(parsed_args.account_id)
        
        # Save results
        saved_files = formatter.save_results(results, parsed_args.account_id)
        logger.info(f"Results saved to: {', '.join(saved_files)}")
        
        # Display results (unless quiet)
        if not config.quiet:
            formatter.display_results(results)
            print(f"✅ Results saved to: {', '.join(saved_files)}")
            
        logger.info("Audit completed successfully")
        return 0
        
    except AWSSSOAuditorError as e:
        logger.error(f"AWS SSO Auditor Error: {e}")
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())