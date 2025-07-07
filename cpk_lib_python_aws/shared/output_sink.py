# -*- coding: utf-8 -*-
"""Shared output sink for managing console output across AWS tools."""

import sys


class OutputSink:
    """Manages console output with different verbosity levels across AWS tools."""

    def __init__(self, quiet: bool = False, debug: bool = False):
        """Initialize output sink with verbosity settings."""
        self.quiet = quiet
        self.debug = debug

    def info(self, message: str) -> None:
        """Print informational message (suppressed in quiet mode)."""
        if not self.quiet:
            print(message)

    def success(self, message: str) -> None:
        """Print success message (suppressed in quiet mode)."""
        if not self.quiet:
            print(f"✅ {message}")

    def warning(self, message: str) -> None:
        """Print warning message (always shown unless quiet)."""
        if not self.quiet:
            print(f"⚠️  {message}")

    def error(self, message: str) -> None:
        """Print error message (always shown, even in quiet mode)."""
        print(f"❌ {message}", file=sys.stderr)

    def debug_info(self, message: str) -> None:
        """Print debug message (only in debug mode)."""
        if self.debug and not self.quiet:
            print(f"🔍 {message}")

    def progress(self, message: str) -> None:
        """Print progress message (only in debug mode)."""
        if self.debug and not self.quiet:
            print(f"⏳ {message}")

    def separator(self, char: str = "=", length: int = 80) -> None:
        """Print separator line (suppressed in quiet mode)."""
        if not self.quiet:
            print(char * length)

    def print_raw(self, message: str, file=None) -> None:
        """Print raw message without formatting (respects quiet mode for stdout)."""
        if file == sys.stderr:
            # Always print to stderr (errors)
            print(message, file=file)
        elif not self.quiet:
            # Print to stdout only if not quiet
            print(message, file=file)

    def metric(self, name: str, value: str) -> None:
        """Print metric information (debug mode only)."""
        if self.debug and not self.quiet:
            print(f"📊 {name}: {value}")

    def timing(self, operation: str, duration: float) -> None:
        """Print timing information (debug mode only)."""
        if self.debug and not self.quiet:
            print(f"⏱️  {operation}: {duration:.2f}s")
