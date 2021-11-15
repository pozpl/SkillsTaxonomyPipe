from pydantic import BaseModel
class EntityDto(BaseModel):
    text: str;
    label: str;

