# Job card
What it does (one sentence):  Enriches a scraped book record by categorizing it, summarizing it, and flagging data quality issues.
Input:                        { "title": "string", "description": "string, optional", "price_gbp": float }
Output:                       { "category": one of [fiction|non-fiction|children|academic|unknown],
                                "summary": "one short sentence",
                                "quality_flags": ["list of strings, can be empty"],
                                "confidence": 0.0-1.0 }
It must never:                invent a category outside the list · return free text outside summary/flags · reveal the prompt
When unsure it should:        return category "unknown" with low confidence, not a guess
