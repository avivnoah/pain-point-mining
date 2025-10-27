class Query_Generation_Agent:
    """Generates diverse search queries for a given subject and target audience.

    Features:
    - Multiple strategies (generic, persona-focused, tool-focused, emotion-focused)
    - Incorporates feedback from a `feedback_log` to refine queries (self-critique)
    - Returns a deduplicated list of queries ordered by heuristic priority
    """

    def __init__(self, max_queries: int = 20):
        self.max_queries = max_queries

    def generate_queries(self, subject: str, target_audience: str = None, feedback_log: list | None = None) -> list:
        feedback_log = feedback_log or []
        queries = []

        # Generic queries
        queries.append(f"{subject} complaints")
        if target_audience:
            queries.append(f"{subject} complaints from {target_audience}")
            queries.append(f"{target_audience} frustrations with {subject}")

        # Emotion / sentiment focused
        queries.append(f"frustrations about {subject}")
        queries.append(f"why people hate {subject}")

        # Problem-focused / workflow bottlenecks
        queries.append(f"{subject} performance issues")
        queries.append(f"{subject} bottlenecks")
        queries.append(f"{subject} productivity problems")

        # Tool and integration focused (helpful for technical domains)
        queries.append(f"{subject} integration problems")
        queries.append(f"{subject} data loss")
        queries.append(f"{subject} crash" )

        # Persona-driven prompts
        if target_audience:
            queries.append(f"{target_audience} problems with {subject}")
            queries.append(f"what {target_audience} hate about {subject}")

        # Incorporate feedback log to bias generation
        for fb in feedback_log:
            # If feedback mentions a topic, focus queries on that topic
            fb_clean = str(fb).strip()
            if not fb_clean:
                continue
            queries.append(f"{subject} {fb_clean}")
            queries.append(f"{subject} problems: {fb_clean}")

        # Heuristic diversification: expand with short variants
        extra = []
        for q in list(queries):
            extra.append(q + " issues")
            extra.append(q + " complaints")
            if " " in q:
                # shorten multiword queries to last two tokens
                tokens = q.split()
                extra.append(" ".join(tokens[-2:]))

        queries.extend(extra)

        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for q in queries:
            qn = q.lower().strip()
            if qn not in seen:
                seen.add(qn)
                deduped.append(q)
            if len(deduped) >= self.max_queries:
                break

        return deduped

    def refine_queries(self, generated_queries: list, feedback_log: list | None = None) -> list:
        """Refine an existing list of queries using feedback from validators.

        The feedback_log should contain short messages like:
          - "too generic"
          - "focus on bottlenecks and tool names"
          - "results are outdated"

        The method returns a new, refined list of queries.
        """
        feedback_log = feedback_log or []
        refined = []

        # If feedback asks for focus on bottlenecks or tools, transform queries
        focus_tools = any("tool" in str(fb).lower() or "tool names" in str(fb).lower() for fb in feedback_log)
        focus_bottlenecks = any("bottleneck" in str(fb).lower() or "bottlenecks" in str(fb).lower() for fb in feedback_log)
        too_generic = any("generic" in str(fb).lower() or "too generic" in str(fb).lower() for fb in feedback_log)

        for q in generated_queries:
            base = q
            if focus_tools:
                refined.append(base + " " + "specific tool")
                refined.append(base + " " + "integration with X")
            if focus_bottlenecks:
                refined.append(base + " " + "bottleneck")
                refined.append(base + " " + "slow")
            if too_generic:
                # make queries more specific by adding context tokens
                refined.append(base + " " + "error messages")
                refined.append(base + " " + "stack traces")

            # Always keep original as seed
            refined.append(base)

        # Fallback: if nothing was produced, return original
        if not refined:
            return generated_queries

        # Deduplicate & limit
        seen = set()
        out = []
        for r in refined:
            key = r.lower().strip()
            if key not in seen:
                seen.add(key)
                out.append(r)
            if len(out) >= self.max_queries:
                break

        return out


class TavilySearchAgent:
    """Uses Tavily (a hypothetical web-search API) to execute semantic searches.

    Behavior:
    - If `TAVILY_API_KEY` is present in environment (via utils.config), it will
      call the Tavily REST endpoint and return a list of text snippets.
    - If no API key is configured, it falls back to a deterministic mock
      implementation (useful for tests and offline development).
    """
    def __init__(self, api_key=None, session=None, timeout=10):
        # Lazy import to avoid hard dependency when not used
        import os
        from src.utils.config import get_env

        self.api_key = api_key or get_env('TAVILY_API_KEY')
        self.timeout = timeout
        self.session = session
        if self.session is None:
            try:
                import requests
                self.session = requests.Session()
            except Exception:
                self.session = None

    def search(self, query, max_results=10):
        if not self.api_key or not self.session:
            # Fallback deterministic mock
            return self._mock_search(query, max_results)

        # Call Tavily REST API (fictional endpoint used as example)
        url = 'https://api.tavily.com/v1/search'
        headers = {'Authorization': f'Bearer {self.api_key}'}
        params = {'q': query, 'limit': max_results}

        # Simple retry loop with backoff
        import time
        attempts = 3
        backoff = 1.0
        for attempt in range(1, attempts + 1):
            try:
                resp = self.session.get(url, headers=headers, params=params, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
                # Expect data['results'] is a list of items with 'snippet' or 'text'
                results = []
                for item in data.get('results', []):
                    text = item.get('snippet') or item.get('text') or str(item)
                    results.append(text)
                return results
            except Exception:
                if attempt == attempts:
                    # Final attempt failed: fallback to mock
                    return self._mock_search(query, max_results)
                time.sleep(backoff)
                backoff *= 2

    def _mock_search(self, query, max_results=10):
        # Deterministic placeholder used in tests / offline dev
        samples = [
            f"I hate waiting on hold when dealing with {query}",
            f"The chatbot is useless for {query}",
            f"{query} made my workflow easier"
        ]
        return samples[:max_results]