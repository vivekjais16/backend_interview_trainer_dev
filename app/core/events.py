import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Callable, Any, Coroutine, Union, Type

logger = logging.getLogger("interview_trainer.events")

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

class DomainEvent:
    """Base class for all decoupled domain events."""
    EVENT_NAME: str = "domain.event"

    def __init__(self, name: str, payload: Dict[str, Any]):
        self.name = name
        self.payload = payload
        self.timestamp = utc_now_iso()

    def __repr__(self):
        return f"<DomainEvent {self.name} at {self.timestamp}>"

class ExecutionCompletedEvent(DomainEvent):
    EVENT_NAME = "execution.completed"

    def __init__(self, execution_type: str, success: bool, execution_time_ms: float, code_length: int):
        super().__init__(self.EVENT_NAME, {
            "execution_type": execution_type,
            "success": success,
            "execution_time_ms": execution_time_ms,
            "code_length": code_length
        })
        self.execution_type = execution_type
        self.success = success
        self.execution_time_ms = execution_time_ms
        self.code_length = code_length

class TurnEvaluatedEvent(DomainEvent):
    EVENT_NAME = "turn.evaluated"

    def __init__(self, session_id: int, question_id: int, score: float, verdict: str):
        super().__init__(self.EVENT_NAME, {
            "session_id": session_id,
            "question_id": question_id,
            "score": score,
            "verdict": verdict
        })
        self.session_id = session_id
        self.question_id = question_id
        self.score = score
        self.verdict = verdict

class SessionCreatedEvent(DomainEvent):
    EVENT_NAME = "session.created"

    def __init__(self, session_id: int, experience_level: str, target_company: str):
        super().__init__(self.EVENT_NAME, {
            "session_id": session_id,
            "experience_level": experience_level,
            "target_company": target_company
        })
        self.session_id = session_id
        self.experience_level = experience_level
        self.target_company = target_company

class EventDispatcher:
    """
    Decoupled Event Dispatcher for Microservice Domain Events.
    Allows components to publish events without knowing who is listening.
    """
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type_or_name: Union[str, Type[DomainEvent]], handler: Callable):
        """Registers a listener callback for a given event name or DomainEvent class."""
        if isinstance(event_type_or_name, type) and issubclass(event_type_or_name, DomainEvent):
            event_name = getattr(event_type_or_name, "EVENT_NAME", event_type_or_name.__name__)
        else:
            event_name = str(event_type_or_name)

        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(handler)
        logger.debug(f"Subscribed handler {getattr(handler, '__name__', str(handler))} to event '{event_name}'")

    def publish(self, event: DomainEvent):
        """Publishes an event to all registered listeners without blocking."""
        handlers = self._listeners.get(event.name, [])
        for h in handlers:
            try:
                if asyncio.iscoroutinefunction(h):
                    asyncio.create_task(h(event))
                else:
                    h(event)
            except Exception as e:
                logger.error(f"Error executing listener {h} for event {event.name}: {e}")

# Global singleton event dispatcher
event_dispatcher = EventDispatcher()
