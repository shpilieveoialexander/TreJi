from pydantic import BaseModel


class MsgResponse(BaseModel):
    """Schema for JSON Responses"""

    msg: str
