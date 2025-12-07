from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
import json


class LifeCoreApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.auth_header = {"HTTP_AUTHORIZATION": "Bearer dev-secret-key"}
        self.user = User.objects.create_user(username="lcuser", password="pass1234")

    def test_create_and_list_observations(self):
        payload = {
            "user": self.user.id,
            "code": "glucose",
            "value": 110.5,
            "unit": "mg/dL",
            "taken_at": timezone.now().isoformat(),
            "source": "test",
        }
        resp = self.client.post("/api/lifecore/observations", data=json.dumps(payload), content_type="application/json", **self.auth_header)
        self.assertEqual(resp.status_code, 201)

        list_resp = self.client.get(f"/api/lifecore/observations/list?user_id={self.user.id}&code=glucose", **self.auth_header)
        self.assertEqual(list_resp.status_code, 200)
        data = list_resp.json()
        self.assertIn("observations", data)
        self.assertEqual(len(data["observations"]), 1)

    def test_documents_create_and_list(self):
        doc_payload = {
            "user": self.user.id,
            "title": "Informe anual",
            "content": "Resumen anual de salud con mención de presión y glucosa.",
        }
        create_doc = self.client.post("/api/lifecore/documents", data=json.dumps(doc_payload), content_type="application/json", **self.auth_header)
        self.assertEqual(create_doc.status_code, 201)

        list_resp = self.client.get(f"/api/lifecore/documents/list?user_id={self.user.id}", **self.auth_header)
        self.assertEqual(list_resp.status_code, 200)
        listed = list_resp.json()
        self.assertIn("documents", listed)
        self.assertGreaterEqual(len(listed["documents"]), 1)
