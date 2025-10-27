"""Workflow orchestrator with optional LangGraph integration.

This module will try multiple import paths for LangGraph and, if available,
build a graph-based workflow. If LangGraph isn't installed or the API doesn't
match, it falls back to a simple sequential orchestrator that uses the
project's agent classes directly. Either way `Workflow.run()` returns a
dictionary with at least the key `pain_points` (so tests and callers stay
stable).
"""
from typing import Any, Dict

from src.agents.search_agent import Query_Generation_Agent
from src.agents.scraper_agent import Search_and_Retrieval_Agent
from src.agents.analyzer_agent import Validation_Agent
from src.agents.aggregator_agent import Synthesis_Agent


def _import_langgraph():
    """Try several possible langgraph import paths and return (GraphClass, NodeClass)
    or (None, None) if unavailable.
    """
    candidates = [
        ("langgraph", "Graph", "Node"),
        ("langgraph.core", "Graph", "Node"),
        ("langgraph.graph", "Graph", "Node"),
        ("langchain_core.runnables.graph", "Graph", "Node"),
    ]
    for module_name, graph_name, node_name in candidates:
        try:
            module = __import__(module_name, fromlist=[graph_name, node_name])
            Graph = getattr(module, graph_name)
            Node = getattr(module, node_name)
            return Graph, Node
        except Exception:
            continue
    return None, None


class Workflow:
    def __init__(self, subject: str = "customer service", target_audience: str = "users"):
        self.subject = subject
        self.target_audience = target_audience
        # Prepare local agents
        self.query_agent = Query_Generation_Agent()
        self.search_agent = Search_and_Retrieval_Agent()
        self.validation_agent = Validation_Agent()
        self.synthesis_agent = Synthesis_Agent()

        # Try to wire a LangGraph graph if available
        Graph, Node = _import_langgraph()
        if Graph and Node:
            try:
                self._use_langgraph(Graph, Node)
                self._use_graph = True
            except Exception:
                # If graph wiring fails for any reason, fall back to local mode
                self._use_graph = False
        else:
            self._use_graph = False

    def _use_langgraph(self, GraphClass: Any, NodeClass: Any):
        """Construct a simple LangGraph graph using the available classes.

        The exact API varies between versions, so we attempt a conservative
        wiring: create nodes that wrap the agent callables and add simple
        edges. This is intentionally minimal because full LangGraph integration
        should be implemented and tested with the target library version.
        """
        # Build a minimal graph instance
        self.graph = GraphClass()

        # Helper to wrap an agent into a callable node. Different LangGraph
        # releases may accept different node constructor params; try common ones.
        def _make_node(name, agent_callable):
            try:
                # Some versions allow Node(name, fn)
                return NodeClass(name, agent_callable)
            except Exception:
                try:
                    # Some versions accept Node(name=name, runnable=fn)
                    return NodeClass(name=name, runnable=agent_callable)
                except Exception:
                    # Last resort: just instantiate NodeClass(name)
                    n = NodeClass(name)
                    # attach the callable for our simple runner
                    setattr(n, "callable", agent_callable)
                    return n

        # Create nodes for each agent
        qn = _make_node("query_generator", lambda state: self.query_agent.generate_queries(
            state.get("subject"), state.get("target_audience"), state.get("feedback_log", [])
        ))
        sn = _make_node("searcher", lambda state: self.search_agent.execute_queries(
            state.get("generated_queries", []), state.get("source_filters", [])))
        vn = _make_node("validator", lambda state: self.validation_agent.validate_results(
            state.get("raw_results", [])))
        an = _make_node("aggregator", lambda state: self.synthesis_agent.compile_report(
            state.get("validated_pain_points", [])))

        # Add nodes to graph — API differences exist; try multiple ways
        try:
            # common API: graph.add_node(node)
            self.graph.add_node(qn)
            self.graph.add_node(sn)
            self.graph.add_node(vn)
            self.graph.add_node(an)
        except Exception:
            # Fallback: append to a nodes attribute if present
            if not hasattr(self.graph, "nodes"):
                self.graph.nodes = []
            self.graph.nodes.extend([qn, sn, vn, an])

        # Store node refs for possible custom execution
        self._nodes = [qn, sn, vn, an]

    def run(self) -> Dict[str, Any]:
        # Ensure state is populated with subject/targets
        state = {
            "subject": self.subject,
            "target_audience": self.target_audience,
            "feedback_log": [],
            "source_filters": ["social media", "forums"],
        }

        if getattr(self, "_use_graph", False):
            # Try to execute nodes using LangGraph if available. Because Node
            # APIs differ, we support either a `callable` attribute or a
            # `.run()` / `.call()` method on the node.
            for node in getattr(self, "_nodes", []):
                # Execute node using attached callable if present
                if hasattr(node, "callable") and callable(getattr(node, "callable")):
                    out = node.callable(state)
                else:
                    # Try common runtimes
                    executed = False
                    for name in ("run", "call", "execute"):
                        if hasattr(node, name):
                            fn = getattr(node, name)
                            try:
                                out = fn(state)
                                executed = True
                                break
                            except Exception:
                                continue
                    if not executed:
                        # As last resort, try calling the node itself
                        try:
                            out = node(state)
                        except Exception:
                            out = None

                # integrate outputs into state using best-effort keys
                if out is not None:
                    # heuristics based on which node produced output
                    if isinstance(out, list):
                        # assume search outputs list -> raw_results
                        if "raw_results" not in state or len(state.get("raw_results", [])) == 0:
                            state["raw_results"] = out
                        else:
                            state["raw_results"].extend(out)
                    elif isinstance(out, dict):
                        state.update(out)
                    else:
                        # ignore scalar outputs for now
                        pass

            # After graph execution, validate and synthesize if not already done
            validated = state.get("validated_pain_points") or self.validation_agent.validate_results(state.get("raw_results", []))
            report = state.get("report") or self.synthesis_agent.compile_report(validated)
            return {"pain_points": validated, "report": report}

        # Local sequential fallback (keeps tests and simple usage working)
        generated_queries = self.query_agent.generate_queries(self.subject, self.target_audience, [])
        raw_results = self.search_agent.execute_queries(generated_queries, ["social media", "forums"])
        validated = self.validation_agent.validate_results(raw_results)
        report = self.synthesis_agent.compile_report(validated)
        return {"pain_points": validated, "report": report}