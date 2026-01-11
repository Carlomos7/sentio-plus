"""
Logging configuration for ETL pipeline using dictConfig.
"""
import json
import logging
import logging.config
from pathlib import Path
from src.config.settings import get_settings

settings = get_settings()
APP_NAME = settings.app_name

def setup_logging() -> logging.Logger:
    """
    Configure logging using JSON config file.
    Environment differences handled by settings (log_level, log_to_file).
    """
    
    # Load JSON config
    config_file = settings.logging_config_file
    
    if not config_file.exists():
        raise FileNotFoundError(f"Logging configuration not found: {config_file}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Apply log level from settings to all loggers
    for logger_config in config.get('loggers', {}).values():
        logger_config['level'] = settings.log_level
    
    # Update log file paths
    if settings.log_to_file:
        settings.log_dir.mkdir(parents=True, exist_ok=True)
        
        for handler in config.get('handlers', {}).values():
            if 'filename' in handler:
                filename = Path(handler['filename']).name
                handler['filename'] = str(settings.log_dir / filename)
    else:
        # Remove file handlers if log_to_file is False
        config['handlers'] = {
            k: v for k, v in config.get('handlers', {}).items()
            if v.get('class') != 'logging.handlers.RotatingFileHandler'
        }
        
        # Update loggers to only use console
        for logger_config in config.get('loggers', {}).values():
            logger_config['handlers'] = ['console']
    
    # Apply the configuration
    logging.config.dictConfig(config)
    
    # Get and return the logger
    logger = logging.getLogger(settings.app_name)
    logger.info(f"Logging initialized - Level: {settings.log_level}")
    
    return logger


def get_logger(name: str = APP_NAME, module: str = None) -> logging.Logger:
    """
    Get a logger for a specific module or the default logger.
    Args:
        name: The name of the logger.
        module: The name of the module to get a logger for.
    Returns:
        A logger for the specific module or the default logger.
    """
    if module:
        return logging.getLogger(name).getChild(module)
    else:
        return logging.getLogger(name)