# ComfyUI MCP server

This optional local MCP server lets an MCP client submit API-format workflows,
inspect the queue and recent history, interrupt generation, and manage pending
jobs. It talks only to the local ComfyUI HTTP API.

Install its optional dependency in the Python environment used to run the MCP
server:

```bash
python -m pip install -r script_examples/requirements-mcp.txt
```

Configure your MCP client to start `script_examples/comfyui_mcp_server.py` with
the ComfyUI repository's Python interpreter. For example, an MCP client using
JSON configuration can use:

```json
{
  "mcpServers": {
    "comfyui": {
      "command": "/path/to/ComfyUI/venv/bin/python",
      "args": ["/path/to/ComfyUI/script_examples/comfyui_mcp_server.py"],
      "env": {"COMFYUI_URL": "http://127.0.0.1:8188"}
    }
  }
}
```

Replace the paths with the local paths on your machine. `COMFYUI_URL` may use a
different port, but must point to a local HTTP server. If ComfyUI Login is
enabled, set `COMFYUI_TOKEN` to the API token shown in its startup log. Keep the
token private. Export workflows in API format from ComfyUI before passing them
to `submit_workflow`.
