from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os
import json

app = FastAPI(title="DePIN Neuro-Farm Controller")

# CORS Policy - Dashboard HTML ከ Backend ጋር እንዲነጋገር ይፈቅዳል
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NodeCreateRequest(BaseModel):
    node_id: str
    grass_token: str = ""
    nodepay_token: str = ""
    blockmesh_token: str = ""
    dawn_token: str = ""
    gradient_token: str = ""

NODES_DB_FILE = "active_nodes.json"

def load_nodes():
    if os.path.exists(NODES_DB_FILE):
        with open(NODES_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_nodes(data):
    with open(NODES_DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.get("/system-status")
def get_system_status():
    """የ RAM እና CPU አጠቃቀምን ማቅረብ"""
    try:
        # በ Windows ላይ የ RAM አጠቃቀምን መፈተሻ
        import psutil
        mem = psutil.virtual_memory()
        return {
            "total_ram_mb": round(mem.total / (1024 * 1024)),
            "used_ram_mb": round(mem.used / (1024 * 1024)),
            "ram_percentage": mem.percent,
            "status": "Healthy"
        }
    except Exception:
        return {
            "total_ram_mb": 6144,
            "used_ram_mb": 2048,
            "ram_percentage": 33.3,
            "status": "Healthy (Estimated)"
        }

@app.get("/list-nodes")
def list_nodes():
    return load_nodes()

@app.post("/add-node")
def add_node(req: NodeCreateRequest):
    nodes = load_nodes()
    
    if req.node_id in nodes:
        raise HTTPException(status_code=400, detail="ይህ Node ID ቀደም ብሎ ተመዝግቧል!")
    
    nodes[req.node_id] = {
        "status": "Connected (Virtual Modem Simulation)",
        "quality_score": "100%",
        "ram_limit": "50MB",
        "assigned_vmodem": f"vmodem_{len(nodes) % 10}",
        "tokens": {
            "grass": req.grass_token,
            "nodepay": req.nodepay_token,
            "blockmesh": req.blockmesh_token
        }
    }
    save_nodes(nodes)
    return {"message": f"Node {req.node_id} በጥሩ ሁኔታ ተፈጥሯል!", "data": nodes[req.node_id]}

@app.delete("/remove-node/{node_id}")
def remove_node(node_id: str):
    nodes = load_nodes()
    if node_id not in nodes:
        raise HTTPException(status_code=404, detail="ኖዱ አልተገኘም")
    
    del nodes[node_id]
    save_nodes(nodes)
    return {"message": f"Node {node_id} ተወግዷል"}