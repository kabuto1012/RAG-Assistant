"""
FastAPI main application for the RDR2 Agent API.
Production-ready REST API with proper error handling, logging, and monitoring.
"""

import asyncio
import time
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.models import QueryRequest, QueryResponse, HealthResponse, ErrorResponse
from coordinator.main_coordinator import RDR2AgentCoordinator
from config.configuration_manager import ConfigurationManager


# Global coordinator instance
coordinator: Optional[RDR2AgentCoordinator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown of the RDR2 Agent system.
    """
    global coordinator
    
    try:
        print("🚀 Starting RDR2 Agent API...")
        
        # Initialize the configuration manager
        config_manager = ConfigurationManager()
        
        # Initialize the coordinator
        coordinator = RDR2AgentCoordinator(config_manager)
        
        print("✅ RDR2 Agent API started successfully!")
        yield
        
    except Exception as e:
        print(f"❌ Failed to start RDR2 Agent API: {e}")
        raise
    finally:
        print("🛑 Shutting down RDR2 Agent API...")
        coordinator = None


# Create FastAPI application
app = FastAPI(
    title="RDR2 Agent API",
    description="Production-ready API for Red Dead Redemption 2 intelligent assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware for web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this for production
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    error_id = str(uuid.uuid4())
    
    print(f"❌ Unhandled error [{error_id}]: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred. Please try again later.",
            timestamp=datetime.now(),
            request_id=error_id
        ).model_dump()
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the RDR2 Agent API and its components"
)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        HealthResponse: Current system status
    """
    try:
        if coordinator is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RDR2 Agent system not initialized"
            )
        
        # Get system status from coordinator
        system_status = coordinator.get_system_status()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            system_info=system_status,
            version="1.0.0"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@app.get(
    "/",
    summary="API Information",
    description="Basic information about the RDR2 Agent API"
)
async def root():
    """
    Root endpoint with basic API information.
    
    Returns:
        dict: Basic API information
    """
    return {
        "service": "RDR2 Agent API",
        "version": "1.0.0",
        "description": "Intelligent assistant for Red Dead Redemption 2",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.now().isoformat()
    }


@app.post(
    "/query",
    response_model=QueryResponse,
    summary="Ask RDR2 Question",
    description="Submit a question about Red Dead Redemption 2 and get an AI-generated answer"
)
async def query_rdr2(request: QueryRequest):
    """
    Process a user query about Red Dead Redemption 2.
    
    Args:
        request: Query request containing the user's question
        
    Returns:
        QueryResponse: AI-generated answer with metadata
        
    Raises:
        HTTPException: If the query processing fails
    """
    start_time = time.time()
    
    try:
        if coordinator is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RDR2 Agent system not initialized"
            )
        
        # Validate question length
        if len(request.question.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty"
            )
        
        print(f"📝 Processing query: {request.question[:100]}...")
        
        # Execute the workflow (run synchronous method in thread pool)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, coordinator.execute_workflow, request.question)
        
        processing_time = time.time() - start_time
        
        if result.success:
            print(f"✅ Query processed successfully in {processing_time:.2f}s")
            
            return QueryResponse(
                answer=result.content,
                success=True,
                processing_time=processing_time,
                timestamp=datetime.now(),
                session_id=request.session_id
            )
        else:
            print(f"❌ Query processing failed: {result.error_message}")
            
            return QueryResponse(
                answer="I'm sorry, I couldn't process your question at this time. Please try again.",
                success=False,
                processing_time=processing_time,
                timestamp=datetime.now(),
                session_id=request.session_id,
                error_message=result.error_message
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Query processing failed: {str(e)}"
        
        print(f"❌ {error_msg}")
        
        # Return a user-friendly error response instead of raising HTTP exception
        return QueryResponse(
            answer="I'm sorry, I encountered an error while processing your question. Please try again.",
            success=False,
            processing_time=processing_time,
            timestamp=datetime.now(),
            session_id=request.session_id,
            error_message=error_msg
        )


@app.get(
    "/status",
    summary="System Status",
    description="Get detailed status information about the RDR2 Agent system components"
)
async def system_status():
    """
    Get detailed system status information.
    
    Returns:
        dict: Detailed system status
    """
    try:
        if coordinator is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RDR2 Agent system not initialized"
            )
        
        status_info = coordinator.get_system_status()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_status": status_info,
            "api_version": "1.0.0",
            "uptime_info": "Available via health endpoint"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system status: {str(e)}"
        )


if __name__ == "__main__":
    """
    Run the API server directly.
    For production, use a proper ASGI server like uvicorn or gunicorn.
    """
    print("🚀 Starting RDR2 Agent API server...")
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Set to True for development
        log_level="info"
    )
