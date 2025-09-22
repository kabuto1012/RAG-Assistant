"""
Startup script for the RDR2 Agent API.
Handles Python path configuration and starts the API server.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting RDR2 Agent API server...")
    
    # Start the server
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
