"""
Integration and Unit tests for Microservices Decoupling Architecture:
- Contract polymorphism & Dependency Injection overrides
- Decoupled Domain Event Dispatcher
- Circuit Breaker fault isolation & resilience
- Microservices Health & Readiness Diagnostics
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.container import (
    get_code_execution_service,
    get_event_dispatcher
)
from app.contracts.execution import CodeExecutionContract
from app.core.events import (
    EventDispatcher,
    ExecutionCompletedEvent,
    SessionCreatedEvent,
    TurnEvaluatedEvent
)
from app.core.resilience import CircuitBreaker, CircuitBreakerOpenException

client = TestClient(app)


def test_microservices_health_endpoints():
    """Verify microservices liveness, readiness, and services diagnostic status."""
    # Liveness check
    live_resp = client.get("/api/v1/health/liveness")
    assert live_resp.status_code == 200
    assert live_resp.json()["status"] == "alive"

    # Readiness check
    ready_resp = client.get("/api/v1/health/readiness")
    assert ready_resp.status_code == 200
    assert ready_resp.json()["status"] == "ready"

    # Detailed subsystem health check
    services_resp = client.get("/api/v1/health/services")
    assert services_resp.status_code == 200
    data = services_resp.json()
    assert data["status"] == "healthy"
    assert "subsystems" in data
    subsystems = data["subsystems"]
    
    # Verify all decoupled subsystems report status
    expected_subsystems = [
        "database_primary",
        "sandbox_python",
        "sandbox_sql",
        "sandbox_redis",
        "sandbox_nosql",
        "ai_evaluator",
        "question_catalog",
        "knowledge_mindmaps"
    ]
    for sub in expected_subsystems:
        assert sub in subsystems
        assert subsystems[sub]["status"] in ["HEALTHY", "DEGRADED"]


def test_dependency_injection_override_decoupling():
    """
    Demonstrate that domain services can be swapped/mocked at runtime via
    FastAPI dependency injection without altering router implementations.
    """
    class MockCodeExecutionService(CodeExecutionContract):
        def execute(self, code: str, timeout_seconds: int = 5) -> dict:
            return {
                "stdout": "Mocked Microservice Engine Output",
                "stderr": "",
                "return_value": "42",
                "execution_time_ms": 1.23,
                "success": True,
                "test_results": [],
                "complexity_analysis": {"time_complexity": "O(1)", "space_complexity": "O(1)"}
            }

        def analyze_complexity(self, code: str) -> dict:
            return {
                "time_complexity": "O(1)",
                "space_complexity": "O(1)",
                "bottlenecks": [],
                "optimization_suggestions": []
            }

    # Override the dependency in FastAPI
    app.dependency_overrides[get_code_execution_service] = lambda: MockCodeExecutionService()

    try:
        resp = client.post("/api/v1/sandbox/python", json={"code": "print('hello world')"})
        assert resp.status_code == 200
        result = resp.json()
        assert result["stdout"] == "Mocked Microservice Engine Output"
        assert result["execution_time_ms"] == 1.23
        assert result["complexity_analysis"]["time_complexity"] == "O(1)"
    finally:
        # Clean up dependency overrides
        app.dependency_overrides.pop(get_code_execution_service, None)


def test_domain_event_dispatcher():
    """Verify asynchronous/decoupled publish-subscribe domain event bus."""
    dispatcher = EventDispatcher()
    received_events = []

    def handle_execution(event: ExecutionCompletedEvent):
        received_events.append(event)

    def handle_session(event: SessionCreatedEvent):
        received_events.append(event)

    # Subscribe handlers using class or string
    dispatcher.subscribe(ExecutionCompletedEvent, handle_execution)
    dispatcher.subscribe(SessionCreatedEvent, handle_session)

    # Publish events
    exec_event = ExecutionCompletedEvent(
        execution_type="python",
        success=True,
        execution_time_ms=12.5,
        code_length=42
    )
    sess_event = SessionCreatedEvent(
        session_id=999,
        experience_level="lead",
        target_company="Google"
    )

    dispatcher.publish(exec_event)
    dispatcher.publish(sess_event)

    assert len(received_events) == 2
    assert received_events[0].execution_type == "python"
    assert received_events[1].target_company == "Google"


def test_circuit_breaker_resilience():
    """Verify circuit breaker trips on consecutive failures and activates fallback."""
    breaker = CircuitBreaker("test_llm_service", failure_threshold=2, recovery_timeout_seconds=60.0)
    assert breaker.state == "CLOSED"

    def faulty_service():
        raise RuntimeError("External Provider Timeout 504")

    # First failure
    with pytest.raises(RuntimeError):
        breaker.call(faulty_service)
    assert breaker.state == "CLOSED"

    # Second failure -> trips breaker
    with pytest.raises(RuntimeError):
        breaker.call(faulty_service)
    assert breaker.state == "OPEN"

    # Subsequent call fails immediately with CircuitBreakerOpenException without invoking service
    with pytest.raises(CircuitBreakerOpenException):
        breaker.call(faulty_service)

    # Call with fallback returns graceful fallback response
    fallback_result = breaker.call_with_fallback(
        faulty_service,
        fallback_func=lambda: {"fallback": True, "message": "Circuit breaker active"}
    )
    assert fallback_result == {"fallback": True, "message": "Circuit breaker active"}
