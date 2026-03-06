print("Importing FastAPI")
from fastapi import FastAPI
print("Importing CORS")
from fastapi.middleware.cors import CORSMiddleware
print("Importing BaseModel")
from pydantic import BaseModel
print("Importing RCA")
from engines.rca import run_pvm_analysis
print("Importing Optimization")
from engines.optimization import run_scenario_optimization

print("Creating App")
app = FastAPI(title="Boardroom Copilot Decision Intelligence API")

print("Adding Middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Finished evaluating main module level code")
