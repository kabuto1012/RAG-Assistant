"""
FastAPI models for the RDR2 Agent API.
Defines request and response models for the REST API.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for RDR2 queries."""
    
    question: str = Field(
        ..., 
        description="The user's question about Red Dead Redemption 2",
        min_length=1,
        max_length=1000,
        example="What are the best weapons for hunting in RDR2?"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID for tracking user sessions",
        example="user_123_session_456"
    )


class QueryResponse(BaseModel):
    """Response model for RDR2 queries."""
    
    answer: str = Field(
        ...,
        description="The AI-generated answer to the user's question"
    )
    
    success: bool = Field(
        ...,
        description="Whether the query was processed successfully"
    )
    
    processing_time: float = Field(
        ...,
        description="Time taken to process the query in seconds"
    )
    
    timestamp: datetime = Field(
        ...,
        description="When the response was generated"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="Session ID if provided in the request"
    )
    
    error_message: Optional[str] = Field(
        None,
        description="Error message if the query failed"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(
        ...,
        description="API status",
        example="healthy"
    )
    
    timestamp: datetime = Field(
        ...,
        description="Current timestamp"
    )
    
    system_info: Dict[str, Any] = Field(
        ...,
        description="System component status information"
    )
    
    version: str = Field(
        ...,
        description="API version",
        example="1.0.0"
    )


class ErrorResponse(BaseModel):
    """Response model for API errors."""
    
    error: str = Field(
        ...,
        description="Error type",
        example="ValidationError"
    )
    
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    
    timestamp: datetime = Field(
        ...,
        description="When the error occurred"
    )
    
    request_id: Optional[str] = Field(
        None,
        description="Unique request identifier for debugging"
    )
