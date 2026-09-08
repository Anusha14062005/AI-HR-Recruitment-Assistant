import unittest
from services.matching_service import compute_match

class TestCandidateMatching(unittest.TestCase):
    """Test 5-factor weighted candidate matching algorithm."""

    def setUp(self):
        self.job = {
            "title": "Senior Python Backend Engineer",
            "required_skills": ["Python", "Flask", "MySQL", "Docker"],
            "preferred_skills": ["Redis", "AWS"],
            "experience_required_years": 5.0,
            "education_requirements": "Bachelor's in CS"
        }

    def test_strong_match(self):
        candidate = {
            "name": "Rahul Sharma",
            "skills": [
                {"skill_name": "Python"},
                {"skill_name": "Flask"},
                {"skill_name": "MySQL"},
                {"skill_name": "Docker"},
                {"skill_name": "Redis"}
            ],
            "years_experience": 5.5,
            "education": [{"degree": "Bachelor of Science in Computer Science"}],
            "projects": [{"project_title": "Payment API", "technologies_used": "Python, Flask, MySQL"}],
            "extracted_text": "Experienced Senior Python developer using Flask and MySQL."
        }

        result = compute_match(candidate, self.job)
        self.assertGreaterEqual(result['overall_score'], 85.0)
        self.assertEqual(result['recommendation'], "Strong Match")
        self.assertIn("Python", result['matched_skills'])
        self.assertEqual(len(result['missing_skills']), 0)

    def test_skill_gap_identification(self):
        candidate = {
            "name": "David Miller",
            "skills": [
                {"skill_name": "Python"},
                {"skill_name": "Flask"}
            ],
            "years_experience": 2.5,
            "education": [{"degree": "B.S. in Information Systems"}],
            "projects": [],
            "extracted_text": "Junior Python programmer."
        }

        result = compute_match(candidate, self.job)
        self.assertLess(result['overall_score'], 80.0)
        self.assertIn("MySQL", result['missing_skills'])
        self.assertIn("Docker", result['missing_skills'])

if __name__ == '__main__':
    unittest.main()

