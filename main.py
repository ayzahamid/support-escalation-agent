from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from schemas import SupportRequest, PipelineResponse
from orchestrator import Orchestrator

app = FastAPI(
    title="Bank Support API",
    description="Multi-agent customer support system for banking queries.",
    version="2.0.0",
)

_orchestrator: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


# ── Support endpoint ──────────────────────────────────────────────────────────

@app.post("/support", response_model=PipelineResponse, tags=["Support"])
def handle_support_request(request: SupportRequest):
    """
    Run a customer query through the full multi-agent pipeline:
    Relevance → Classification → Support (with tools) → Escalation (if needed).
    """
    try:
        return get_orchestrator().handle(request.query)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "Bank Support API"}


# ── Items CRUD (original endpoints) ──────────────────────────────────────────

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    in_stock: bool = True


items: dict[int, Item] = {}
_next_id = 1


@app.get("/items", response_model=dict[int, Item], tags=["Items"])
def list_items():
    return items


@app.get("/items/{item_id}", response_model=Item, tags=["Items"])
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]


@app.post("/items", response_model=dict, tags=["Items"])
def create_item(item: Item):
    global _next_id
    items[_next_id] = item
    created_id = _next_id
    _next_id += 1
    return {"id": created_id, "item": item}


@app.put("/items/{item_id}", response_model=Item, tags=["Items"])
def update_item(item_id: int, item: Item):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id] = item
    return item


@app.delete("/items/{item_id}", tags=["Items"])
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    del items[item_id]
    return {"message": f"Item {item_id} deleted"}
