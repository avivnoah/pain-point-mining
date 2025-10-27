import unittest
from src.graph.workflow import Workflow

class TestWorkflow(unittest.TestCase):

    def setUp(self):
        self.workflow = Workflow()

    def test_initialization(self):
        self.assertIsNotNone(self.workflow)

    def test_agent_integration(self):
        result = self.workflow.run()
        self.assertIsInstance(result, dict)
        self.assertIn('pain_points', result)
        self.assertIsInstance(result['pain_points'], list)

    def test_workflow_output(self):
        result = self.workflow.run()
        self.assertGreater(len(result['pain_points']), 0)

if __name__ == '__main__':
    unittest.main()