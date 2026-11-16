"""stdio MCP adapter for Blender's official local socket bridge add-on."""

import json
import socket

from mcp.server.fastmcp import FastMCP


HOST = "127.0.0.1"
PORT = 9876
MAX_RESPONSE_BYTES = 10 * 1024 * 1024

mcp = FastMCP("Blender")


def _execute(code: str) -> dict:
    request = json.dumps({"type": "execute", "code": code, "strict_json": True}).encode("utf-8") + b"\0"
    with socket.create_connection((HOST, PORT), timeout=5) as conn:
        conn.settimeout(300)
        conn.sendall(request)
        response = bytearray()
        while b"\0" not in response:
            chunk = conn.recv(4096)
            if not chunk:
                raise RuntimeError("Blender closed the MCP bridge connection")
            response.extend(chunk)
            if len(response) > MAX_RESPONSE_BYTES:
                raise RuntimeError("Blender response exceeded 10 MiB")

    result = json.loads(response.split(b"\0", 1)[0])
    if result.get("status") != "ok":
        raise RuntimeError(result.get("message", "Blender execution failed"))
    return result.get("result", {})


@mcp.tool()
def get_scene_summary() -> dict:
    """Read the current Blender scene, objects, active object, and render size."""
    return _execute(
        "import bpy\n"
        "scene = bpy.context.scene\n"
        "result = {\n"
        "    'scene': scene.name,\n"
        "    'objects': [{'name': obj.name, 'type': obj.type} for obj in scene.objects],\n"
        "    'active_object': bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None,\n"
        "    'render_size': [scene.render.resolution_x, scene.render.resolution_y],\n"
        "}"
    )


@mcp.tool()
def execute_blender_python(code: str) -> dict:
    """Execute Python inside Blender via its local MCP add-on. Set `result` to a JSON-serializable dict. This grants scene-level control; review code before running it."""
    if not code.strip():
        raise ValueError("code must not be empty")
    return _execute(code)


if __name__ == "__main__":
    mcp.run(transport="stdio")
