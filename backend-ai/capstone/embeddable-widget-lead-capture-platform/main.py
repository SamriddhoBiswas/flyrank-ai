import os
import time
import logging
from typing import List, Optional
from fastapi import FastAPI, Request, Response, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import ValidationError

from models import WidgetCreate, SubmissionCreate
from repository import repo

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EmbeddableWidgetPlatform")

app = FastAPI(
    title="FlyRank Embeddable Widget & Lead-Capture Platform",
    description="Production-grade public submission API, embeddable JS widget delivery, CORS handling, rate limiting, and geo fallback enrichment.",
    version="1.0.0"
)

# Enable CORS for all external client website origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory IP rate limiter: 5 requests per 10 seconds
ip_request_timestamps = {}

# ---------------------------------------------------------
# Authentication Dependency (Tenant API Key)
# ---------------------------------------------------------
def get_current_tenant(x_api_key: Optional[str] = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key authentication header.")
    tenant = repo.get_tenant_by_key(x_api_key)
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid API Key.")
    return tenant

# ---------------------------------------------------------
# 1. Health Check
# ---------------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "platform": "FlyRank Embeddable Widget Platform"}

# ---------------------------------------------------------
# 2. Public Cached Embed Script Delivery (GET /widget.js)
# ---------------------------------------------------------
@app.get("/widget.js")
def get_widget_script():
    js_code = """
(function() {
    console.log("🚀 FlyRank Embeddable Widget Bootstrapped!");
    const scripts = document.getElementsByTagName('script');
    let widgetId = null;
    for (let s of scripts) {
        if (s.src && s.src.includes('widget.js')) {
            const urlParams = new URLSearchParams(s.src.split('?')[1]);
            widgetId = urlParams.get('id');
        }
    }
    if (!widgetId) widgetId = 'demo-widget-id';

    const baseUrl = 'http://localhost:8000';
    fetch(`${baseUrl}/api/v1/widgets/${widgetId}/config`)
        .then(r => r.json())
        .then(config => {
            const container = document.createElement('div');
            container.id = 'flyrank-widget-container';
            container.style.position = 'fixed';
            container.style.bottom = '20px';
            container.style.right = '20px';
            container.style.zIndex = '999999';
            container.style.backgroundColor = '#FFFFFF';
            container.style.border = '2px solid ' + (config.accent_color || '#2563EB');
            container.style.borderRadius = '12px';
            container.style.padding = '20px';
            container.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
            container.style.fontFamily = 'sans-serif';
            container.style.maxWidth = '340px';

            container.innerHTML = `
                <h3 style="margin:0 0 8px 0; color:#0F172A;">${config.title}</h3>
                <p style="margin:0 0 14px 0; font-size:14px; color:#475569;">${config.description}</p>
                <form id="flyrank-widget-form">
                    <input type="hidden" name="widget_id" value="${widgetId}">
                    <input type="text" name="bot_field" style="display:none;">
                    <input type="text" name="name" placeholder="Your Name" required style="width:100%; padding:8px; margin-bottom:8px; border:1px solid #CBD5E1; border-radius:6px;">
                    <input type="email" name="email" placeholder="Your Email" required style="width:100%; padding:8px; margin-bottom:8px; border:1px solid #CBD5E1; border-radius:6px;">
                    <textarea name="message" placeholder="Message..." required style="width:100%; padding:8px; margin-bottom:12px; border:1px solid #CBD5E1; border-radius:6px; height:70px;"></textarea>
                    <button type="submit" style="width:100%; background:${config.accent_color || '#2563EB'}; color:#FFF; border:none; padding:10px; border-radius:6px; font-weight:bold; cursor:pointer;">${config.button_text}</button>
                </form>
                <div id="flyrank-widget-status" style="margin-top:10px; font-size:13px; font-weight:bold;"></div>
            `;
            document.body.appendChild(container);

            document.getElementById('flyrank-widget-form').addEventListener('submit', function(e) {
                e.preventDefault();
                const form = e.target;
                const statusDiv = document.getElementById('flyrank-widget-status');
                statusDiv.innerText = 'Submitting... ⏳';

                const payload = {
                    widget_id: widgetId,
                    name: form.name.value,
                    email: form.email.value,
                    message: form.message.value,
                    bot_field: form.bot_field.value || null
                };

                fetch(`${baseUrl}/api/v1/submissions`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                })
                .then(res => {
                    if (res.status === 429) throw new Error('Rate limit exceeded (429)!');
                    if (!res.ok) throw new Error('Submission failed (' + res.status + ')');
                    return res.json();
                })
                .then(data => {
                    statusDiv.style.color = '#10B981';
                    statusDiv.innerText = '✓ Success! Enriched & Stored.';
                    form.reset();
                })
                .catch(err => {
                    statusDiv.style.color = '#EF4444';
                    statusDiv.innerText = '❌ Error: ' + err.message;
                });
            });
        });
})();
    """
    return Response(
        content=js_code,
        media_type="application/javascript",
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
            "Access-Control-Allow-Origin": "*"
        }
    )

