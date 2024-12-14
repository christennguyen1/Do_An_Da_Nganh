from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import user_routes, sensor_routes, relay_routes, setup_routes
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins; specify domains for stricter security
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(user_routes.router, tags=['Users'], prefix='/api/users')
app.include_router(sensor_routes.router, tags=['Sensors'], prefix='/api/sensors')
app.include_router(relay_routes.router, tags=['Relay'], prefix='/api/relay')
app.include_router(setup_routes.router, tags=['Setup'], prefix='/api/setup')

@app.get("/ping")
def ping():
    return {"message": "Server is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)