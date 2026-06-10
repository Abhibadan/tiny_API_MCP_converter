from fastapi import FastAPI,HTTPException,Response
from fastmcp.tools import Tool
import json
# from fastmcp.client import Client
# import asyncio
from pathlib import Path
from mcp_builder_contain import mcp,mcpFunctionZipper
from models import APIModel


# mcp.list_tools


app = FastAPI()

@app.get("/mcp-tools")
async def get_mcp_tools():
    tools = await mcp.list_tools()
    print(tools)
    return [{"name": t.name, "description": t.description} for t in tools]

@app.post("/register-mcp-tool")
def create_mcp_tool(apiDescription:APIModel):
    try:
        _json_path = Path(__file__).parent / "assets" / "json_mcp_store.json"
        with open(_json_path,"r") as file:
            mcp_tools_config = json.load(file)
            mcp_tools_config.append(apiDescription.model_dump(mode="json"))
            
        with open(_json_path,"w") as file:
            json.dump(mcp_tools_config,file)
        tool_declaration=mcpFunctionZipper(apiDescription)
        mcp.add_tool(
            Tool.from_function(
                tool_declaration,
                output_schema=tool_declaration.output_schema
            )
        )
        return Response(status_code=200,content=json.dumps({"message":"Tool registered successfully"}))
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error registering tool: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import asyncio

    async def main():
        # Run FastMCP (SSE) and FastAPI (uvicorn) concurrently in one event loop
        mcp_task = asyncio.create_task(
            mcp.run_async(transport="http", host="0.0.0.0", port=8001)
        )
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        app_task = asyncio.create_task(server.serve())
        await asyncio.gather(mcp_task, app_task)

    asyncio.run(main())
