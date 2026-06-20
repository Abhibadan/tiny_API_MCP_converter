from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Literal, List, Optional, Any


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

class ResponseStructure(BaseModel):
    result: Any = Field(description="The result is the response of the API")
    status: Literal['success','error'] = Field(description="The status of the response")
    statusCode: int = Field(description="The status code of the response")
    error: Optional[str] = Field(default=None, description="The error is the error message of the response")