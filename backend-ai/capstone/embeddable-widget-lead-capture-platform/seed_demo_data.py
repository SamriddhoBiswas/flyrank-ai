import asyncio
from repository import repo

async def seed():
    print("🌱 Seeding Demo Data for Backend AI Capstone...")
    tenant = repo.create_tenant(name="Acme Agency", email="admin@acme.com")
    print(f"  ✓ Created Tenant: '{tenant.name}' | API Key: '{tenant.api_key}'")

    w1 = repo.create_widget(
        tenant_id=tenant.id,
        data={
            "title": "Get a Free AI Audit",
            "description": "Speak with an AI engineer today.",
            "widget_type": "lead_modal",
            "button_text": "Claim Free Audit",
            "accent_color": "#2563EB",
            "allowed_origins": ["*"]
        }
    )
    print(f"  ✓ Created Widget 1 ID: '{w1.id}'")

    w2 = repo.create_widget(
        tenant_id=tenant.id,
        data={
            "title": "Join Newsletter",
            "description": "Weekly AI insights for developers.",
            "widget_type": "signup_form",
            "button_text": "Subscribe Now",
            "accent_color": "#10B981",
            "allowed_origins": ["*"]
        }
    )
    print(f"  ✓ Created Widget 2 ID: '{w2.id}'")

    # Seed sample submissions
    s1 = await repo.save_submission(w1, "Alex Johnson", "alex@example.com", "Interested in AI audit", "8.8.8.8")
    s2 = await repo.save_submission(w2, "Sarah Connor", "sarah@example.com", "Subscribing to newsletter", "1.1.1.1")

    print(f"  ✓ Created {len(repo.submissions)} Sample Submissions (Enriched with Geo data).")
    print("\n✅ SEED COMPLETE! You can run pytest test_suite.py or boot the server with python main.py")

if __name__ == "__main__":
    asyncio.run(seed())