# ---------------------------------------------------------
# 3. Public Cached Widget Config Delivery (GET /api/v1/widgets/{id}/config)
# ---------------------------------------------------------
@app.get("/api/v1/widgets/{widget_id}/config")
def get_widget_config(widget_id: str):
    widget = repo.get_widget(widget_id)
    if not widget:
        # Fallback default widget for demo/tests
        return JSONResponse(
            content={
                "id": widget_id,
                "title": "Get a Free Strategy Call",
                "description": "Fill out the form below to speak with an AI engineer.",
                "widget_type": "lead_modal",
                "button_text": "Submit Request",
                "accent_color": "#2563EB",
                "allowed_origins": ["*"]
            },
            headers={
                "Cache-Control": "public, max-age=60",
                "Access-Control-Allow-Origin": "*"
            }
        )
    
    return JSONResponse(
        content=widget.dict(),
        headers={
            "Cache-Control": "public, max-age=60",
            "Access-Control-Allow-Origin": "*"
        }
    )

# ---------------------------------------------------------
# 4. Public Submission Endpoint (POST /api/v1/submissions)
# ---------------------------------------------------------
@app.post("/api/v1/submissions", status_code=status.HTTP_201_CREATED)
async def create_submission(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"

    # Rate Limiting Audit (Max 5 requests per 10s window)
    now = time.time()
    timestamps = ip_request_timestamps.get(client_ip, [])
    timestamps = [t for t in timestamps if now - t < 10]
    if len(timestamps) >= 5:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Maximum 5 submissions per 10 seconds allowed."
        )
    timestamps.append(now)
    ip_request_timestamps[client_ip] = timestamps

    # Oversized Payload Audit (> 100 KB reject with HTTP 413)
    raw_body = await request.body()
    if len(raw_body) > 102400: # 100 KB limit
        raise HTTPException(status_code=413, detail="Payload Too Large. Max allowed is 100 KB.")

    # Boundary Payload Validation
    try:
        json_data = await request.json()
        payload = SubmissionCreate(**json_data)
    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=f"Validation Error: {ve.errors()}")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON Payload.")

    # Honeypot Spam Prevention Check
    if payload.bot_field:
        logger.warning(f"🤖 Bot submission detected! Honeypot filled: '{payload.bot_field}'. Dropping submission silently.")
        return JSONResponse(status_code=200, content={"status": "success", "message": "Submission received."})

    # Fetch widget configuration
    widget = repo.get_widget(payload.widget_id)
    if not widget:
        widget = repo.create_widget(
            tenant_id="default-tenant",
            data={
                "title": "Default Widget",
                "description": "Auto-created widget",
                "widget_type": "lead_modal",
                "button_text": "Submit",
                "accent_color": "#2563EB",
                "allowed_origins": ["*"]
            }
        )

    # Save submission with Geo Fallback & Safe Side Effects
    sub = await repo.save_submission(
        widget=widget,
        name=payload.name,
        email=payload.email,
        message=payload.message,
        client_ip=client_ip
    )

    return {
        "status": "success",
        "submission_id": sub.id,
        "geo_enriched": sub.geo.dict(),
        "created_at": sub.created_at.isoformat()
    }

# ---------------------------------------------------------
# 5. Authenticated Admin Widget Management (CRUD)
# ---------------------------------------------------------
@app.post("/api/v1/admin/widgets", status_code=status.HTTP_201_CREATED)
def create_widget_admin(data: WidgetCreate, tenant=Depends(get_current_tenant)):
    widget = repo.create_widget(tenant.id, data.dict())
    embed_snippet = f'<script src="http://localhost:8000/widget.js?id={widget.id}"></script>'
    return {
        "widget": widget.dict(),
        "embed_snippet": embed_snippet
    }

@app.get("/api/v1/admin/widgets")
def list_widgets_admin(tenant=Depends(get_current_tenant)):
    widgets = repo.list_widgets_by_tenant(tenant.id)
    return {"widgets": [w.dict() for w in widgets]}

# ---------------------------------------------------------
# 6. Owner Dashboard API (Stats & Submissions)
# ---------------------------------------------------------
@app.get("/api/v1/dashboard/stats")
def get_dashboard_stats():
    total_subs = len(repo.submissions)
    geo_breakdown = {}
    for s in repo.submissions:
        country = s.geo.country
        geo_breakdown[country] = geo_breakdown.get(country, 0) + 1

    return {
        "total_submissions": total_subs,
        "total_widgets": len(repo.widgets),
        "geo_breakdown": geo_breakdown,
        "provider_a_status": "ONLINE" if repo.provider_a_enabled else "OFFLINE",
        "provider_b_status": "ONLINE" if repo.provider_b_enabled else "OFFLINE"
    }

@app.get("/api/v1/dashboard/submissions")
def get_dashboard_submissions():
    return {"submissions": [s.dict() for s in repo.submissions]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
