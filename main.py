
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
import uvicorn

from src.DI.container import get_container
from src.env_loader import load_env_file
from src.routes import routes

#FastAPI provides already a way to save instance and reuse (singleton) but we use also DI container for tests and more complex cases

@asynccontextmanager
async def lifespan(app: FastAPI):
    container = get_container()
    db = container.db             
    app.state.db = db
    try:
        yield
    finally:
        db.client.close()

def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(routes.router)
    return app

app = create_app()


    
if __name__ == "__main__": 
    #load_env_file(Path(".env"))
    print("Starting FastAPI server...")
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
    
    
    


