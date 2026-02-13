"""Unit tests for the orchestrator state machine."""

import pytest
from uuid import uuid4

from maios.core.orchestrator.state import OrchestratorPhase, OrchestratorState


def test_state_creation():
    """Test creating a new orchestrator state."""
    state = OrchestratorState(project_id=uuid4())
    assert state.phase == OrchestratorPhase.PLAN
    assert state.pending_tasks == 0


def test_phase_enum():
    """Test that phase enum values are correct."""
    assert OrchestratorPhase.PLAN.value == "PLAN"
    assert OrchestratorPhase.DELEGATE.value == "DELEGATE"
    assert OrchestratorPhase.MONITOR.value == "MONITOR"
    assert OrchestratorPhase.ESCALATE.value == "ESCALATE"
    assert OrchestratorPhase.REASSIGN.value == "REASSIGN"
    assert OrchestratorPhase.COMPLETE.value == "COMPLETE"


def test_state_with_tasks():
    """Test state with task IDs."""
    task_id_1 = uuid4()
    task_id_2 = uuid4()
    agent_id = uuid4()

    state = OrchestratorState(
        project_id=uuid4(),
        current_task_ids=[task_id_1, task_id_2],
        pending_tasks=2,
        active_agents=[agent_id],
    )

    assert len(state.current_task_ids) == 2
    assert state.pending_tasks == 2
    assert len(state.active_agents) == 1


def test_state_with_escalation():
    """Test state with escalation data."""
    state = OrchestratorState(
        project_id=uuid4(),
        escalation_reason="Test escalation",
        error_message="Something went wrong",
    )

    assert state.escalation_reason == "Test escalation"
    assert state.error_message == "Something went wrong"


def test_state_serialization():
    """Test that state can be serialized with enum values."""
    state = OrchestratorState(project_id=uuid4())
    data = state.model_dump()

    assert data["phase"] == "PLAN"  # use_enum_values makes it a string


@pytest.mark.asyncio
async def test_plan_node():
    """Test the plan node."""
    from maios.core.orchestrator.nodes import plan_node

    state = OrchestratorState(project_id=uuid4())
    result = await plan_node(state)
    assert result.phase == OrchestratorPhase.PLAN


@pytest.mark.asyncio
async def test_delegate_node():
    """Test the delegate node."""
    from maios.core.orchestrator.nodes import delegate_node

    state = OrchestratorState(project_id=uuid4())
    result = await delegate_node(state)
    assert result.phase == OrchestratorPhase.DELEGATE


@pytest.mark.asyncio
async def test_monitor_node():
    """Test the monitor node."""
    from maios.core.orchestrator.nodes import monitor_node

    state = OrchestratorState(project_id=uuid4())
    result = await monitor_node(state)
    assert result.phase == OrchestratorPhase.MONITOR


@pytest.mark.asyncio
async def test_escalate_node():
    """Test the escalate node."""
    from maios.core.orchestrator.nodes import escalate_node

    state = OrchestratorState(project_id=uuid4())
    result = await escalate_node(state)
    assert result.phase == OrchestratorPhase.ESCALATE


@pytest.mark.asyncio
async def test_reassign_node():
    """Test the reassign node."""
    from maios.core.orchestrator.nodes import reassign_node

    state = OrchestratorState(project_id=uuid4())
    result = await reassign_node(state)
    assert result.phase == OrchestratorPhase.REASSIGN


@pytest.mark.asyncio
async def test_complete_node():
    """Test the complete node."""
    from maios.core.orchestrator.nodes import complete_node

    state = OrchestratorState(project_id=uuid4())
    result = await complete_node(state)
    assert result.phase == OrchestratorPhase.COMPLETE


def test_route_from_monitor_escalate():
    """Test routing from monitor to escalate."""
    from maios.core.orchestrator.graph import route_from_monitor

    state = OrchestratorState(
        project_id=uuid4(),
        error_message="Error",
        escalation_reason="Need attention",
    )
    assert route_from_monitor(state) == "escalate"


def test_route_from_monitor_reassign():
    """Test routing from monitor to reassign."""
    from maios.core.orchestrator.graph import route_from_monitor

    state = OrchestratorState(
        project_id=uuid4(),
        failed_task_ids=[uuid4()],
    )
    assert route_from_monitor(state) == "reassign"


def test_route_from_monitor_complete():
    """Test routing from monitor to complete."""
    from maios.core.orchestrator.graph import route_from_monitor

    state = OrchestratorState(
        project_id=uuid4(),
        pending_tasks=0,
    )
    assert route_from_monitor(state) == "complete"


def test_route_from_monitor_delegate():
    """Test routing from monitor to delegate (default)."""
    from maios.core.orchestrator.graph import route_from_monitor

    state = OrchestratorState(
        project_id=uuid4(),
        pending_tasks=5,
    )
    assert route_from_monitor(state) == "delegate"


@pytest.mark.asyncio
async def test_create_orchestrator_graph():
    """Test creating the orchestrator graph."""
    from maios.core.orchestrator.graph import create_orchestrator_graph

    graph = create_orchestrator_graph()
    assert graph is not None


@pytest.mark.asyncio
async def test_graph_invocation():
    """Test invoking the orchestrator graph."""
    from maios.core.orchestrator.graph import create_orchestrator_graph

    graph = create_orchestrator_graph()
    initial_state = OrchestratorState(
        project_id=uuid4(),
        pending_tasks=0,  # Should route to complete
    )

    result = await graph.ainvoke(initial_state.model_dump())
    assert result["phase"] == "COMPLETE"
