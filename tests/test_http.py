import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch

import server


class LocalApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        requirements = json.loads((server.ROOT / "requirements.json").read_text())
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.make_handler({"key": "", "model": server.DEFAULT_MODEL}, requirements))
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=2)

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.httpd.server_port, timeout=3)
        try:
            connection.request(method, path, body=body, headers=headers or {})
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    def test_status_reports_configuration_without_secret(self):
        status, body = self.request("GET", "/api/status")
        self.assertEqual(status, 200)
        result = json.loads(body)
        self.assertFalse(result["configured"])
        self.assertFalse(result["connection_verified"])
        self.assertNotIn("key", result)

    def test_missing_key_is_actionable(self):
        status, body = self.request("POST", "/api/chat", json.dumps({"question": "Refund?"}), {"Content-Type": "application/json"})
        self.assertEqual(status, 503)
        self.assertIn("--setup-key", json.loads(body)["error"])

    def test_cross_origin_request_is_rejected(self):
        status, _ = self.request("POST", "/api/chat", "{}", {"Content-Type": "application/json", "Origin": "https://unrelated.example"})
        self.assertEqual(status, 403)

    def test_invalid_input_does_not_reach_provider(self):
        for payload in ({"question": ""}, {"question": ["not a string"]}, ["not an object"]):
            with self.subTest(payload=payload), patch("server.generate_answer") as mocked:
                status, _ = self.request("POST", "/api/chat", json.dumps(payload), {"Content-Type": "application/json"})
                self.assertEqual(status, 400)
                mocked.assert_not_called()

    def test_static_root_cannot_expose_environment(self):
        status, _ = self.request("GET", "/../.env")
        self.assertEqual(status, 404)

    def test_serves_interface(self):
        status, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"answer-mode", body)


if __name__ == "__main__":
    unittest.main()
