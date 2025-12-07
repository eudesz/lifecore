from typing import Any, Dict, List
from datetime import datetime


class TimelineService:
    def __init__(self):
        self._events: List[Dict[str, Any]] = []

    def record(self, user_id: str, kind: str, payload: Dict[str, Any]):
        self._events.append({
            'user_id': user_id,
            'kind': kind,
            'payload': payload,
            'occurred_at': datetime.utcnow().isoformat(),
        })

    def list_events(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        return [e for e in self._events if e['user_id'] == user_id][-limit:]
