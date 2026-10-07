from pydantic import BaseModel, Field
from typing import Literal, List

class OrchestratorOutput(BaseModel):
    response_text: str = Field(..., description="The response text to be sent to the user.")
    confidence: float = Field(..., description="Confidence score of the response from 0.0 to 1.0.")
    domain: Literal['clinical', 'general'] = Field(..., description="Domain of the intent.")
    mc_constraints: List[str] = Field(default_factory=list, description="List of constraints or guidelines followed.")
