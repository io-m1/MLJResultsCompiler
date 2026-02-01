"""
Universal Platform Adapter System
Enables seamless integration with any communication/collaboration platform
Telegram, Slack, Discord, Teams, email, webhooks, etc.
"""

import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class PlatformMessage:
    """Unified message format across all platforms"""
    platform: str
    user_id: str
    username: str
    message_id: str
    content: str
    timestamp: datetime
    attachments: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self):
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class PlatformResponse:
    """Unified response format for all platforms"""
    text: str
    attachments: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    buttons: List[Dict[str, str]] = None
    thread_id: Optional[str] = None


class PlatformAdapter(ABC):
    """Base adapter for any platform"""
    
    def __init__(self, platform_name: str, config: Dict[str, Any]):
        self.platform_name = platform_name
        self.config = config
        self.message_handlers: List[Callable] = []
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to platform"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from platform"""
        pass
    
    @abstractmethod
    async def send_message(self, user_id: str, response: PlatformResponse) -> bool:
        """Send message to user"""
        pass
    
    @abstractmethod
    async def receive_messages(self) -> List[PlatformMessage]:
        """Receive messages from platform (long-polling or streaming)"""
        pass
    
    def register_handler(self, handler: Callable):
        """Register message handler"""
        self.message_handlers.append(handler)
    
    async def broadcast_message(self, message: PlatformMessage):
        """Broadcast message to all handlers"""
        for handler in self.message_handlers:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Handler error: {e}")
    
    async def run(self):
        """Main event loop"""
        if not await self.connect():
            logger.error(f"Failed to connect to {self.platform_name}")
            return
        
        try:
            while True:
                messages = await self.receive_messages()
                for msg in messages:
                    await self.broadcast_message(msg)
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error in {self.platform_name} adapter: {e}")
        finally:
            await self.disconnect()


class TelegramAdapter(PlatformAdapter):
    """Telegram platform adapter (existing bot)"""
    
    async def connect(self) -> bool:
        logger.info("Telegram adapter connected (via webhook)")
        return True
    
    async def disconnect(self) -> bool:
        logger.info("Telegram adapter disconnected")
        return True
    
    async def send_message(self, user_id: str, response: PlatformResponse) -> bool:
        # Delegated to existing telegram_bot.py handlers
        logger.info(f"Telegram: Sending to {user_id}")
        return True
    
    async def receive_messages(self) -> List[PlatformMessage]:
        # Handled by FastAPI webhook
        return []


class SlackAdapter(PlatformAdapter):
    """Slack platform adapter"""
    
    async def connect(self) -> bool:
        try:
            from slack_bolt.async_app import AsyncApp
            self.slack_app = AsyncApp(token=self.config.get('token'))
            logger.info("Slack adapter connected")
            return True
        except ImportError:
            logger.warning("slack-bolt not installed")
            return False
    
    async def disconnect(self) -> bool:
        logger.info("Slack adapter disconnected")
        return True
    
    async def send_message(self, user_id: str, response: PlatformResponse) -> bool:
        try:
            await self.slack_app.client.chat_postMessage(
                channel=user_id,
                text=response.text,
                blocks=self._format_blocks(response)
            )
            return True
        except Exception as e:
            logger.error(f"Slack send failed: {e}")
            return False
    
    async def receive_messages(self) -> List[PlatformMessage]:
        # Would be handled by Slack event subscriptions
        return []
    
    def _format_blocks(self, response: PlatformResponse) -> List[Dict]:
        """Format response as Slack blocks"""
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": response.text}}]
        if response.buttons:
            blocks.append({
                "type": "actions",
                "elements": [
                    {"type": "button", "text": {"type": "plain_text", "text": btn['text']},
                     "value": btn['value']}
                    for btn in response.buttons
                ]
            })
        return blocks


class DiscordAdapter(PlatformAdapter):
    """Discord platform adapter"""
    
    async def connect(self) -> bool:
        try:
            import discord
            self.bot = discord.Client()
            # Would initialize with token
            logger.info("Discord adapter connected")
            return True
        except ImportError:
            logger.warning("discord.py not installed")
            return False
    
    async def disconnect(self) -> bool:
        logger.info("Discord adapter disconnected")
        return True
    
    async def send_message(self, user_id: str, response: PlatformResponse) -> bool:
        try:
            # Implementation for Discord
            logger.info(f"Discord: Sending to {user_id}")
            return True
        except Exception as e:
            logger.error(f"Discord send failed: {e}")
            return False
    
    async def receive_messages(self) -> List[PlatformMessage]:
        return []


class PlatformBridge:
    """Unified bridge for all platforms"""
    
    def __init__(self):
        self.adapters: Dict[str, PlatformAdapter] = {}
        self.message_router: Optional[Callable] = None
    
    def register_adapter(self, adapter: PlatformAdapter):
        """Register a platform adapter"""
        self.adapters[adapter.platform_name] = adapter
        logger.info(f"Registered adapter: {adapter.platform_name}")
    
    def register_router(self, router: Callable):
        """Register message router"""
        self.message_router = router
    
    async def broadcast_to_all(self, response: PlatformResponse, exclude: str = None):
        """Send message to all platforms"""
        for platform_name, adapter in self.adapters.items():
            if exclude and platform_name == exclude:
                continue
            try:
                await adapter.send_message("broadcast", response)
            except Exception as e:
                logger.error(f"Broadcast to {platform_name} failed: {e}")
    
    async def route_message(self, message: PlatformMessage) -> PlatformResponse:
        """Route message to handler and get response"""
        if self.message_router:
            return await self.message_router(message)
        return PlatformResponse(text="No handler registered")
    
    async def run_all(self):
        """Run all adapters concurrently"""
        tasks = [adapter.run() for adapter in self.adapters.values()]
        await asyncio.gather(*tasks)


# Global bridge instance
platform_bridge = PlatformBridge()
