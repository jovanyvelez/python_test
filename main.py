from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates


app = FastAPI(title="Tienda", version="0.1.0")

# Static files and templates
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
templates = Jinja2Templates(directory="src/web/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Landing page rendering the Jinja2 template."""
    return templates.TemplateResponse("pages/index.html", {
        "request": request
    })


@app.get("/api/v1/mobile-search", response_class=HTMLResponse)
async def mobile_search(request: Request):
    """Return mobile search overlay."""
    return templates.TemplateResponse("components/mobile_search.html", {
        "request": request
    })


@app.get("/api/v1/close-mobile-search", response_class=HTMLResponse)
async def close_mobile_search():
    """Close mobile search overlay."""
    return HTMLResponse("")


@app.get("/api/v1/search-suggestions", response_class=HTMLResponse)
async def search_suggestions(request: Request, q: str = ""):
    """Return search suggestions."""
    q = (q or "").strip().lower()
    
    if not q:
        return HTMLResponse("")
    
    items = [
        ("Camiseta básica", "/products/1"),
        ("Zapatillas running", "/products/2"),
        ("Auriculares inalámbricos", "/products/3"),
        ("Silla ergonómica", "/products/4"),
        ("Cafetera automática", "/products/5"),
        ("Laptop gaming", "/products/6"),
        ("Mouse inalámbrico", "/products/7"),
        ("Teclado mecánico", "/products/8"),
    ]
    
    matches = [item for item in items if q in item[0].lower()]
    if not matches:
        return HTMLResponse("""
            <div style="display: flex; justify-content: center; padding: 1rem; color: #666;">
                Sin resultados
            </div>
        """)
    
    suggestions_html = ""
    max_results = 6
    
    for name, href in matches[:max_results]:
        suggestions_html += f"""
            <a href="{href}">
                <img src="/static/img/search.svg" alt="" width="16" height="16" />
                <span>{name}</span>
            </a>
        """
    
@app.get("/api/v1/products/featured", response_class=HTMLResponse)
async def products_featured():
    """Return an HTML fragment with featured product cards (HTMX target)."""
    cards = []
    for i in range(1, 5):
        cards.append(
            f'''
<article style="border:1px solid rgba(148,163,184,.25);border-radius:.8rem;overflow:hidden;background:linear-gradient(180deg,rgba(255,255,255,.02),rgba(255,255,255,0));">
  <div style="aspect-ratio:4/3;background:#0b1220;"></div>
  <div style="padding:.8rem">
    <h3 style="margin:.2rem 0 .4rem 0;font-size:1.05rem">Producto {i}</h3>
    <p class="muted" style="margin:0 0 .6rem 0">Descripción breve del producto.</p>
    <div style="display:flex;align-items:center;justify-content:space-between">
      <span><strong>$99.99</strong></span>
      <button class="btn" hx-post="/api/v1/cart" hx-vals='{{"product_id": {i}}}' hx-swap="none">Añadir</button>
    </div>
  </div>
</article>
'''
        )
    return HTMLResponse("".join(cards))


@app.post("/api/v1/cart")
async def add_to_cart(product_id: int = Form(...)):
    """Add a product to the cart (placeholder). Returns 204 with an HX trigger."""
    # TODO: Implement real cart persistence/session handling
    headers = {"HX-Trigger": "cart:add"}
    return Response(status_code=204, headers=headers)


# Optional local entry point; prefer `uv run fastapi dev` in development
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
