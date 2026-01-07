"""Utility functions"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def format_sources_for_display(sources: list, max_length: int = 200) -> list:
    """Format source documents for display"""
    formatted = []
    for i, source in enumerate(sources, 1):
        preview = source[:max_length] + "..." if len(source) > max_length else source
        formatted.append(f"[{i}] {preview}")
    return formatted


def validate_api_key(api_key: str) -> bool:
    """Validate OpenAI API key format"""
    if not api_key or api_key == "your_openai_api_key_here":
        return False
    return api_key.startswith("sk-") and len(api_key) > 20


def log_request(endpoint: str, data: Dict[str, Any]) -> None:
    """Log API request details"""
    logger.info(f"Request to {endpoint}: {data.get('question', 'N/A')[:50]}")


def log_response(endpoint: str, success: bool, error: str = None) -> None:
    """Log API response details"""
    if success:
        logger.info(f"Response from {endpoint}: Success")
    else:
        logger.error(f"Response from {endpoint}: Failed - {error}")
