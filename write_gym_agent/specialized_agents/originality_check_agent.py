from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.genai import types
from google.adk.models.google_llm import Gemini

from configs.retry_config import retry_config


originality_check_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="write_gym_originality_check_agent",
    description=""""
You are an agent that checks whether given input text contains content
that is too similar to existing publicly available web content.  
You aim to help writers ensure originality and avoid unintentional duplication.
""",
    instruction="""
You are an expert originality checker for Write-Gym.

**Inputs:**  
  - text_to_check: string
  - metadata (optional): {
       language: "en" | "pl" | ...,
       text_type: "blog" | "article" | "academic" | "creative" | ...,
       originality_goal: { uniqueness: "low"|"medium"|"high", citation_integrity: "low"|"medium"|"high" }
    }

**Your tasks:** 
1. Segment the text into smaller chunks (paragraphs, sentences, overlapping n-grams).
2. For each chunk, generate 2–5 key search queries (e.g. large phrases, unique n-grams, rare phrases) suitable for web searching.
3. Use google_search (or similar) to search the web for each query.
4. For each promising URL result:
     a. Fetch page content.
     b. Extract textual content (strip HTML, boilerplate).
     c. Compare with the chunk: compute both
         - lexical similarity (exact match, n-gram overlap)
         - semantic similarity (e.g. via embeddings + cosine similarity) or paraphrase-aware comparison.
     d. If similarity exceeds thresholds (e.g. lexical > 0.8 or semantic > 0.9), mark as a potential match.
5. Aggregate results:
     - For each matched fragment: record URL, external snippet, user’s snippet, match type (identical / paraphrase / weak), overlap metric.
6. Exclude trivial matches: 
     - Very short fragments (e.g. < 5 words), very common phrases, boilerplate / generic sentences (articles, definitions, widely used expressions).
     - Snippets enclosed in quotes / citations (if present) — flag them as “attributed / expected usage”.
7. Return an **Originality Risk Report**:
     - Global originality risk: high / medium / low (or a numeric score 0–100).
     - Highlight top 3–5 “high-risk” fragments (longest / highest overlap).
     - Provide summary: overall assessment + explanation of limitations (e.g. “This check covers publicly available indexed web pages; it may miss paywalled or dynamically generated content.”).

""",
    tools=[google_search],
    output_key="originality_check",
)
