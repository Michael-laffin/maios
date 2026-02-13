"""Orchestrator graph definition using LangGraph."""

from langgraph.graph import END, StateGraph

from maios.core.orchestrator.nodes import (
    complete_node,
    delegate_node,
    escalate_node,
    monitor_node,
    plan_node,
    reassign_node,
)
from maios.core.orchestrator.state import OrchestratorPhase, OrchestratorState


def route_from_monitor(state: OrchestratorState) -> str:
    """Determine next phase from monitor."""
    if state.error_message and state.escalation_reason:
        return "escalate"
    if state.failed_task_ids and len(state.failed_task_ids) > 0:
        return "reassign"
    if state.pending_tasks == 0:
        return "complete"
    return "delegate"


def create_orchestrator_graph():
    """Create the orchestrator state graph."""
    workflow = StateGraph(OrchestratorState)

    # Add nodes
    workflow.add_node("plan", plan_node)
    workflow.add_node("delegate", delegate_node)
    workflow.add_node("monitor", monitor_node)
    workflow.add_node("escalate", escalate_node)
    workflow.add_node("reassign", reassign_node)
    workflow.add_node("complete", complete_node)

    # Set entry point
    workflow.set_entry_point("plan")

    # Add edges
    workflow.add_edge("plan", "delegate")
    workflow.add_edge("delegate", "monitor")

    # Conditional edges from monitor
    workflow.add_conditional_edges(
        "monitor",
        route_from_monitor,
        {
            "delegate": "delegate",
            "escalate": "escalate",
            "reassign": "reassign",
            "complete": "complete",
        },
    )

    workflow.add_edge("escalate", "monitor")
    workflow.add_edge("reassign", "delegate")
    workflow.add_edge("complete", END)

    return workflow.compile()
