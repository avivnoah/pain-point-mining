import unittest
from src.agents.search_agent import Query_Generation_Agent
from src.agents.scraper_agent import Search_and_Retrieval_Agent
from src.agents.analyzer_agent import Validation_Agent
from src.agents.aggregator_agent import Synthesis_Agent

class TestQueryGenerationAgent(unittest.TestCase):
    def setUp(self):
        self.agent = Query_Generation_Agent()

    def test_generate_queries(self):
        subject = "customer service"
        target_audience = "users"
        feedback_log = ["I hate waiting on hold", "The chatbot is useless"]
        queries = self.agent.generate_queries(subject, target_audience, feedback_log)
        self.assertIsInstance(queries, list)
        self.assertGreater(len(queries), 0)

class TestSearchAndRetrievalAgent(unittest.TestCase):
    def setUp(self):
        self.agent = Search_and_Retrieval_Agent()

    def test_execute_queries(self):
        generated_queries = ["customer service complaints", "issues with support"]
        source_filters = ["social media", "forums"]
        results = self.agent.execute_queries(generated_queries, source_filters)
        self.assertIsInstance(results, list)

class TestValidationAgent(unittest.TestCase):
    def setUp(self):
        self.agent = Validation_Agent()

    def test_validate_results(self):
        raw_results = ["I hate waiting on hold", "The service was great"]
        validated = self.agent.validate_results(raw_results)
        self.assertIsInstance(validated, list)
        self.assertIn("I hate waiting on hold", validated)

class TestSynthesisAgent(unittest.TestCase):
    def setUp(self):
        self.agent = Synthesis_Agent()

    def test_compile_report(self):
        validated_pain_points = ["I hate waiting on hold", "The chatbot is useless"]
        report = self.agent.compile_report(validated_pain_points)
        self.assertIsInstance(report, str)
        self.assertIn("Pain Points Report", report)

if __name__ == '__main__':
    unittest.main()