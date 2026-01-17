"""
NiceGUI App Shared State Management
Manages shared UI state across modules.
"""
from typing import Optional, Dict, Any, List
from threading import Lock

from logger import get_logger

logger = get_logger()


class UIState:
    """Manages shared UI state across NiceGUI app modules."""
    
    def __init__(self):
        """Initialize state manager."""
        self._lock = Lock()
        self._state: Dict[str, Any] = {}
        self._ui_components: Dict[str, Any] = {}
        self._user_preferences: Dict[str, Any] = {}
        
    def set_component(self, key: str, component: Any) -> None:
        """Store a UI component reference."""
        with self._lock:
            self._ui_components[key] = component
            logger.debug(f"Stored UI component: {key}")
    
    def get_component(self, key: str) -> Optional[Any]:
        """Get a UI component reference."""
        with self._lock:
            return self._ui_components.get(key)
    
    def remove_component(self, key: str) -> None:
        """Remove a UI component reference."""
        with self._lock:
            if key in self._ui_components:
                del self._ui_components[key]
                logger.debug(f"Removed UI component: {key}")
    
    def set_state(self, key: str, value: Any) -> None:
        """Set a state value."""
        with self._lock:
            self._state[key] = value
            logger.debug(f"Set state: {key} = {value}")
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        with self._lock:
            return self._state.get(key, default)
    
    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update multiple state values at once."""
        with self._lock:
            self._state.update(updates)
            logger.debug(f"Updated state: {list(updates.keys())}")
    
    def set_preference(self, key: str, value: Any) -> None:
        """Set a user preference."""
        with self._lock:
            self._user_preferences[key] = value
            logger.debug(f"Set preference: {key} = {value}")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        with self._lock:
            return self._user_preferences.get(key, default)
    
    def clear(self) -> None:
        """Clear all state (useful for testing or reset)."""
        with self._lock:
            self._state.clear()
            self._ui_components.clear()
            self._user_preferences.clear()
            logger.debug("Cleared all state")
    
    def get_all_components(self) -> Dict[str, Any]:
        """Get all UI component references."""
        with self._lock:
            return self._ui_components.copy()
    
    def get_all_state(self) -> Dict[str, Any]:
        """Get all state values."""
        with self._lock:
            return self._state.copy()
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all user preferences."""
        with self._lock:
            return self._user_preferences.copy()


# Global state instance
_state_instance: Optional[UIState] = None


def get_state() -> UIState:
    """Get or create the global state instance."""
    global _state_instance
    if _state_instance is None:
        _state_instance = UIState()
    return _state_instance


def reset_state() -> None:
    """Reset the global state instance (useful for testing)."""
    global _state_instance
    _state_instance = None
