"""
Startup script that initializes gevent for Cassandra driver
before starting the FastAPI application.

This is necessary for Python 3.13+ compatibility where asyncore was removed.
"""
import os
import sys

# Use gevent as the event loop for cassandra-driver (Python 3.13 compatible)
try:
    from gevent import monkey
    monkey.patch_all()
    print("✓ Gevent monkey patching applied for Cassandra driver")
except ImportError:
    print("Warning: gevent not found, trying asyncio reactor...")
    # Fallback to asyncio
    os.environ['CASSANDRA_DRIVER_EVENT_LOOP'] = 'asyncio'
    import cassandra.io.asyncioreactor
    cassandra.io.asyncioreactor.AsyncioConnection.initialize_reactor()
    print("✓ Cassandra asyncio reactor initialized")

# Now we can safely import the application
from app.main import app

# Now run uvicorn with the app object directly (not string import)
if __name__ == "__main__":
    import uvicorn
    
    print("Starting PathFinder Backend API...")
    print("API: http://localhost:9000")
    print("Docs: http://localhost:9000/docs")
    print("")
    
    uvicorn.run(
        app,  # Pass the app object directly, not as a string
        host="0.0.0.0",
        port=9000,
        reload=False,  # Disable reload to avoid event loop re-initialization issues
        log_level="info"
    )
