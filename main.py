import uvicorn
from fastapi import FastAPI
from Restful_api import RestFul_api

app = FastAPI()

app.include_router(RestFul_api)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
