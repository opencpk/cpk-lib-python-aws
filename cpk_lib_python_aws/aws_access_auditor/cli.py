# -*- coding: utf-8 -*-
"""CLI interface for AWS SSO Auditor."""

import argparse
import logging
import sys
from typing import List

from ..shared import OutputSink  # <-- CHANGED: Import from shared instead of local
from .auditor import AWSSSOAuditor
from .config import Config
from .exceptions import AWSSSOAuditorError
from .formatters import OutputFormatter


def setup_logging(debug: bool = False, quiet: bool = False) -> None:
    """Setup logging configuration."""
    if quiet:
        level = logging.ERROR
    elif debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("aws_access_auditor.log"), logging.StreamHandler()],
    )


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Audit AWS SSO Groups and Permission Sets for an account",
        prog="aws-access-auditor",
    )

    parser.add_argument("account_id", help="AWS Account ID to audit")

    parser.add_argument(
        "--output-format",
        choices=["json", "yaml", "both"],
        default="both",
        help="Output format (default: both)",
    )

    parser.add_argument(
        "--output-dir",
        default="./aws-sso-audit-results",
        help="Output directory (default: ./aws-sso-audit-results)",
    )

    parser.add_argument("--aws-region", default="us-east-1", help="AWS region (default: us-east-1)")

    parser.add_argument("--aws-profile", help="AWS profile to use")

    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress console output, only save files"
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    parser.add_argument(
        "--no-timestamp", action="store_true", help="Don't include timestamp in filenames"
    )

    return parser


def main(args: List[str] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Setup logging
    setup_logging(parsed_args.debug, parsed_args.quiet)
    logger = logging.getLogger(__name__)

    # Create configuration
    output_formats = (
        [parsed_args.output_format] if parsed_args.output_format != "both" else ["json", "yaml"]
    )

    config = Config(
        aws_region=parsed_args.aws_region,
        aws_profile=parsed_args.aws_profile,
        output_formats=output_formats,
        output_directory=parsed_args.output_dir,
        include_timestamp=not parsed_args.no_timestamp,
        debug=parsed_args.debug,
        quiet=parsed_args.quiet,
    )

    # Create output sink for clean console management
    output = OutputSink(config.quiet, config.debug)

    try:
        # Initialize auditor and formatter
        output.progress("Initializing AWS SSO Auditor...")
        auditor = AWSSSOAuditor(config, output)
        formatter = OutputFormatter(config, output)

        # Run audit
        output.info(f"Starting audit for account: {parsed_args.account_id}")
        logger.info("Starting audit for account: %s", parsed_args.account_id)

        results = auditor.audit_account(parsed_args.account_id)

        # Save results
        output.progress("Saving results to files...")
        saved_files = formatter.save_results(results, parsed_args.account_id)
        logger.info("Results saved to: %s", ", ".join(saved_files))

        # Display results using output sink
        formatter.display_results(results)
        output.success(f"Results saved to: {', '.join(saved_files)}")

        # Show summary in debug mode
        if config.debug:
            summary = results.get("summary", {})
            output.debug_info(
                f"Processed {summary.get('total_groups', 0)} groups, "
                f"{summary.get('total_permission_sets', 0)} permission sets"
            )

        logger.info("Audit completed successfully")
        return 0

    except AWSSSOAuditorError as e:
        logger.error("AWS SSO Auditor Error: %s", e)
        output.error(f"AWS SSO Auditor Error: {e}")
        return 1
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        output.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
