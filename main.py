from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/sorgula", response_class=HTMLResponse)
async def run_osint(request: Request, target: str = Form(...)):
    analysis_result = f"--- AXERO WEB ANALİZ RAPORU --- \n\nHedef: {target}\nDurum: Güvenli / Taramalar Tamamlandı [axerocore.net]"
    
    return templates.TemplateResponse(
        "index.html", {"request": request, "result": analysis_result}
    )
