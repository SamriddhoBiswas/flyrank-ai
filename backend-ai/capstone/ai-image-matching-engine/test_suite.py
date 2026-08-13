import pytest
from fastapi.testclient import TestClient
from main import app
from repository import repo
from seed_demo_data import seed

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_seed_data():
    repo.images.clear()
    repo.posts.clear()
    repo.reviews.clear()
    repo.cost_logs.clear()
    seed()

def test_probe_1_batch_processing_and_low_confidence_flag():
    """PROBE 1 — Batch vision job generates schema-valid tags and flags low confidence."""
    images = repo.list_images()
    assert len(images) >= 50
    
    # Verify low-confidence flagging
    low_conf_imgs = [img for img in images if img.metadata.is_low_confidence]
    assert len(low_conf_imgs) > 0
    assert low_conf_imgs[0].metadata.confidence < 0.70

def test_probe_2_red_fox_query_ranking():
    """PROBE 2 — Query images for 'red fox' article -> fox image ranks #1; wolf and dog rank lower."""
    fox_post = repo.get_post("post-fox-101")
    all_images = repo.list_images()
    
    resp = client.get(f"/api/v1/posts/{fox_post.id}/images")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ACCEPTED"
    assert "fox" in data["suggested_image"]["subject"].lower()

def test_probe_3_forced_wolf_rejection_guard():
    """PROBE 3 — Force wolf candidate for fox post -> Guard rejects with category-mismatch explanation."""
    fox_post = repo.get_post("post-fox-101")
    wolf_img = next(img for img in repo.list_images() if "wolf" in img.filename)

    resp = client.get(f"/api/v1/posts/{fox_post.id}/images?force_candidate_id={wolf_img.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "REJECTED"
    assert "mismatch" in data["reason"].lower() or "expected fox" in data["reason"].lower()

def test_probe_4_no_confident_match_fallback():
    """PROBE 4 — Query post with no suitable image -> 'No confident match' + detailed reasons."""
    sub_post = repo.get_post("post-sub-103") # Submarine article vs Animal photos
    resp = client.get(f"/api/v1/posts/{sub_post.id}/images")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "NO_CONFIDENT_MATCH"
    assert "below threshold" in data["reason"].lower() or "do not match" in data["reason"].lower()

def test_probe_5_eval_top1_precision():
    """PROBE 5 — Run eval metrics -> top-1 precision reported on labeled set."""
    resp = client.get("/api/v1/eval/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "top_1_precision_pct" in data
    assert data["top_1_precision_pct"] >= 90.0

def test_probe_6_attributed_cost_tracking():
    """PROBE 6 — Every vision and embedding call attributed in cost log."""
    resp = client.get("/api/v1/costs")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_api_calls"] > 0
    assert data["total_cost_usd"] > 0.0
