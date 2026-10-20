import time
import logging
from enum import Enum
from typing import Callable, Any, Optional

logger = logging.getLogger("interview_trainer.resilience")

class CircuitState(str, Enum):
    CLOSED = "CLOSED"       # Normal operational state
    OPEN = "OPEN"           # Tripped state (failing fast, no downstream calls)
    HALF_OPEN = "HALF_OPEN" # Testing if downstream service recovered

class CircuitBreakerOpenException(Exception):
    """Raised when an operation is attempted while circuit breaker is OPEN."""
    pass

class CircuitBreaker:
    """
    Microservice Circuit Breaker Pattern.
    Prevents cascading failures when external services (e.g. LLM APIs) fail repeatedly.
    """
    def __init__(self, name: str = "service", failure_threshold: int = 3, recovery_timeout_seconds: float = 30.0, **kwargs):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = kwargs.get("recovery_timeout", recovery_timeout_seconds)
        
        self.state: CircuitState = CircuitState.CLOSED
        self.failure_count: int = 0
        self.last_failure_time: Optional[float] = None
        self.last_state_change: float = time.time()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Executes a function under circuit breaker protection, raising CircuitBreakerOpenException if OPEN."""
        if not self.can_execute():
            raise CircuitBreakerOpenException(f"CircuitBreaker '{self.name}' is OPEN. Fast-failing downstream call.")
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception:
            self.record_failure()
            raise

    def call_with_fallback(self, func: Callable, fallback_func: Callable, *args, **kwargs) -> Any:
        """Executes a function with fallback protection if circuit is open or call fails."""
        if not self.can_execute():
            logger.info(f"CircuitBreaker '{self.name}' is OPEN. Executing fallback.")
            return fallback_func()
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            logger.warning(f"Operation failed in CircuitBreaker '{self.name}': {e}. Executing fallback.")
            return fallback_func()

    def record_success(self):
        """Records a successful operation, resetting the failure counter and closing the circuit."""
        if self.state != CircuitState.CLOSED:
            logger.info(f"CircuitBreaker '{self.name}' recovered: {self.state.value} -> CLOSED")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.last_state_change = time.time()

    def record_failure(self):
        """Records a failure. If threshold is exceeded, trips circuit to OPEN."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
            logger.warning(
                f"CircuitBreaker '{self.name}' TRIPPED to OPEN after {self.failure_count} consecutive failures. "
                f"Cooldown window: {self.recovery_timeout_seconds}s"
            )

    def can_execute(self) -> bool:
        """Determines if a call can proceed or if it should be fast-failed."""
        if self.state == CircuitState.CLOSED:
            return True

        # If OPEN, check if recovery cooldown elapsed
        if self.state == CircuitState.OPEN:
            elapsed = time.time() - self.last_state_change
            if elapsed >= self.recovery_timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = time.time()
                logger.info(f"CircuitBreaker '{self.name}' entered HALF_OPEN (trial execution allowed).")
                return True
            return False

        # In HALF_OPEN state, allow single trial
        return True
