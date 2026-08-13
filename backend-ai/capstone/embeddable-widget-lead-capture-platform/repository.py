import httpx
import logging
from typing import Dict, Any, List, Optional
from models import Tenant, Widget, Submission, GeoEnrichment

logger = logging.getLogger("WidgetRepository")

class Repository:
    """
    Decoupled Data Repository managing multi-tenant isolation, 
    geo enrichment fallback chains, and non-blocking side effects.
    """
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.widgets: Dict[str, Widget] = {}
        self.submissions: List[Submission] = []
        self.provider_a_enabled = True
        self.provider_b_enabled = True
        self.email_side_effect_enabled = True

    # ---------------------------------------------------------
    # Tenant & Auth Operations
    # ---------------------------------------------------------
    def create_tenant(self, name: str, email: str) -> Tenant:
        tenant = Tenant(name=name, email=email)
        self.tenants[tenant.api_key] = tenant
        return tenant

    def get_tenant_by_key(self, api_key: str) -> Optional[Tenant]:
        return self.tenants.get(api_key)

    # ---------------------------------------------------------
    # Widget Management (Tenant Isolated)
    # ---------------------------------------------------------
    def create_widget(self, tenant_id: str, data: Dict[str, Any]) -> Widget:
        widget = Widget(tenant_id=tenant_id, **data)
        self.widgets[widget.id] = widget
        return widget

    def get_widget(self, widget_id: str) -> Optional[Widget]:
        return self.widgets.get(widget_id)

    def list_widgets_by_tenant(self, tenant_id: str) -> List[Widget]:
        return [w for w in self.widgets.values() if w.tenant_id == tenant_id]

    # ---------------------------------------------------------
    # Geo Enrichment Fallback Chain (Provider A -> Provider B -> Fallback)
    # ---------------------------------------------------------
    async def enrich_ip_geo(self, ip_address: str) -> GeoEnrichment:
        # Provider A (ip-api.com)
        if self.provider_a_enabled:
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    resp = await client.get(f"http://ip-api.com/json/{ip_address}")
                    if resp.status_code == 200:
                        data = resp.json()
                        return GeoEnrichment(
                            ip=ip_address,
                            country=data.get("country", "United States"),
                            city=data.get("city", "San Francisco"),
                            provider_used="Provider A (ip-api.com)"
                        )
            except Exception as e:
                logger.warning(f"Provider A failed: {e}. Falling back to Provider B...")

        # Provider B (ipapi.co)
        if self.provider_b_enabled:
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    resp = await client.get(f"https://ipapi.co/{ip_address}/json/")
                    if resp.status_code == 200:
                        data = resp.json()
                        return GeoEnrichment(
                            ip=ip_address,
                            country=data.get("country_name", "United States"),
                            city=data.get("city", "New York"),
                            provider_used="Provider B (ipapi.co)"
                        )
            except Exception as e:
                logger.warning(f"Provider B failed: {e}. Graceful degradation triggered...")

        # Graceful Degradation: Store submission without geo data
        return GeoEnrichment(ip=ip_address, country="Unknown", city="Unknown", provider_used="None (Degraded)")

    # ---------------------------------------------------------
    # Safe Side Effects (Email/Webhook notification)
    # ---------------------------------------------------------
    async def trigger_email_side_effect(self, submission: Submission):
        if not self.email_side_effect_enabled:
            logger.error("❌ Email Side Effect Failed! Throwing simulated exception...")
            raise Exception("SMTP Server Connection Timeout (Simulated Failure)")
        
        logger.info(f"✉️ Confirmation email sent to '{submission.email}' for submission ID '{submission.id}'.")

    # ---------------------------------------------------------
    # Submission Persistence
    # ---------------------------------------------------------
    async def save_submission(self, widget: Widget, name: str, email: str, message: str, client_ip: str) -> Submission:
        geo = await self.enrich_ip_geo(client_ip)
        
        sub = Submission(
            widget_id=widget.id,
            tenant_id=widget.tenant_id,
            name=name,
            email=email,
            message=message,
            geo=geo
        )
        self.submissions.append(sub)

        # Trigger safe side effect (Failure must NOT block submission storage success)
        try:
            await self.trigger_email_side_effect(sub)
        except Exception as e:
            logger.warning(f"Non-critical side effect failed harmlessly: {e}. Submission row preserved.")

        return sub

# Singleton Repository Instance
repo = Repository()
