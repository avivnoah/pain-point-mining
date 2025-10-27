from datetime import datetime
from typing import List, Dict, Any, Optional


class Synthesis_Agent:
    """Compiles the final report from validated pain points.

    The agent accepts a list of validated pain point dicts with at least
    'quote', 'source', and 'timestamp' keys (timestamp may be a datetime).
    It returns a formatted Markdown string by default.
    """

    def __init__(self, output_format: str = "markdown"):
        self.output_format = output_format

    def compile_report(self, validated_pain_points: List[Dict[str, Any]]) -> str:
        """Return a report as a string. Supported formats: 'markdown', 'json'."""
        if self.output_format == "json":
            import json

            # Ensure timestamps are serializable
            cleaned = []
            for p in validated_pain_points:
                cp = dict(p)
                ts = cp.get('timestamp')
                if isinstance(ts, datetime):
                    cp['timestamp'] = ts.isoformat()
                cleaned.append(cp)
            return json.dumps({'pain_points': cleaned}, indent=2)

        # Default: markdown
        lines = ["# Pain Points Report", ""]
        if not validated_pain_points:
            lines.append("No validated pain points found.")
            return "\n".join(lines)

        for i, p in enumerate(validated_pain_points, start=1):
            quote = p.get('quote')
            source = p.get('source', 'unknown')
            ts = p.get('timestamp')
            if isinstance(ts, datetime):
                ts = ts.date().isoformat()
            lines.append(f"{i}. \"{quote}\"")
            lines.append(f"   - Source: {source}")
            if ts:
                lines.append(f"   - Date: {ts}")
            lines.append("")

        return "\n".join(lines)
class Synthesis_Agent:
    """Synthesis agent that compiles validated pain points into a human-readable report.

    Tests provide a simple list of strings (quotes). In production the analyzer may
    return dicts with metadata. This class supports both formats.
    """
    def __init__(self):
        self.report = ""

    def compile_report(self, validated_pain_points):
        # Accept either a list of strings or a list of dicts
        formatted_points = []
        for p in validated_pain_points:
            if isinstance(p, str):
                formatted_points.append({
                    'pain_point': p,
                    'source': 'unknown',
                    'timestamp': None
                })
            elif isinstance(p, dict):
                # Ensure required keys exist with defaults
                formatted_points.append({
                    'pain_point': p.get('pain_point') or p.get('quote') or str(p),
                    'source': p.get('source', 'unknown'),
                    'timestamp': p.get('timestamp')
                })
            else:
                formatted_points.append({
                    'pain_point': str(p),
                    'source': 'unknown',
                    'timestamp': None
                })

        self.report = self._render_report(formatted_points)
        return self.report

    def _render_report(self, formatted_points):
        lines = ["Pain Points Report", "===================", ""]
        for i, item in enumerate(formatted_points, start=1):
            lines.append(f"{i}. \"{item['pain_point']}\"")
            lines.append(f"   Source: {item['source']}")
            if item.get('timestamp'):
                lines.append(f"   Date: {item['timestamp']}")
            lines.append("")
        return "\n".join(lines)