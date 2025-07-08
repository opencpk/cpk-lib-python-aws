# -*- coding: utf-8 -*-
"""Output formatting utilities for AWS SSO Auditor."""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import yaml

from .config import Config

logger = logging.getLogger(__name__)


class OutputFormatter:
    """Handles output formatting and file operations."""

    def __init__(self, config: Config, output_sink=None):
        """Initialize formatter with configuration and optional output sink."""
        self.config = config
        self.output_sink = output_sink
        self._ensure_output_directory()

    def _ensure_output_directory(self) -> None:
        """Ensure output directory exists."""
        try:
            os.makedirs(self.config.output_directory, exist_ok=True)
            logger.debug("Output directory ensured: %s", self.config.output_directory)
        except Exception as e:
            logger.error(
                "Failed to create output directory %s: %s", self.config.output_directory, e
            )
            raise

    def save_results(self, data: Dict[str, Any], account_id: str) -> List[str]:
        """Save results to files based on configuration."""
        saved_files = []

        timestamp = (
            datetime.now().strftime("%Y%m%d_%H%M%S") if self.config.include_timestamp else ""
        )

        for format_type in self.config.output_formats:
            if format_type in ["json", "both"]:
                json_file = self._save_json(data, account_id, timestamp)
                saved_files.append(json_file)

            if format_type in ["yaml", "both"]:
                yaml_file = self._save_yaml(data, account_id, timestamp)
                saved_files.append(yaml_file)

        return saved_files

    def _save_json(self, data: Dict[str, Any], account_id: str, timestamp: str) -> str:
        """Save data as JSON file."""
        filename_parts = ["aws_sso_audit", account_id]
        if timestamp:
            filename_parts.append(timestamp)
        filename = "_".join(filename_parts) + ".json"

        filepath = os.path.join(self.config.output_directory, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

        logger.info("JSON results saved to: %s", filepath)
        return filepath

    def _save_yaml(self, data: Dict[str, Any], account_id: str, timestamp: str) -> str:
        """Save data as YAML file."""
        filename_parts = ["aws_sso_audit", account_id]
        if timestamp:
            filename_parts.append(timestamp)
        filename = "_".join(filename_parts) + ".yaml"

        filepath = os.path.join(self.config.output_directory, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        logger.info("YAML results saved to: %s", filepath)
        return filepath

    def display_results(self, data: Dict[str, Any]) -> None:
        """Display results to console using output sink if available."""
        if self.config.quiet:
            return

        if self.output_sink:
            # Use output sink for clean display
            self.output_sink.separator()
            self.output_sink.info("AWS SSO AUDIT RESULTS")
            self.output_sink.separator()
            self.output_sink.print_raw(json.dumps(data, indent=2, default=str))
        else:
            # Fallback to direct print (backward compatibility)
            print("\n" + "=" * 80)
            print("AWS SSO AUDIT RESULTS")
            print("=" * 80)
            print(json.dumps(data, indent=2, default=str))

    def format_summary(self, data: Dict[str, Any]) -> str:
        """Format a summary of audit results."""
        summary = data.get("summary", {})
        metadata = data.get("metadata", {})

        lines = [
            "📊 AWS SSO Audit Summary",
            f"🆔 Account: {metadata.get('account_id', 'Unknown')}",
            f"📅 Generated: {metadata.get('generated_at', 'Unknown')}",
            f"👥 Groups: {summary.get('total_groups', 0)}",
            f"🔐 Permission Sets: {summary.get('total_permission_sets', 0)}",
            f"🔗 Assignments: {summary.get('total_assignments', 0)}",
        ]

        return "\n".join(lines)
