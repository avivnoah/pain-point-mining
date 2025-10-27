from agents.search_agent import Query_Generation_Agent
from agents.scraper_agent import Search_and_Retrieval_Agent
from agents.analyzer_agent import Validation_Agent
from agents.aggregator_agent import Synthesis_Agent
from graph.workflow import Workflow
from langgraph_cli.config import Config

def main():
    # Initialize configuration
    config = Config()

    # Create instances of agents
    query_agent = Query_Generation_Agent()
    scraper_agent = Search_and_Retrieval_Agent()
    analyzer_agent = Validation_Agent()
    aggregator_agent = Synthesis_Agent()

    # Initialize the workflow
    workflow = Workflow(query_agent, scraper_agent, analyzer_agent, aggregator_agent)

    # Start the workflow
    workflow.run()

if __name__ == "__main__":
    main()