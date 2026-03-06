from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Boardroom Copilot Decision Intelligence API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since this is a local tool
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Boardroom Copilot Engine running"}

@app.post("/api/analyze")
def analyze_query(request: QueryRequest):
    # This acts as the LLM Intent Router placeholder
    # In a real app, LangChain/LlamaIndex would parse the intent here.
    query_lower = request.query.lower()
    
    response_payload = {
        "insight": "Analysis complete.",
        "charts": [],
        "rca": None,
        "scenario": None
    }
    
    if "diagnose" in query_lower or "why" in query_lower or "margin dip" in query_lower:
        # Route to RCA (PVM) Engine
        # hardcoded data for MVP proxy
        from engines.rca import run_pvm_analysis
        rca_result = run_pvm_analysis()
        response_payload["rca"] = rca_result
        response_payload["insight"] = "I have run a Price-Volume-Mix analysis on the variance. Here is the mathematical breakdown of the margin dip."
        
    elif "fix" in query_lower or "scenario" in query_lower or "optimize" in query_lower:
        # Route to Decision Science Optimization Engine
        # E.g. trying to recover a $1.2M gap
        from engines.optimization import run_scenario_optimization
        scenario_result = run_scenario_optimization(current_margin_gap=120000, baseline_volume=500000)
        response_payload["scenario"] = scenario_result
        response_payload["insight"] = f"Optimization complete. {scenario_result.get('prescription')}"
        
    else:
        response_payload["insight"] = f"General BI Analysis complete for: {request.query}"

    return response_payload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
