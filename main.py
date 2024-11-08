from fastapi import FastAPI
from routes import user_routes, sensor_routes, relay_routes, setup_routes
import uvicorn


app = FastAPI()

# Include routers

app.include_router(user_routes.router, tags=['Users'], prefix='/api/users')
app.include_router(sensor_routes.router, tags=['Sensors'], prefix='/api/sensors')
app.include_router(relay_routes.router, tags=['Relay'], prefix='/api/relay')
app.include_router(setup_routes.router, tags=['Setup'], prefix='/api/setup')

@app.route('/ping', methods=['GET'])
def ping():
    return {"message": "Server is running"}, 200


if __name__ == "__name__":
    uvicorn.run("main:app", host = "0.0.0.0", port = 8080, reload = True)

