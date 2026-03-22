import textwrap
from config import PRODUCTS, WORD_RANGE

PROMPT_HEADER = f"""\
You are generating one advertisement stimulus for a behavioural experiment.

Output format MUST be exactly four lines:
Hook: <one sentence>
Facts: <one sentence reproduced verbatim from FACTS_LINE>
Framing: <2–3 sentences; targeting happens here>
CTA: <one neutral sentence; no urgency>

Hard constraints:
- Total combined text (Hook+Facts+Framing+CTA) must be {WORD_RANGE[0]}–{WORD_RANGE[1]} words. Count number of words before providing the message to meet the word count requirement.
- Facts line must match FACTS_LINE exactly (verbatim).
- Do NOT add any benefits/claims beyond the facts line.
- Do NOT use social proof, scarcity/urgency, or authority cues.
- Do NOT mention personality labels or address the reader as a trait (e.g., “as an extravert…”).
- Do NOT use bullet points or lists; write natural sentences.
"""

RULE_GENERIC = """\
TARGETING (GENERIC):
Write a general, broadly appealing ad that is NOT tailored to any personality trait.
Keep the framing neutral: avoid strong social/crowd language AND avoid novelty/abstract “exploration” language.
Do not imply “quiet solo recharge” either—stay balanced and mainstream.
"""

RULE_E_PLUS = """\
TARGETING (EXTRAVERSION — HIGH):
Tailor the framing to someone high on Extraversion.
Use a social orientation + energetic/action tone.
Include at least 2 social cues (e.g., friends, together, group, meet people, community) AND at least 2 high-energy/action cues (e.g., lively, buzz, kick off, jump in).
Keep cues natural (no keyword stuffing).
"""

RULE_E_MINUS = """\
TARGETING (EXTRAVERSION — LOW):
Tailor the framing to someone low on Extraversion.
Use calm, autonomy/solo tone.
Include at least 2 autonomy cues (e.g., your own pace, private, solo-friendly, personal space) AND at least 2 low-arousal cues (e.g., calm, unwind, low-key, quiet).
Avoid explicit social words like friends, crowd, meet people, together, community.
Keep cues natural (no keyword stuffing).
"""

RULE_O_PLUS = """\
TARGETING (OPENNESS — HIGH):
Tailor the framing to someone high on Openness.
Emphasize novelty/exploration + abstract/value framing + light aesthetic/creative imagery (grounded, not poetic).
Include at least 2 novelty cues (e.g., discover, new perspectives, unfamiliar, curated, experimental) AND at least 2 abstract/value cues (e.g., meaning, imagination, possibility, perspective, ideas).
Keep cues natural (no keyword stuffing).
"""

RULE_O_MINUS = """\
TARGETING (OPENNESS — LOW):
Tailor the framing to someone low on Openness.
Emphasize conventional/practical/predictable + concrete utility.
Include at least 2 predictability cues (e.g., straightforward, reliable, familiar, no surprises, proven) AND at least 2 utility cues (e.g., simple steps, efficient, clear plan, practical).
Avoid novelty/exploration language like discover, experiment, new perspectives, unexpected.
Keep cues natural (no keyword stuffing).
"""

VARIANT_TO_RULE = {
    "GENERIC": RULE_GENERIC,
    "E_PLUS": RULE_E_PLUS,
    "E_MINUS": RULE_E_MINUS,
    "O_PLUS": RULE_O_PLUS,
    "O_MINUS": RULE_O_MINUS,
}

NOW_GENERATE_BLOCK_TEMPLATE = """\
Now generate for:
PRODUCT_NAME = {product_name}
INTERNAL_VARIANT = {variant}
FACTS_LINE = {facts_line}
PARAPHRASE_ID = {paraphrase_id}
"""

SYSTEM_BASE = """\
You are a precise instruction-following assistant generating advertisement stimuli for a behavioural experiment.
Output ONLY the four labelled lines. No preamble, no explanation, no sign-off.
"""
SYSTEM_WORD_COUNT = """\
WORD COUNT FAILURE IS COMMON. Before outputting, follow these steps:
1. Draft all four lines.
2. Count every word in Hook + Facts + Framing + CTA combined.
3. If below the minimum, expand the Framing sentences only.
4. If above the maximum, trim the Framing sentences only.
5. Only output when the total is within the required range.
"""
SYSTEM_VERBATIM = """\
FACTS LINE: copy the FACTS_LINE character-for-character into the Facts field.
Do not rephrase, shorten, reorder, or change any punctuation.
"""

MODEL_SYSTEM_EXTRAS = {
    "qwen3": [SYSTEM_WORD_COUNT],
    "mistral": [SYSTEM_WORD_COUNT],
    "glm": [SYSTEM_WORD_COUNT, SYSTEM_VERBATIM],
    "llama": [SYSTEM_WORD_COUNT],
    "gpt": [],
}

NO_THINK_MODELS = {"qwen3"}

def append_no_think(model: str, prompt: str) -> str:
    if any(alias in model.lower() for alias in NO_THINK_MODELS):
        return prompt + "\n/no_think"
    return prompt

def build_system_prompt(model: str) -> str:
    extras = []
    for key, blocks in MODEL_SYSTEM_EXTRAS.items():
        if key in model.lower():
            extras = blocks
            break
    return "\n\n".join([SYSTEM_BASE] + extras).strip()

def build_prompt(product_id: str, variant: str, paraphrase_id: int) -> str:
    if variant not in VARIANT_TO_RULE:
        raise ValueError(f"Unknown variant: {variant}")
    if product_id not in PRODUCTS:
        raise ValueError(f"Unknown product_id: {product_id}")
    product = PRODUCTS[product_id]
    rule_block = VARIANT_TO_RULE[variant]
    now_block = NOW_GENERATE_BLOCK_TEMPLATE.format(
        product_name=product["product_name"],
        variant=variant,
        facts_line=product["facts_line"],
        paraphrase_id=paraphrase_id,
    )
    return "\n\n".join([
        textwrap.dedent(PROMPT_HEADER).strip(),
        textwrap.dedent(rule_block).strip(),
        textwrap.dedent(now_block).strip(),
    ])
