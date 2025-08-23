from pydantic import BaseModel, Field


class CreateEventResponseDTO(BaseModel):
    event_id: str = Field(..., max_length=8)
