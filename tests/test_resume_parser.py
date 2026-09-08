import unittest
from services.resume_parser import extract_resume_entities

class TestResumeParser(unittest.TestCase):
    """Test text parsing and entity extraction heuristics."""

    def test_entity_extraction(self):
        sample_text = """
        PRIYA PATEL
        Senior Frontend Engineer
        Email: priya.patel@testcorp.com | Phone: +1 (555) 345-6789
        San Jose, CA

        SUMMARY:
        Frontend engineer with 4 years of experience delivering interactive web apps using React, TypeScript, and Bootstrap.

        SKILLS:
        React, JavaScript, TypeScript, HTML5, CSS3, Bootstrap, Git

        EXPERIENCE:
        Frontend Developer at CloudScale (2020 - Present)
        Developed dashboards with React and Bootstrap.

        EDUCATION:
        Bachelor of Science in Software Engineering, San Jose State University
        """

        data = extract_resume_entities(sample_text)

        self.assertEqual(data['email'], "priya.patel@testcorp.com")
        self.assertIn("555", data['phone'])
        self.assertGreaterEqual(data['years_experience'], 3.0)

        skill_names = [s['skill_name'] for s in data['skills']]
        self.assertIn("React", skill_names)
        self.assertIn("JavaScript", skill_names)
        self.assertIn("TypeScript", skill_names)

        self.assertTrue(len(data['education']) > 0)
        self.assertIn("Bachelor", data['education'][0]['degree'])
        self.assertTrue(len(data['summary']) > 20)

if __name__ == '__main__':
    unittest.main()

