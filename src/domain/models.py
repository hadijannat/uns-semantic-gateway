import time
from typing import Literal, Any, Optional
from pydantic import BaseModel, Field, field_validator


class UNSPayload(BaseModel):
    """
    The 'Golden Record' for the Unified Namespace.
    Standardizes all incoming data to a strict ISA-95 schema.
    """
    value: Any
    timestamp: int = Field(
        default_factory=lambda: int(time.time() * 1000),
        description="Epoch milliseconds"
    )
    quality: Literal["Good", "Bad", "Uncertain"] = "Good"
    unit: str
    asset_id: str
    metadata: Optional[dict] = None

    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: int) -> int:
        """Business Logic: Ensure timestamp is reasonable (not from 1970)."""
        if v < 1700000000000:
            raise ValueError("Timestamp too old - must be after Nov 2023")
        return v

    def to_json(self) -> str:
        """Serialize for MQTT publishing."""
        return self.model_dump_json(exclude_none=True)
