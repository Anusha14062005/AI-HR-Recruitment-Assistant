import unittest
from app import create_app

class TestFlaskRoutes(unittest.TestCase):
    """Test Flask web endpoints and authentication redirects."""

    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_login_page_renders(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI HR Recruitment Assistant', response.data)

    def test_register_page_renders(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create HR Account', response.data)

    def test_protected_dashboard_redirects_unauthenticated(self):
        response = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    def test_protected_api_returns_401(self):
        response = self.client.get('/api/me')
        self.assertEqual(response.status_code, 401)

    def test_public_jobs_api(self):
        response = self.client.get('/api/jobs')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])

if __name__ == '__main__':
    unittest.main()

