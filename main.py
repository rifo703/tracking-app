from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import datetime

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

deliveries = []
production = []
completed = []
customers = []

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "deliveries": deliveries,
        "customers": customers
    })

@app.post("/add")
async def add_delivery(
    firma: str = Form(...), adet: int = Form(...), renk: str = Form(...),
    kalinlik: str = Form(...), ozellik: str = Form(...)
):
    deliveries.append({
        "id": len(deliveries) + 1,
        "firma": firma,
        "adet": adet,
        "renk": renk,
        "kalinlik": kalinlik,
        "ozellik": ozellik,
        "tarih": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "asama": ""
    })
    if firma not in customers:
        customers.append(firma)
    return RedirectResponse("/", status_code=303)

@app.post("/delete/{item_id}")
async def delete_delivery(item_id: int):
    global deliveries
    deliveries = [d for d in deliveries if d["id"] != item_id]
    return RedirectResponse("/", status_code=303)

@app.get("/production", response_class=HTMLResponse)
async def show_production(request: Request):
    return templates.TemplateResponse("production.html", {
        "request": request,
        "deliveries": deliveries,
        "production": production,
        "asamalar": ["Yağlama", "Kuru Traş", "Gergi", "Boyama", "Asort Desi"]
    })

@app.post("/start/{item_id}")
async def start_production(item_id: int, asama: str = Form(...)):
    item = next((d for d in deliveries if d["id"] == item_id), None)
    if item:
        item["asama"] = asama
        item["start_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        production.append(item)
        deliveries.remove(item)
    return RedirectResponse("/production", status_code=303)

@app.post("/complete/{item_id}")
async def complete_production(item_id: int):
    item = next((p for p in production if p["id"] == item_id), None)
    if item:
        item["complete_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        completed.append(item)
        production.remove(item)
    return RedirectResponse("/completed", status_code=303)

@app.get("/completed", response_class=HTMLResponse)
async def show_completed(request: Request):
    return templates.TemplateResponse("completed.html", {"request": request, "completed": completed})

@app.post("/add-customer")
async def add_customer(name: str = Form(...)):
    if name not in customers:
        customers.append(name)
    return RedirectResponse("/", status_code=303)
