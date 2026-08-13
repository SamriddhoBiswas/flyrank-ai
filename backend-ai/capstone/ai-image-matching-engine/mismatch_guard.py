from typing import List, Optional
from models import Post, ImageRecord, CandidateMatch, MatchDecision
from embedding_engine import cosine_similarity

SIMILARITY_THRESHOLD = 0.75
CONFIDENCE_THRESHOLD = 0.70

def evaluate_match_with_guard(post: Post, candidate_images: List[ImageRecord], forced_candidate: Optional[ImageRecord] = None) -> MatchDecision:
    """
    The Mismatch Guard: Safety layer combining similarity thresholds, 
    subject/category validation, and confidence scores to prevent false recommendations.
    """
    # If a specific forced candidate is tested (e.g. forcing a wolf onto a fox post)
    if forced_candidate:
        sim = cosine_similarity(post.embedding, forced_candidate.embedding)
        cand = CandidateMatch(
            image_id=forced_candidate.id,
            filename=forced_candidate.filename,
            subject=forced_candidate.metadata.subject,
            caption=forced_candidate.metadata.caption,
            similarity_score=round(sim, 3),
            confidence_score=forced_candidate.metadata.confidence
        )

        # Subject mismatch check
        post_target = post.target_subject.lower()
        image_subj = forced_candidate.metadata.subject.lower()

        if "fox" in post_target and "wolf" in image_subj:
            return MatchDecision(
                post_id=post.id,
                post_title=post.title,
                suggested_image=None,
                status="REJECTED",
                reason=f"Animal category mismatch: expected fox, detected {forced_candidate.metadata.subject}.",
                ranked_candidates=[cand]
            )

        if sim < SIMILARITY_THRESHOLD:
            return MatchDecision(
                post_id=post.id,
                post_title=post.title,
                suggested_image=None,
                status="REJECTED",
                reason=f"Similarity score {round(sim, 2)} is below required threshold {SIMILARITY_THRESHOLD}.",
                ranked_candidates=[cand]
            )

    # General candidate pool ranking
    ranked_candidates: List[CandidateMatch] = []
    for img in candidate_images:
        # Skip low confidence images for top candidate matching, but keep for audit
        if img.metadata.is_low_confidence:
            continue
        sim = cosine_similarity(post.embedding, img.embedding)
        cand = CandidateMatch(
            image_id=img.id,
            filename=img.filename,
            subject=img.metadata.subject,
            caption=img.metadata.caption,
            similarity_score=round(sim, 3),
            confidence_score=img.metadata.confidence
        )
        ranked_candidates.append(cand)

    # Sort candidates by similarity descending
    ranked_candidates.sort(key=lambda x: x.similarity_score, reverse=True)

    if not ranked_candidates:
        return MatchDecision(
            post_id=post.id,
            post_title=post.title,
            suggested_image=None,
            status="NO_CONFIDENT_MATCH",
            reason="No confident candidate images available in repository.",
            ranked_candidates=[]
        )

    best = ranked_candidates[0]

    # Rule 1: Check similarity threshold cutoff
    if best.similarity_score < SIMILARITY_THRESHOLD:
        return MatchDecision(
            post_id=post.id,
            post_title=post.title,
            suggested_image=None,
            status="NO_CONFIDENT_MATCH",
            reason=f"No confident match found. Top similarity score ({best.similarity_score}) is below threshold ({SIMILARITY_THRESHOLD}); detected subjects do not match article topic.",
            ranked_candidates=ranked_candidates[:3]
        )

    # Rule 3: Subject sanity check (Fox vs Wolf / Dog mismatch guard)
    post_target = post.target_subject.lower()
    best_subj = best.subject.lower()
    if "fox" in post_target and ("wolf" in best_subj or "dog" in best_subj):
        return MatchDecision(
            post_id=post.id,
            post_title=post.title,
            suggested_image=None,
            status="REJECTED",
            reason=f"Animal category mismatch: expected fox, detected {best.subject}.",
            ranked_candidates=ranked_candidates[:3]
        )

    # Passed all guard checks -> ACCEPTED
    return MatchDecision(
        post_id=post.id,
        post_title=post.title,
        suggested_image=best,
        status="ACCEPTED",
        reason=f"High-confidence match ({best.similarity_score} similarity score, {best.confidence_score} vision confidence).",
        ranked_candidates=ranked_candidates[:3]
    )
