from pydantic import BaseModel


class TeableObjectLinkSchema(BaseModel):
    id: str
    title: str
