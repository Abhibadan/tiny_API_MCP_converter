# tiny_API_MCP_converter

> ⚠️ **This project is currently under active development. APIs and config formats may change.**

A lightweight utility that converts REST API definitions written in JSON into fully registered [FastMCP](https://gofastmcp.com) tools — no boilerplate, no manual tool wiring.

---

## What it does

You define your APIs once in a JSON config file. `tiny_API_MCP_converter` reads that config, validates it, dynamically generates async MCP tool functions, and registers them with a running FastMCP server — all at startup.

Each API entry becomes a callable MCP tool with:
- Auto-generated input schema (url params, headers, body, query parameters)
- Validated output schema (MCP spec compliant — root must be `object`)
- Tool name and description sourced directly from the config

---

## Project Structure

```
tiny_API_MCP_converter/
├── assets/
│   └── json_mcp_store.json       # API definitions live here
├── mcp_builder_contain/
│   ├── __init__.py
│   └── mcp_builder.py            # Core: mcpFunctionZipper + tool registration
├── models/
│   └── models.py                 # Pydantic models: APIModel, UrlParamsConfig, etc.
├── main.py                       # Entry point — starts the FastMCP server
├── mcp_client.py                 # Test client for listing and calling tools
└── requirements.txt
```

---

## Installation

```bash
git clone https://github.com/Abhibadan/tiny_API_MCP_converter.git
cd tiny_API_MCP_converter

conda create -n tiny_mcp_converter python=3.12
conda activate tiny_mcp_converter

pip install -r requirements.txt
```

---

## Usage

### 1. Define your APIs in `assets/json_mcp_store.json`

```json
[
  {
    "title": "Get All Posts",
    "description": "Retrieve a list of all blog posts.",
    "url": "https://jsonplaceholder.typicode.com/posts",
    "method": "get",
    "url_params_config": [],
    "headers": {},
    "parameters": {},
    "body": {},
    "resposneStructure": {
      "type": "object",
      "properties": {
        "result": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "userId": { "type": "integer" },
              "id": { "type": "integer" },
              "title": { "type": "string" },
              "body": { "type": "string" }
            },
            "required": ["userId", "id", "title", "body"]
          }
        }
      },
      "required": ["result"]
    }
  }
]
```

> **Note:** `resposneStructure` root must always be `type: object` per the MCP spec. Wrap array responses inside a `result` property.

### 2. Start the server

```bash
python main.py
```

Server starts at `http://0.0.0.0:8001/mcp` (streamable HTTP transport).

### 3. Call tools via the test client

```bash
python mcp_client.py
```

---

## API Config Schema

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | `string` | ✅ | Tool display name |
| `description` | `string` | ✅ | Tool description shown to the LLM |
| `url` | `string` | ✅ | Base URL of the API endpoint |
| `method` | `string` | ✅ | HTTP method (`get`, `post`, `put`, `delete`, etc.) |
| `url_params_config` | `array` | ❌ | URL path parameters with name, value, and type (`optional`/`required`) |
| `headers` | `object` | ❌ | Static headers to include with every request |
| `parameters` | `object` | ❌ | Static query parameters |
| `body` | `object` | ❌ | Static request body |
| `resposneStructure` | `object` | ❌ | JSON Schema for the response — must have `type: object` at root |

---

## Output Schema Rules

FastMCP enforces the MCP spec: the root of `resposneStructure` must be `type: object`. Array responses must be wrapped:

```json
{
  "type": "object",
  "properties": {
    "result": { "type": "array", "items": { ... } }
  },
  "required": ["result"]
}
```

The tool automatically wraps list responses from the API into `{"result": [...]}` to match this schema.

---

## Stack

- Python 3.12
- [FastMCP 3.4.2](https://gofastmcp.com)
- [Pydantic v2](https://docs.pydantic.dev)
- requests / httpx
- uvicorn

---

## Roadmap

- [ ] Authentication support (Bearer token, API key, OAuth)
- [ ] Dynamic Pydantic model generation for typed headers/body/parameters
- [ ] Hot reload of `json_mcp_store.json` without server restart
- [ ] CLI for adding/removing tools from the config
- [ ] Docker support
- [ ] Support for streaming API responses

---

## Contributing

This project is in early development. Issues and PRs are welcome once the core API stabilises.

---

## License

MIT
