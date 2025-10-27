"""Error logging and crash recovery utilities"""
import logging
import sys
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class ErrorLogger:
    """Centralized error logging system"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize error logger (singleton)"""
        if self._initialized:
            return

        # Create logs directory
        self.logs_dir = Path.home() / '.decoder_tool' / 'logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.log_file = self.logs_dir / f'decoder_tool_{datetime.now().strftime("%Y%m%d")}.log'

        # Create logger
        self.logger = logging.getLogger('DecoderTool')
        self.logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Console handler (only warnings and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self._initialized = True

        self.logger.info("=" * 60)
        self.logger.info("Decoder Tool Started")
        self.logger.info(f"Log file: {self.log_file}")
        self.logger.info("=" * 60)

    def log_exception(self, exc: Exception, context: str = ""):
        """
        Log an exception with full traceback

        Args:
            exc: Exception object
            context: Additional context about where error occurred
        """
        exc_info = sys.exc_info()
        tb_str = ''.join(traceback.format_exception(*exc_info))

        error_msg = f"Exception in {context}: {str(exc)}\n{tb_str}"
        self.logger.error(error_msg)

        return error_msg

    def log_error(self, message: str, context: str = ""):
        """
        Log an error message

        Args:
            message: Error message
            context: Additional context
        """
        full_msg = f"[{context}] {message}" if context else message
        self.logger.error(full_msg)

    def log_warning(self, message: str, context: str = ""):
        """
        Log a warning message

        Args:
            message: Warning message
            context: Additional context
        """
        full_msg = f"[{context}] {message}" if context else message
        self.logger.warning(full_msg)

    def log_info(self, message: str, context: str = ""):
        """
        Log an info message

        Args:
            message: Info message
            context: Additional context
        """
        full_msg = f"[{context}] {message}" if context else message
        self.logger.info(full_msg)

    def log_debug(self, message: str, context: str = ""):
        """
        Log a debug message

        Args:
            message: Debug message
            context: Additional context
        """
        full_msg = f"[{context}] {message}" if context else message
        self.logger.debug(full_msg)

    def get_recent_errors(self, lines: int = 50) -> str:
        """
        Get recent error log entries

        Args:
            lines: Number of lines to retrieve

        Returns:
            Recent log entries as string
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except Exception:
            return "Unable to read log file"

    def get_log_file_path(self) -> Path:
        """Get path to current log file"""
        return self.log_file

    def cleanup_old_logs(self, days: int = 7):
        """
        Delete log files older than specified days

        Args:
            days: Number of days to keep logs
        """
        try:
            cutoff = datetime.now().timestamp() - (days * 86400)

            for log_file in self.logs_dir.glob('decoder_tool_*.log'):
                if log_file.stat().st_mtime < cutoff:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log file: {log_file.name}")
        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {str(e)}")


class CrashRecovery:
    """Handles crash recovery and auto-save"""

    def __init__(self, save_dir: Path = None):
        """
        Initialize crash recovery

        Args:
            save_dir: Directory to store recovery files
        """
        if save_dir is None:
            save_dir = Path.home() / '.decoder_tool' / 'recovery'

        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.recovery_file = self.save_dir / 'recovery_state.json'
        self.logger = ErrorLogger()

    def save_state(self, state: dict):
        """
        Save application state for recovery

        Args:
            state: Dictionary with application state
        """
        try:
            state['timestamp'] = datetime.now().isoformat()
            state['version'] = '2.3.1'

            with open(self.recovery_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

            self.logger.log_debug("Application state saved", "CrashRecovery")

        except Exception as e:
            self.logger.log_error(f"Failed to save state: {str(e)}", "CrashRecovery")

    def load_state(self) -> Optional[dict]:
        """
        Load saved application state

        Returns:
            Dictionary with saved state or None if not available
        """
        try:
            if not self.recovery_file.exists():
                return None

            with open(self.recovery_file, 'r', encoding='utf-8') as f:
                state = json.load(f)

            self.logger.log_info("Recovery state loaded", "CrashRecovery")
            return state

        except Exception as e:
            self.logger.log_error(f"Failed to load state: {str(e)}", "CrashRecovery")
            return None

    def clear_state(self):
        """Clear saved recovery state"""
        try:
            if self.recovery_file.exists():
                self.recovery_file.unlink()
                self.logger.log_debug("Recovery state cleared", "CrashRecovery")
        except Exception as e:
            self.logger.log_error(f"Failed to clear state: {str(e)}", "CrashRecovery")

    def has_recovery_state(self) -> bool:
        """Check if recovery state exists"""
        return self.recovery_file.exists()


# Global logger instance
_error_logger = None


def get_logger() -> ErrorLogger:
    """Get global error logger instance"""
    global _error_logger
    if _error_logger is None:
        _error_logger = ErrorLogger()
    return _error_logger
