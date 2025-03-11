# Setup Instructions

## Backend Setup

### Python Environment
1. Install Python 3.11.9 (stable version with latest minor change, supports langraph local server)
2. If multiple Python versions exist, use:
```bash
py -3.11 -m
py -3.11 -m pip install --upgrade pip
```
3. Create virtual environment using your preferred package manager (venv, virtualenv, or uv). Note: Conda not recommended due to potential package compatibility limitations.

### Using UV (Recommended)
4. Install UV:
```bash
py -3.11 -m pip install uv
```

5. Create and activate virtual environment:
```bash
py -3.11 -m uv venv
.venv\Scripts\activate
```

### Package Installation
6. Upgrade pip:
```bash
py -3.11 -m pip install --upgrade pip
```

7. Install FastAPI:
```bash
uv pip install "fastapi[standard]"
```

8. Install Langgraph:
```bash
uv pip install langgraph
```

9. Install local server extension:
```bash
uv pip install -U "langgraph-cli[inmem]"
```

### Running Backend Server
You can use either of these commands:
```bash
cd backend; fastapi dev
# or
cd backend; uvicorn main:app --reload
```

### Agent Debugging
#### Edit this file according th agent that you will evaluated, this ax example with "agent_a"
C:{path}\RALFR3_V2\backend\app\agents\langgraph.json
{
    "dependencies": ["./backend/requirements.txt"],
    "graphs": {
        "raflr3": "./agent_a.py:graph"
    },
    "python_version": "3.11"
}

Execute these commands:
```bash
cd C:{path}\RALFR3_V2\backend\app\agents
langgraph dev
```

## Frontend Setup

1. Install Streamlit:
```bash
uv pip install streamlit
```

2. Run local server:
```bash
cd frontend; streamlit run main.py
```

## Running Both Backend and Frontend

You can run both the backend and frontend servers in a single terminal using Git Bash. Execute the following command:

```bash
bash start.sh
```
