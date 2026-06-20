from fastmcp import FastMCP
from fastmcp.tools import Tool
import json
import requests
from pathlib import Path
from models import APIModel, UrlParamsConfig,ResponseStructure
from typing import Annotated, List

mcp = FastMCP("api-mcp-converter")

def mcpFunctionZipper(config: APIModel):
    url_params_config_json = json.dumps([p.model_dump() for p in config.url_params_config], indent=2)

    async def main(
        url_params: Annotated[List[UrlParamsConfig], {f"""The url_params will be concatenated with the base URL.
        The url_params_config is :
        {url_params_config_json}
        and it contains the following information:
        name: The name of the url_param
        value: The value of the url_param
        type: The type of the url_param
        if type is optional, it is not mandatory to provide the value
        if type is required, it is mandatory to provide the value
        The order of url_params in the url will be the same as the order of url_params_config
        """}] = {},
        headers: Annotated[dict, {"The headers will be sent as headers"}] = {},
        body: Annotated[dict, {"The body will be sent as the body of the request"}] = {},
        parameters: Annotated[dict, {"The parameters will be sent as query parameters"}] = {}
    ) -> ResponseStructure:
        try:
            base_url_params = {p.name: p.value for p in config.url_params_config}
            merged_url_params = base_url_params | (url_params if isinstance(url_params, dict) else {})
            url_params_str = "/".join([str(v) for v in merged_url_params.values()])

            merged_headers = config.headers.model_dump() | headers
            merged_body = config.body.model_dump() | body
            merged_parameters = config.parameters.model_dump() | parameters

            url = config.url
            if merged_url_params:
                url += f"/{url_params_str}"

            response = requests.request(
                config.method.upper(), url,
                headers=merged_headers,
                params=merged_parameters,
                json=merged_body if merged_body else None
            )
            response.raise_for_status()
            data = response.json()

            return ResponseStructure(result=data,status="success",statusCode=response.status_code)

        except requests.HTTPError as e:
            return ResponseStructure(result=None,status="error",statusCode=e.response.status_code,error=f"HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            return ResponseStructure(result=None,status="error",statusCode=500,error=str(e))

    main.__name__ = config.title.replace(" ", "_").lower()
    main.__doc__ = f"\n    {config.description}\n    "
    return main

_json_path = Path(__file__).parent.parent / "assets" / "json_mcp_store.json"
with open(_json_path) as file:
    mcp_tools_config = json.load(file)
    for tool in mcp_tools_config:
        tool_declaration = mcpFunctionZipper(APIModel(**tool))
        mcp.add_tool(
            Tool.from_function(
                tool_declaration,
                title=tool["title"],
                output_schema=ResponseStructure.model_json_schema()
            )
        )