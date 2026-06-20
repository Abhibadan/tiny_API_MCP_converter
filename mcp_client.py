from fastmcp import Client
import json
import asyncio


client = Client({
    "mcpServers": {
        "api-mcp-converter": {
            "url": "http://localhost:8001/mcp"
        }
    }
}
)

async def main():
    async with client:
        try:
            tools = await client.list_tools()
            print(json.dumps([t.model_dump(mode='json') for t in tools],indent=2))
        except Exception as e:
            print(e)

        try:
            response = await client.call_tool("get_all_posts",{
            "headers":{},
            "body":{},
            "parameters":{},
            "url_params":[]
        })
            print(response)
        except Exception as e:
            print(e)
            



    

asyncio.run(main())