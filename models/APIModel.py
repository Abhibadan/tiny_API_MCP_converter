from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal, List


class HeaderModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class BodyModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class ParameterModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class UrlParamsConfig(BaseModel):
    name: str = Field(description="The name of the url_param")
    value: str = Field(description="The value of the url_param")
    type: Literal['optional', 'required'] = Field(description="The type of the url_param")


class APIModel(BaseModel):
    title: str
    description: str
    url: str
    method: str
    url_params_config: List[UrlParamsConfig] = Field(default=[], description="The url_params_config is a list of UrlParamsConfig that will be used to generate the url_params.")
    headers: HeaderModel = Field(default_factory=HeaderModel, description="The headers is a HeaderModel that will be used to generate the headers.")
    parameters: ParameterModel = Field(default_factory=ParameterModel, description="The parameters is a ParameterModel that will be used to generate the parameters.")
    body: BodyModel = Field(default_factory=BodyModel, description="The body is a BodyModel that will be used to generate the body.")
    resposneStructure: dict = Field(default={}, description="The resposneStructure is a dict that will be used to generate the response structure.")

    @field_validator("resposneStructure")
    @classmethod
    def validate_output_schema(cls, v: dict) -> dict:
        if not v:
            return v

        VALID_TYPES = {"string", "number", "integer", "boolean", "object", "array", "null"}

        def _validate_node(schema: dict, path: str):
            if not isinstance(schema, dict):
                raise ValueError(f"Schema node at '{path}' must be a dict, got {type(schema).__name__}")

            if "type" not in schema:
                raise ValueError(f"Missing 'type' at '{path}'")

            schema_type = schema["type"]
            if schema_type not in VALID_TYPES:
                raise ValueError(f"Invalid type '{schema_type}' at '{path}'. Must be one of {VALID_TYPES}")

            if path == "root" and schema_type != "object":
                raise ValueError(
                    f"MCP spec requires root output schema type to be 'object', got '{schema_type}'. "
                    f"Wrap array/primitive responses as: {{\"type\": \"object\", \"properties\": {{\"result\": <your_schema>}}, \"required\": [\"result\"]}}"
                )

            if schema_type == "object":
                properties = schema.get("properties", {})
                if not isinstance(properties, dict):
                    raise ValueError(f"'properties' at '{path}' must be a dict")
                for prop_name, prop_schema in properties.items():
                    _validate_node(prop_schema, f"{path}.properties.{prop_name}")

                required = schema.get("required", [])
                if not isinstance(required, list):
                    raise ValueError(f"'required' at '{path}' must be a list")
                for req_field in required:
                    if req_field not in properties:
                        raise ValueError(f"'required' field '{req_field}' at '{path}' not found in properties")

            if schema_type == "array":
                if "items" not in schema:
                    raise ValueError(f"'array' type at '{path}' must have an 'items' field")
                _validate_node(schema["items"], f"{path}.items")

        _validate_node(v, "root")
        return v