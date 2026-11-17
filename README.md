LangGraph MCP Demo
A simple MCP (Model Context Protocol) project built with LangGraph.

Features
MCP Server
MCP Client
LangGraph Workflow
GitHub Actions CI/CD
Pytest Unit Testing
Project Structure
.
├── mathserver.py
├── mcpclient.py
├── simple.py
├── tests/
│   └── test_math.py
├── requirements.txt
└── .github/workflows/
Installation
pip install -r requirements.txt
Run Application
python simple.py
Run Tests
pytest tests/ -v
CI/CD
GitHub Actions automatically executes:

pip install -r requirements.txt
pytest tests/ -v
whenever code is pushed to the repository.

Technologies Used
Python
LangGraph
MCP
Pytest
GitHub Actions

