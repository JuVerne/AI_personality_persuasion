import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OUT_DIR = Path("stimuli_out")
FAIL_DIR = Path("stimuli_out_fail")

WORD_RANGE = (90, 110)
TEMPERATURE = 0.9
PARAPHRASE_IDS = [1, 2, 3]
VARIANTS = ["GENERIC", "E_PLUS", "E_MINUS", "O_PLUS", "O_MINUS"]

MODEL_ALIASES = {
    "llama-3.3-70b-instruct": "llama70",
    "qwen3-30b-a3b-instruct-2507": "qwen30b",
    "mistral-large-3-675b-instruct-2512": "mistral_large",
    "glm-4.7": "glm47",
    "qwen3-235b-a22b": "qwen235b",
}

def model_alias(model_id: str) -> str:
    return MODEL_ALIASES.get(model_id, model_id.replace("/", "_"))

PRODUCTS = {
    "P1": {"product_name": "Weekend city trip",
           "facts_line": "Two nights in a central hotel with breakfast, flexible dates, and free cancellation up to 48 hours before check-in."},
    "P2": {"product_name": "Fitness app",
           "facts_line": "Personalized workouts from 10–30 minutes, progress tracking, and adjustable plans for strength, cardio, or mobility."},
    "P3": {"product_name": "Noise-cancelling headphones",
           "facts_line": "Active noise cancellation, transparency mode, 30-hour battery, and comfortable over-ear fit for travel or focus."},
    "P4": {"product_name": "Language-learning course",
           "facts_line": "Structured lessons, speaking practice, feedback exercises, and weekly goals designed for steady progress."},
    "P5": {"product_name": "Subscription coffee",
           "facts_line": "Fresh beans delivered monthly, your roast preference, flexible skip/pause, and tasting notes included with each delivery."},
    "P6": {"product_name": "Productivity tool",
           "facts_line": "Task lists, calendars, reminders, and templates that sync across devices, with simple sharing for projects."},
}

api_key = os.getenv("CHAT_AI_API_KEY")
BASE_URL = os.getenv("GWDG_BASE_URL", "https://chat-ai.academiccloud.de/v1")

SELECTED_MODELS = [
    "mistral-large-3-675b-instruct-2512",
    "qwen3-30b-a3b-instruct-2507",
]