"""LLM-as-judge prompts for insight groundedness (optional live path)."""

GROUNDEDNESS = """
Score 1-5 how well the insight is grounded in the provided raw responses.
1 = invented, 5 = every claim is supported by cited persona answers.
Return JSON: {"score": int, "rationale": str}
"""
