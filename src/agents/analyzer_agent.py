import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any


class Validation_Agent:
    """Validation agent that filters raw_results into validated pain points.

    Input: raw_results — list of strings or dicts with optional 'text', 'url', 'timestamp', 'source'.
    Output: a list of validated pain point dicts. Also sets `feedback_log` on the
    instance with short notes for upstream agents.
    """

    DEFAULT_MAX_AGE_MONTHS = 24

    # simple frustration patterns
    FRUSTRATION_PATTERNS = [
        r"\bi hate\b",
        r"\bso slow\b",
        r"\bso frustrating\b",
        r"\bthis is useless\b",
        r"\bdoesn't work\b",
        r"\bnot working\b",
        r"\bnever works\b",
        r"\bwaste of time\b",
        r"\bbroken\b",
        r"\bcan't .*\b",
    ]

    def __init__(self, max_age_months: int = None):
        self.max_age_months = max_age_months or self.DEFAULT_MAX_AGE_MONTHS
        self.feedback_log: List[str] = []

    def validate_results(self, raw_results: List[Any]) -> List[str]:
        """Validate and cluster raw results.

        Returns a list of dicts: {quote, source, url, timestamp, cluster}
        """
        self.feedback_log = []
        normalized = []

        for item in raw_results:
            entry = self._normalize(item)
            if not entry:
                continue
            if not self._passes_recency(entry):
                # record feedback for upstream query refinement
                self.feedback_log.append(f"Dropped outdated: {entry.get('timestamp')} -> {entry.get('quote')[:60]}")
                continue
            if not self._is_frustration(entry.get('quote', '')):
                # non-frustration: ignore but keep note
                self.feedback_log.append(f"Filtered neutral: {entry.get('quote')[:60]}")
                continue
            normalized.append(entry)

        # attempt clustering
        clusters = self._cluster_quotes([e['quote'] for e in normalized])
        for e, c in zip(normalized, clusters):
            e['cluster'] = c

        # Collate validated pain points (deduplicated by quote)
        seen = set()
        validated = []
        for e in normalized:
            q = e['quote']
            if q in seen:
                continue
            seen.add(q)
            validated.append(e)

        # store detailed records and return simplified list of quote strings for backwards compatibility
        self.validated_details = validated
        return [e['quote'] for e in validated]

    def _normalize(self, item: Any) -> Dict[str, Any]:
        # Accept either raw string or dicts
        if isinstance(item, str):
            return {'quote': item, 'source': 'unknown', 'url': None, 'timestamp': datetime.now(timezone.utc)}
        if isinstance(item, dict):
            quote = item.get('text') or item.get('snippet') or item.get('quote') or item.get('content')
            if not quote:
                return None
            # Parse timestamp if present
            ts = item.get('timestamp') or item.get('date') or item.get('created_at')
            parsed = self._parse_timestamp(ts)
            return {'quote': quote, 'source': item.get('source', 'unknown'), 'url': item.get('url'), 'timestamp': parsed}
        return None

    def _parse_timestamp(self, ts) -> Any:
        # Try to parse timestamps from common formats. Use pandas if available,
        # otherwise try common patterns and fallback to now.
        if not ts:
            return datetime.now(timezone.utc)
        try:
            # try pandas parser if available
            import pandas as pd

            parsed = pd.to_datetime(ts, utc=True, errors='coerce')
            if pd.isna(parsed):
                return datetime.now(timezone.utc)
            dt = parsed.to_pydatetime()
            # Ensure tz-aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            # naive fallback
            for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d", "%d %b %Y"):
                try:
                    dt = datetime.strptime(str(ts), fmt)
                    return dt.replace(tzinfo=timezone.utc)
                except Exception:
                    continue
            return datetime.now(timezone.utc)

    def _passes_recency(self, entry: Dict[str, Any]) -> bool:
        now = datetime.now(timezone.utc)
        ts = entry.get('timestamp') or now
        # Normalize ts to tz-aware UTC
        if getattr(ts, 'tzinfo', None) is None:
            ts = ts.replace(tzinfo=timezone.utc)
        age = now - ts
        max_age = timedelta(days=int(self.max_age_months * 30))
        return age <= max_age

    def _is_frustration(self, text: str) -> bool:
        txt = text.lower()
        for pat in self.FRUSTRATION_PATTERNS:
            if re.search(pat, txt):
                return True
        return False

    def _cluster_quotes(self, quotes: List[str]) -> List[int]:
        """Attempt to cluster quotes into integer cluster ids.

        Prefer sklearn's TF-IDF + KMeans if available. If not, do a simple
        keyword-overlap clustering.
        """
        if not quotes:
            return []
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.cluster import KMeans
            vec = TfidfVectorizer(stop_words='english')
            X = vec.fit_transform(quotes)
            n_clusters = min(5, max(1, len(quotes) // 3))
            km = KMeans(n_clusters=n_clusters, random_state=42)
            labels = km.fit_predict(X)
            return [int(l) for l in labels]
        except Exception:
            # Simple overlap-based clustering: cluster by most frequent keyword
            clusters = []
            buckets = []
            for q in quotes:
                tokens = set(re.findall(r"\w{4,}", q.lower()))
                assigned = False
                for i, b in enumerate(buckets):
                    # if share tokens, same cluster
                    if tokens & b:
                        clusters.append(i)
                        b.update(tokens)
                        assigned = True
                        break
                if not assigned:
                    buckets.append(set(tokens))
                    clusters.append(len(buckets) - 1)
            return clusters
