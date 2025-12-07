from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta


class MemoryManager:
    """Capa de memoria: corto, mediano, largo plazo (scaffold)."""

    def __init__(self):
        self._session_buffer: List[Dict[str, Any]] = []
        self._timeline_events: List[Dict[str, Any]] = []
        self._lifetime_profile: Dict[str, Any] = {}

    # Corto plazo
    def add_session_turn(self, user_id: str, role: str, text: str):
        self._session_buffer.append({
            'user_id': user_id,
            'role': role,
            'text': text,
            'ts': datetime.utcnow().isoformat(),
        })

    def get_session_context(self, max_items: int = 10) -> List[Dict[str, Any]]:
        return self._session_buffer[-max_items:]

    # Mediano plazo (timeline)
    def add_timeline_event(self, user_id: str, kind: str, payload: Dict[str, Any]):
        self._timeline_events.append({
            'user_id': user_id,
            'kind': kind,
            'payload': payload,
            'occurred_at': datetime.utcnow().isoformat(),
        })

    def get_timeline(self, user_id: str, days: int = 90) -> List[Dict[str, Any]]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        return [e for e in self._timeline_events if e['user_id'] == user_id and datetime.fromisoformat(e['occurred_at']) >= cutoff]

    # Largo plazo (perfil semántico)
    def update_lifetime_profile(self, user_id: str, patch: Dict[str, Any]):
        profile = self._lifetime_profile.get(user_id, {})
        profile.update(patch)
        self._lifetime_profile[user_id] = profile

    def get_lifetime_profile(self, user_id: str) -> Dict[str, Any]:
        return self._lifetime_profile.get(user_id, {})
