from django.test import TestCase, Client
from django.contrib.auth.models import User
import json
import os


class AgentsV2Tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.auth_header = {"HTTP_AUTHORIZATION": "Bearer dev-secret-key"}
        self.user = User.objects.create_user(username="testuser", password="pass1234")

    def test_status_ok(self):
        resp = self.client.get("/api/agents/v2/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("agents_loaded", data)

    def test_analyze_requires_auth(self):
        # Without auth should be 401/403
        resp = self.client.post("/api/agents/v2/analyze", data=json.dumps({"query": "hola"}), content_type="application/json")
        self.assertIn(resp.status_code, (401, 403))

        # With system API key
        payload = {"query": "glucosa en los últimos 7 días", "user_id": self.user.id, "category": "informational"}
        resp_ok = self.client.post("/api/agents/v2/analyze", data=json.dumps(payload), content_type="application/json", **self.auth_header)
        self.assertEqual(resp_ok.status_code, 200)
        data = resp_ok.json()
        self.assertIn("status", data)
        self.assertIn("final_text", data)

    def test_rag_references_on_analyze(self):
        # Create a minimal document via backend endpoint
        doc_payload = {
            "user": self.user.id,
            "title": "Historia clínica - glucosa",
            "content": "El paciente reporta niveles de glucosa elevados en ayunas.",
        }
        create_doc = self.client.post(
            "/api/lifecore/documents",
            data=json.dumps(doc_payload),
            content_type="application/json",
            **self.auth_header,
        )
        self.assertEqual(create_doc.status_code, 201)

        # Query that should retrieve the document as reference
        analyze_payload = {"query": "glucosa", "user_id": self.user.id}
        resp = self.client.post("/api/agents/v2/analyze", data=json.dumps(analyze_payload), content_type="application/json", **self.auth_header)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        refs = data.get("references") or data.get("documents_details") or []
        self.assertTrue(isinstance(refs, list))
        self.assertGreaterEqual(len(refs), 1)

    def test_rag_disabled_flag(self):
        # Temporarily disable RAG
        prev = os.environ.get('FEATURE_RAG')
        os.environ['FEATURE_RAG'] = 'false'
        try:
            analyze_payload = {"query": "glucosa", "user_id": self.user.id}
            resp = self.client.post("/api/agents/v2/analyze", data=json.dumps(analyze_payload), content_type="application/json", **self.auth_header)
            self.assertEqual(resp.status_code, 200)
            refs = resp.json().get('references') or []
            self.assertEqual(len(refs), 0)
        finally:
            if prev is None:
                del os.environ['FEATURE_RAG']
            else:
                os.environ['FEATURE_RAG'] = prev
