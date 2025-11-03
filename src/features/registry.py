"""Feature registry for managing bot features."""
import logging
from typing import Dict, List

from src.features.base import BaseFeature

logger = logging.getLogger(__name__)


class FeatureRegistry:
    """Registry for managing bot features."""
    
    def __init__(self):
        """Initialize the registry."""
        self._features: Dict[str, BaseFeature] = {}
        logger.info("FeatureRegistry initialized")
    
    def register(self, feature: BaseFeature):
        """Register a feature.
        
        Args:
            feature: Feature instance to register
        """
        command = feature.command
        if command in self._features:
            logger.warning(f"Overwriting feature for command: {command}")
        
        self._features[command] = feature
        logger.info(f"Registered feature: {command}")
    
    def get(self, command: str) -> BaseFeature:
        """Get a feature by command.
        
        Args:
            command: Command name
            
        Returns:
            Feature instance
            
        Raises:
            KeyError: If feature not found
        """
        return self._features[command]
    
    def get_all(self) -> List[BaseFeature]:
        """Get all registered features.
        
        Returns:
            List of all features
        """
        return list(self._features.values())
    
    def has(self, command: str) -> bool:
        """Check if a feature is registered.
        
        Args:
            command: Command name
            
        Returns:
            True if feature is registered
        """
        return command in self._features

