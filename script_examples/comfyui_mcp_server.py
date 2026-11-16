"""Local MCP tools for submitting and managing ComfyUI API workflows."""

import ipaddress
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _base_url():
    url = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
    parsed = urlsplit(url)
    if parsed.scheme != "http" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("COMFYUI_URL must be a local http URL, such as http://127.0.0.1:8188")
    try:
        local = parsed.hostname == "localhost" or ipaddress.ip_address(parsed.hostname).is_loopback
    except ValueError:
        local = False
    if not local or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("COMFYUI_URL must point to a local ComfyUI server")
    return url


def _api(path, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("COMFYUI_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(_base_url() + path, data=data, headers=headers)
    try:
        with urlopen(req, timeout=30) as response:
            raw = response.read()
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ComfyUI returned HTTP {error.code}: {detail}") from error
    except URLError as error:
        raise RuntimeError(f"Could not reach ComfyUI: {error.reason}") from error
    if not raw:
        return {"ok": True}
    return json.loads(raw)


mcp = FastMCP("ComfyUI")


@mcp.tool()
def get_queue() -> dict:
    """Return currently running and pending ComfyUI jobs."""
    return _api("/queue")


@mcp.tool()
def get_history(max_items: int = 20) -> dict:
    """Return recent completed ComfyUI jobs."""
    if max_items < 1:
        raise ValueError("max_items must be positive")
    return _api(f"/history?max_items={max_items}")


@mcp.tool()
def submit_workflow(workflow: dict) -> dict:
    """Submit an API-format workflow exported from ComfyUI."""
    if not workflow:
        raise ValueError("workflow must not be empty")
    return _api("/prompt", {"prompt": workflow, "extra_data": {"comfy_usage_source": "comfyui-mcp"}})


@mcp.tool()
def interrupt(prompt_id: str = "") -> dict:
    """Interrupt the current job, or the specified running job."""
    payload = {"prompt_id": prompt_id} if prompt_id else {}
    return _api("/interrupt", payload)


@mcp.tool()
def clear_pending_queue() -> dict:
    """Remove all waiting jobs from the queue."""
    _api("/queue", {"clear": True})
    return {"ok": True}


@mcp.tool()
def remove_pending_job(prompt_id: str) -> dict:
    """Remove a waiting job by its prompt ID."""
    if not prompt_id:
        raise ValueError("prompt_id must not be empty")
    _api("/queue", {"delete": [prompt_id]})
    return {"ok": True, "prompt_id": prompt_id}


if __name__ == "__main__":
    mcp.run(transport="stdio")
