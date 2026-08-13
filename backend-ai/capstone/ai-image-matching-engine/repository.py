import logging
from typing import Dict, List, Optional
from models import ImageRecord, Post, ReviewAction, CostEntry

logger = logging.getLogger("ImageMatchingRepository")

class Repository:
    """Decoupled Data Store for Images, Embeddings, Posts, Reviews, and Cost Metering."""
    def __init__(self):
        self.images: Dict[str, ImageRecord] = {}
        self.posts: Dict[str, Post] = {}
        self.reviews: List[ReviewAction] = []
        self.cost_logs: List[CostEntry] = []

    def save_image(self, image: ImageRecord):
        self.images[image.id] = image

    def get_image(self, image_id: str) -> Optional[ImageRecord]:
        return self.images.get(image_id)

    def list_images(self) -> List[ImageRecord]:
        return list(self.images.values())

    def save_post(self, post: Post):
        self.posts[post.id] = post

    def get_post(self, post_id: str) -> Optional[Post]:
        return self.posts.get(post_id)

    def list_posts(self) -> List[Post]:
        return list(self.posts.values())

    def record_cost(self, operation_type: str, item_id: str, tokens_or_calls: int, cost_usd: float):
        entry = CostEntry(
            operation_type=operation_type,
            item_id=item_id,
            tokens_or_calls=tokens_or_calls,
            cost_usd=cost_usd
        )
        self.cost_logs.append(entry)

    def total_cost_usd(self) -> float:
        return sum(c.cost_usd for c in self.cost_logs)

    def save_review(self, action: ReviewAction):
        self.reviews.append(action)

repo = Repository()
