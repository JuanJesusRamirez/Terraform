uv pip install langgraph
py -3.11 -m uv venv     
py -3.11 -m pip install --upgrade pip
uv pip install "fastapi[standard]"
uv pip install -U "langgraph-cli[inmem]"