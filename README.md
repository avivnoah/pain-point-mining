# Pain Point Mining

## Overview
The Pain Point Mining project is a multi-agent system designed to systematically mine the internet for frustrations and complaints related to specific subjects. By leveraging various agents, the system generates queries, scrapes data, validates results, and compiles reports to identify true pain points.

## Project Structure
```
pain-point-mining
├── src
│   ├── main.py                # Entry point for the application
│   ├── agents                 # Contains agent modules
│   │   ├── search_agent.py    # Generates search queries
│   │   ├── scraper_agent.py   # Scrapes data from the internet
│   │   ├── analyzer_agent.py   # Validates and filters results
│   │   └── aggregator_agent.py # Compiles final reports
│   ├── graph                  # Contains workflow logic
│   │   └── workflow.py        # Manages data flow between agents
│   ├── models                 # Contains data models and schemas
│   │   └── schemas.py         # Defines data structures
│   ├── utils                  # Utility functions and configurations
│   │   ├── config.py          # Configuration settings
│   │   └── helpers.py         # Helper functions
│   └── data                   # Data-related modules
├── tests                      # Contains test modules
│   ├── test_agents.py         # Unit tests for agents
│   └── test_workflow.py       # Unit tests for workflow
├── requirements.txt           # Project dependencies
├── .env.example               # Example environment variables
├── .gitignore                 # Files to ignore in version control
└── README.md                  # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd pain-point-mining
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables by copying `.env.example` to `.env` and filling in the necessary values.

## Usage
To run the application, execute the following command:
```
python src/main.py
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.