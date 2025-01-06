"""Logging utilities"""

from loguru import logger
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union
import json
from datetime import datetime

class LoggerConfig:
    def __init__(
        self,
        log_path: str = "logs",
        retention: str = "1 week",
        rotation: str = "100 MB",
        format: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    ):
        self.log_path = Path(log_path)
        self.retention = retention
        self.rotation = rotation
        self.format = format
        self.log_path.mkdir(parents=True, exist_ok=True)

    def setup_logger(self) -> None:
        """Configure loguru logger with console and file handlers."""
        # Remove default handler
        logger.remove()

        # Add console handler with custom format
        logger.add(
            sys.stdout,
            format=self.format,
            level="INFO",
            colorize=True
        )

        # Add file handler for all logs
        logger.add(
            self.log_path / "riddler_{time}.log",
            format=self.format,
            level="DEBUG",
            rotation=self.rotation,
            retention=self.retention,
            compression="zip"
        )

        # Add file handler for errors only
        logger.add(
            self.log_path / "riddler_errors_{time}.log",
            format=self.format,
            level="ERROR",
            rotation=self.rotation,
            retention=self.retention,
            compression="zip",
            filter=lambda record: record["level"].name == "ERROR"
        )

class StructuredLogger:
    def __init__(self):
        self.logger = logger

    def _format_extra(self, extra: Optional[Dict[str, Any]] = None) -> str:
        """Format extra fields as JSON string."""
        if extra:
            return f" | extra={json.dumps(extra)}"
        return ""

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.logger.info(f"{message}{self._format_extra(extra)}")

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.logger.debug(f"{message}{self._format_extra(extra)}")

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.logger.warning(f"{message}{self._format_extra(extra)}")

    def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.logger.error(f"{message}{self._format_extra(extra)}")

    def exception(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.logger.exception(f"{message}{self._format_extra(extra)}")
        
    def api_call(
        self,
        service: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an API call.
        
        Args:
            service: Service name (e.g., 'Pexels', 'ElevenLabs')
            endpoint: API endpoint
            params: Request parameters
        """
        self.info(
            f"API call to {service} ({endpoint})",
            extra={
                "service": service,
                "endpoint": endpoint,
                "params": params
            }
        )
        
    def cache_operation(
        self,
        operation: str,
        key: str,
        success: bool
    ) -> None:
        """Log a cache operation.
        
        Args:
            operation: Operation type ('get' or 'put')
            key: Cache key
            success: Whether the operation was successful
        """
        self.debug(
            f"Cache {operation}: {'hit' if success else 'miss'}",
            extra={
                "operation": operation,
                "key": key,
                "success": success
            }
        )
        
    def video_processing(
        self,
        operation: str,
        input_path: str,
        output_path: str,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Log a video processing operation.
        
        Args:
            operation: Operation type (e.g., 'resize', 'merge')
            input_path: Input video path
            output_path: Output video path
            success: Whether the operation was successful
            error: Optional error message
        """
        if success:
            self.info(
                f"Video {operation} successful",
                extra={
                    "operation": operation,
                    "input": input_path,
                    "output": output_path
                }
            )
        else:
            self.error(
                f"Video {operation} failed",
                extra={
                    "operation": operation,
                    "input": input_path,
                    "output": output_path,
                    "error": error
                }
            )

# Initialize logger with default configuration
logger_config = LoggerConfig()
logger_config.setup_logger()
structured_logger = StructuredLogger()

# Export the configured logger instance
log = structured_logger 