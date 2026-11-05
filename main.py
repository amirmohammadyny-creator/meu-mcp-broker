from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import subprocess
import json
import os

app = FastAPI(title="Meu AI MCP Broker")
SECRET_KEY = os.getenv("BROKER_SECRET", "my-super-secret-key")

class ToolRequest(BaseModel):
    server_name: str
    tool_name: str
    arguments: dict

@app.post("/call-tool")
async def call_tool(req: ToolRequest, authorization: str = Header(None)):
    if not authorization or authorization != f"Bearer {SECRET_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    server_map = {
        "digikala": "iran-mcp-digikala",
        "divar": "iran-mcp-divar",
        "torob": "iran-mcp-torob"
    }
    
    uvx_package = server_map.get(req.server_name)
    if not uvx_package:
        raise HTTPException(status_code=400, detail="Server not supported by broker yet")

    try:
        rpc_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": req.tool_name,
                "arguments": req.arguments
            },
            "id": 1
        }
        
        process = subprocess.Popen(
            ["uvx", uvx_package],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=json.dumps(rpc_request) + "\n", timeout=30)
        
        for line in stdout.splitlines():
            if line.strip().startswith("{"):
                response = json.loads(line)
                return {"result": response.get("result", {})}
                
        raise HTTPException(status_code=500, detail=f"Invalid MCP response. Stderr: {stderr}")

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Tool execution timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    return {"status": "Broker is running!"}
