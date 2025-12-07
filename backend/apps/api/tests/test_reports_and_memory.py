from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
import json


class ReportsAndMemoryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.auth_header = {"HTTP_AUTHORIZATION": "Bearer dev-secret-key"}
        self.user = User.objects.create_user(username="repouser", password="pass1234")
        # Seed one observation to have content for reports
        payload = {
            "user": self.user.id,
            "code": "glucose",
            "value": 100,
            "unit": "mg/dL",
            "taken_at": timezone.now().isoformat(),
        }
        self.client.post("/api/lifecore/observations", data=json.dumps(payload), content_type="application/json", **self.auth_header)

    def test_reports_endpoints(self):
        csv_resp = self.client.get(f"/api/reports/observations.csv?user_id={self.user.id}", **self.auth_header)
        self.assertEqual(csv_resp.status_code, 200)
        self.assertIn("text/csv", csv_resp["Content-Type"])  # content type may include charset

        md_resp = self.client.get(f"/api/reports/summary.md?user_id={self.user.id}", **self.auth_header)
        self.assertEqual(md_resp.status_code, 200)
        self.assertIn("text/markdown", md_resp["Content-Type"])  # content type may include charset

        pdf_resp = self.client.get(f"/api/reports/summary.pdf?user_id={self.user.id}", **self.auth_header)
        self.assertIn(pdf_resp.status_code, (200, 501))
        if pdf_resp.status_code == 200:
            self.assertIn("application/pdf", pdf_resp["Content-Type"])  # content type may include charset

    def test_memory_summarize(self):
        # Create an episode through analyze
        analyze_payload = {"query": "resumen", "user_id": self.user.id, "category": "informational"}
        analyze_resp = self.client.post("/api/agents/v2/analyze", data=json.dumps(analyze_payload), content_type="application/json", **self.auth_header)
        self.assertEqual(analyze_resp.status_code, 200)

        # Summarize
        sum_payload = {"user_id": self.user.id}
        sum_resp = self.client.post("/api/lifecore/memory/summarize", data=json.dumps(sum_payload), content_type="application/json", **self.auth_header)
        self.assertEqual(sum_resp.status_code, 200)
        data = sum_resp.json()
        self.assertIn("summary", data)

    def test_flags_endpoint(self):
        resp = self.client.get("/api/flags")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('flags', data)
        self.assertIn('RAG', data['flags'])
        self.assertIn('PROACTIVITY', data['flags'])
