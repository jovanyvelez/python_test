from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates


app = FastAPI(title="Tienda", version="0.1.0")

# Static files and templates
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
templates = Jinja2Templates(directory="src/web/templates")


def get_device_info(request: Request):
    """Extract device information from request headers."""
    screen_width = int(request.headers.get("x-screen-width", "1024"))
    device_type = request.headers.get("x-device-type", "")
    user_agent = request.headers.get("user-agent", "").lower()
    
    # Fallback detection if headers not present
    if not device_type:
        is_mobile_ua = any(device in user_agent for device in ["mobile", "android", "iphone", "ipod"])
        device_type = "mobile" if (screen_width < 576 or is_mobile_ua) else "desktop"
    
    return {
        "type": device_type,
        "width": screen_width,
        "is_mobile": device_type == "mobile" or screen_width < 576,
        "is_tablet": 576 <= screen_width < 768,
        "is_desktop": screen_width >= 768
    }


def render_mobile_header_normal(cart_count=0):
    """Render mobile normal header layout."""
    return templates.get_template("components/header_mobile_normal.html").render(
        cart_count=cart_count
    )


def render_desktop_header_normal(cart_count=0):
    """Render desktop normal header layout."""
    return templates.get_template("components/header_desktop_normal.html").render(
        cart_count=cart_count
    )


def render_mobile_header_search():
    """Render mobile search header layout."""
    return templates.get_template("components/header_mobile_search.html").render()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Landing page rendering the Jinja2 template."""
    device = get_device_info(request)
    return templates.TemplateResponse("pages/index.html", {
        "request": request, 
        "device": device
    })


@app.get("/api/v1/header/normal-mode", response_class=HTMLResponse)
async def header_normal_mode(request: Request):
    """Return appropriate normal header based on device."""
    device = get_device_info(request)
    
    # TODO: Get actual cart count from session/database
    cart_count = 0
    
    if device["is_mobile"]:
        html_content = render_mobile_header_normal(cart_count)
    else:
        html_content = render_desktop_header_normal(cart_count)
    
    return HTMLResponse(html_content)


@app.get("/api/v1/header/search-mode", response_class=HTMLResponse)
async def header_search_mode(request: Request):
    """Return appropriate search header based on device."""
    device = get_device_info(request)
    
    if device["is_mobile"]:
        html_content = render_mobile_header_search()
        return HTMLResponse(html_content)
    else:
        # Desktop keeps normal view with integrated search
        cart_count = 0  # TODO: Get actual cart count
        html_content = render_desktop_header_normal(cart_count)
        return HTMLResponse(html_content)


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


@app.get("/api/v1/search-suggestions", response_class=HTMLResponse)
async def search_suggestions(request: Request, q: str = ""):
    """Return search suggestions optimized for device."""
    device = get_device_info(request)
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
        no_results_class = "suggestion-mobile no-results" if device["is_mobile"] else "suggestion-desktop no-results"
        return HTMLResponse(f"""
            <div class="{no_results_class}">
                <span style="color: #ccc;">Sin resultados</span>
            </div>
        """)
    
    suggestions_html = ""
    suggestion_class = "suggestion-mobile" if device["is_mobile"] else "suggestion-desktop"
    max_results = 4 if device["is_mobile"] else 6
    
    for name, href in matches[:max_results]:
        suggestions_html += f"""
            <a href="{href}" class="{suggestion_class}">
                <img src="/static/img/search.svg" alt="" width="16" height="16" />
                <span>{name}</span>
            </a>
        """
    
    return HTMLResponse(suggestions_html)


# Optional local entry point; prefer `uv run fastapi dev` in development
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
