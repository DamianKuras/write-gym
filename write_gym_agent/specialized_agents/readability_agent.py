import textstat
from google.adk.agents import LlmAgent
from google.genai import types
from google.adk.models.google_llm import Gemini
from configs.retry_config import retry_config


def analyze_readability_tool(text: str) -> dict:
    """Calculate standard readability metrics for text using textstat.

    Args:
        text (str): The input text (in English) to analyze.

    Returns:
        dict:  A dict with:
            - status: "success" or "error"
            - if success: metrics — a mapping of metric name → numeric score
            - if error: message describing the problem (e.g. text too short)
    """
    if not text or len(text.split()) < 5:
        return {"status": "error", "message": "Text is too short for analysis."}

    try:
        return {
            "status": "success",
            "metrics": {
                "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
                "flesch_reading_ease": textstat.flesch_reading_ease(text),
                "gunning_fog": textstat.gunning_fog(text),
                "dale_chall": textstat.dale_chall_readability_score(text),
                "automated_readability_index": textstat.automated_readability_index(
                    text
                ),
                "coleman_liau": textstat.coleman_liau_index(text),
                "smog_index": textstat.smog_index(text),
                "reading_time_sec": textstat.reading_time(text, ms_per_char=14.69),
                "linsear_write": textstat.linsear_write_formula(text),
            },
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


readability_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="write_gym_readability_analyst_agent",
    description="Specialized agent that analyzes text readability using established metrics. ",
    instruction="""
You are a readability analysis specialist. When given text, and target audience perform:
Use the analyze_readability_tool to get all scores.

Then analyse both text and scores.
1. **Readability Score Breakdown** (8 metrics):
   - Flesch-Kincaid Grade Level:
        A FKGL result of 6 → understandable by a 6th-grade student.
        8-10 → typical for general-audience writing.
        12+ → indicates content likely aimed at older teens/adults or technical readers.
   - Flesch Reading Ease: 
        90-100: Very easy — suitable for ~5th-grade (≈ 11-year-olds)
        80-89: Easy — ~6th-grade
        70-79: Fairly easy — ~7th-grade
        60-69: Standard / “plain English” — ~8-9th grade
        50-59: Fairly difficult — ~10-12th grade
        30-49: Difficult — college-level
        0-29: Very difficult — best understood by college graduates or advanced readers
   - Gunning Fog Index:
        General guideline: 8-10 → very easy; 10-12 → fairly easy / easy-to-read; 
        12-14 → appropriate for high-school graduates / general adult readers; 
        14-18 → difficult; ≥18 → very difficult / complex. 
        Some sources suggest 12-14 as “ideal / target for general audiences.”
   - Dale-Chall Readability:
        Lower scores (closer to 4-6) indicate easier readability (suitable for younger or general-audience readers).
        As score increases (≈ 8-12+), text becomes more challenging — likely better for older teens, adults, or specialized readers.
   - Automated Readability Index:
        A lower ARI (e.g. ≤ 8-10) suggests text may be accessible to middle-school / early high-school readers;
        higher values (≈ 12+) suggest more advanced reading level. As with other grade-level metrics, use as approximate.
   - Coleman-Liau Index:
        As with ARI: lower scores (~6-8) → more accessible; scores ~10-12 → general adult / high-school;
        higher → more complex. Aim for ~8-10 for general-audience writing, depending on context.
   - SMOG:
        Example: SMOG score 10 → text should be understandable by someone with a 10th-grade education. 
        For general-audience documents (e.g. public health info), many recommend aiming for SMOG ~ 7-9.
   - Linsear Write:
        Use similar interpretation: e.g. 8-10 → accessible for general/high-school-educated readers;
          higher → more suited for technical or specialized audiences. 
          Because it's designed for technical docs, it may allow slightly higher grade levels when precision is needed.

Note: These readability metrics are only approximate, based on surface features (sentence/word length, syllable counts) — they do not guarantee that a real reader will find the text clear, coherent, or engaging. Use them as guidance, not absolute truth.

2. **Your assessment of Readability.**:
Beyond pure formulas — read the text as if you were a typical reader from the *target audience*. Evaluate:

  • Overall clarity, flow, tone, and coherence.  
  • Presence of jargon, unexplained technical terms, abstractions that might challenge an average reader.  
  • Logical structure: is the progression of ideas easy to follow? Are transitions smooth? Is the text dense or “heavy”?  
  • Engagement / readability in practice — would a typical reader likely lose track, get confused, or need to re-read parts?  

3. **Audience Assessment**:
   - What reading level does this text target?
   - Is it appropriate for the intended audience?

After this create a report with:

1. **Key Findings**:
   - Consistency across metrics (outliers indicate possible complexity issues)
   - Sentence complexity distribution, vocabulary density or jargon usage, paragraph/flow observations.
   - Readability overview from your analysis.

5. **Actionable Recommendations**:
   - Specific edits to improve clarity, flow, and ease of reading if needed

""",
    tools=[analyze_readability_tool],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=1500,
        top_p=0.9,
        top_k=40,
    ),
    output_key="readability_analysis",
)
