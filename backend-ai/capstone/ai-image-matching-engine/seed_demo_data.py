from repository import repo
from models import ImageRecord, Post
from vision_engine import analyze_image_content
from embedding_engine import generate_embedding

def seed():
    print("🌱 Seeding Demo Dataset (~50 Images & Target Articles)...")
    
    # 1. Seed ~50 Image Files
    image_files = []
    for i in range(1, 16):
        image_files.append(f"red_fox_{i:02d}.jpg")
    for i in range(1, 11):
        image_files.append(f"gray_wolf_{i:02d}.jpg")
    for i in range(1, 11):
        image_files.append(f"domestic_dog_{i:02d}.jpg")
    for i in range(1, 8):
        image_files.append(f"grizzly_bear_{i:02d}.jpg")
    for i in range(1, 6):
        image_files.append(f"white_tailed_deer_{i:02d}.jpg")
    for i in range(1, 4):
        image_files.append(f"blurry_shape_low_conf_{i:02d}.jpg")

    for fn in image_files:
        analysis, v_cost = analyze_image_content(fn)
        embedding, e_cost = generate_embedding(analysis.caption)
        
        img = ImageRecord(
            filename=fn,
            url=f"http://localhost:8000/static/images/{fn}",
            metadata=analysis,
            embedding=embedding
        )
        repo.save_image(img)
        repo.record_cost("VISION_ANALYSIS", img.id, 1, v_cost)
        repo.record_cost("EMBEDDING_GENERATION", img.id, 1, e_cost)

    print(f"  ✓ Processed & Saved {len(repo.images)} Images with Vision Tags and 16-D Embeddings.")

    # 2. Seed Posts
    p1_title = "The Behavior of Red Foxes in Autumn Forests"
    p1_text = "Red foxes (Vulpes vulpes) display remarkable solitary hunting behaviors in dense woodland habitats..."
    p1_emb, p1_cost = generate_embedding(p1_text)
    p1 = Post(id="post-fox-101", title=p1_title, content=p1_text, topic_category="animal", target_subject="red fox", embedding=p1_emb)
    repo.save_post(p1)
    repo.record_cost("EMBEDDING_GENERATION", p1.id, 1, p1_cost)

    p2_title = "Gray Wolf Pack Dynamics and Territorial Hunting"
    p2_text = "Gray wolves rely on intricate vocalizations and social hierarchies to defend vast winter territories..."
    p2_emb, p2_cost = generate_embedding(p2_text)
    p2 = Post(id="post-wolf-102", title=p2_title, content=p2_text, topic_category="animal", target_subject="gray wolf", embedding=p2_emb)
    repo.save_post(p2)
    repo.record_cost("EMBEDDING_GENERATION", p2.id, 1, p2_cost)

    p3_title = "Deep Sea Submarine Exploration in Abyssal Trenches"
    p3_text = "Hydrothermal vents located 10,000 meters below sea level support unique chemosynthetic ecosystems..."
    p3_emb, p3_cost = generate_embedding(p3_text)
    p3 = Post(id="post-sub-103", title=p3_title, content=p3_text, topic_category="oceanography", target_subject="submarine", embedding=p3_emb)
    repo.save_post(p3)
    repo.record_cost("EMBEDDING_GENERATION", p3.id, 1, p3_cost)

    print(f"  ✓ Processed & Saved {len(repo.posts)} Articles (Fox, Wolf, Submarine).")
    print(f"  ✓ Total Attributed AI Cost Logged: ${round(repo.total_cost_usd(), 6)} USD.")
    print("\n✅ SEED COMPLETE! You can run pytest test_suite.py -v or boot python main.py")

if __name__ == "__main__":
    seed()
