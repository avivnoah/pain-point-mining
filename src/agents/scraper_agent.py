from typing import List, Dict, Any


class Search_and_Retrieval_Agent:
    """A tool-using agent that executes queries against available search tools.

    It prefers Tavily (if available via src.agents.search_agent.TavilySearchAgent).
    If external tools are not configured, it returns deterministic mock results
    so the system remains testable offline.
    """
    def __init__(self, tools: Dict[str, Any] = None):
        # Lazy import to avoid hard dependency when not used
        try:
            from src.agents.search_agent import TavilySearchAgent
        except Exception:
            TavilySearchAgent = None

        self.tools = tools or {}
        # If no tavily provided in tools, instantiate one if possible
        if 'tavily' not in self.tools and TavilySearchAgent is not None:
            try:
                self.tools['tavily'] = TavilySearchAgent()
            except Exception:
                self.tools['tavily'] = None

    def execute_queries(self, generated_queries: List[str], source_filters: List[str]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for q in generated_queries:
            # Decide which tool(s) to use based on source_filters
            if 'tavily' in self.tools and self.tools['tavily']:
                snippets = self.tools['tavily'].search(q)
                results.extend(self._normalize_snippets(snippets, q, source='tavily'))
            else:
                # Fallback to built-in mock results
                results.extend(self._mock_results(q))

            # Placeholder: if reddit requested, call reddit tool (not implemented)
            if any('reddit' in s.lower() for s in source_filters):
                results.extend(self._mock_reddit(q))

            # Placeholder: if twitter/x requested, call twitter tool (not implemented)
            if any(s.lower() in ('twitter', 'x') for s in source_filters):
                results.extend(self._mock_twitter(q))

        return results

    def _normalize_snippets(self, snippets: List[str], query: str, source: str) -> List[Dict[str, Any]]:
        from datetime import datetime

        normalized = []
        for i, text in enumerate(snippets):
            normalized.append({
                'text': text,
                'url': f'https://{source}.example/{query.replace(" ", "-")}/{i}',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'source': source
            })
        return normalized

    def _mock_results(self, query: str) -> List[Dict[str, Any]]:
        # Deterministic mock results for offline testing
        return self._normalize_snippets([
            f"I hate waiting on hold when dealing with {query}",
            f"The chatbot is useless for {query}",
            f"{query} made my workflow easier"
        ], query, source='mock')

    def _mock_reddit(self, query: str) -> List[Dict[str, Any]]:
        return self._normalize_snippets([
            f"Reddit post: Ugh, {query} is the worst",
        ], query, source='reddit')

    def _mock_twitter(self, query: str) -> List[Dict[str, Any]]:
        return self._normalize_snippets([
            f"Twitter: can't believe {query} broke again",
        ], query, source='twitter')