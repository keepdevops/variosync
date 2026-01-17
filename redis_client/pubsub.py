"""
Redis pub/sub operations.
"""
from typing import Any, Dict
import json

from logger import get_logger

logger = get_logger()


class RedisPubSub:
    """Redis pub/sub operations."""
    
    def __init__(self, client):
        """Initialize with Redis client."""
        self.client = client
    
    def publish(self, channel: str, message: Dict[str, Any]) -> int:
        """Publish message to channel."""
        try:
            serialized = json.dumps(message)
            return self.client.publish(channel, serialized)
        except Exception as e:
            logger.error(f"Error publishing to channel {channel}: {e}")
            return 0
    
    def subscribe(self, channel: str, handler):
        """Subscribe to channel and handle messages."""
        try:
            pubsub = self.client.pubsub()
            pubsub.subscribe(channel)
            
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        handler(data)
                    except Exception as e:
                        logger.error(f"Error handling message: {e}")
        except Exception as e:
            logger.error(f"Error subscribing to channel {channel}: {e}")
