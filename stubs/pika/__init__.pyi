from typing import Any, Callable, Dict, Optional, Union

class ConnectionParameters:
    """Stub for Pika ConnectionParameters."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        virtual_host: str = "/",
        credentials: Optional[Any] = None,
        channel_max: int = 0,
        heartbeat: Optional[int] = None,
    ) -> None:
        ...

class BlockingConnection:
    """Stub for Pika BlockingConnection."""
    
    def __init__(self, parameters: ConnectionParameters) -> None:
        ...
    
    def channel(self) -> "BlockingChannel":
        ...
    
    def close(self) -> None:
        ...

class BlockingChannel:
    """Stub for Pika BlockingChannel."""
    
    def queue_declare(
        self, 
        queue: str, 
        passive: bool = False,
        durable: bool = False,
        exclusive: bool = False,
        auto_delete: bool = False,
        arguments: Optional[Dict[str, Any]] = None
    ) -> Any:
        ...
    
    def basic_publish(
        self,
        exchange: str,
        routing_key: str,
        body: Union[str, bytes],
        properties: Optional[Any] = None,
        mandatory: bool = False
    ) -> None:
        ...
    
    def basic_consume(
        self,
        queue: str,
        on_message_callback: Callable[[Any, Any, Any, Any], None],
        auto_ack: bool = False,
        exclusive: bool = False,
        consumer_tag: Optional[str] = None,
        arguments: Optional[Dict[str, Any]] = None
    ) -> str:
        ...
