from openai import OpenAI
from config import api_key, BASE_URL, SELECTED_MODELS, VARIANTS, PARAPHRASE_IDS, OUT_DIR, TEMPERATURE, PRODUCTS
from generation import generate_one_message
from records import save_record, load_completed_keys
from config import model_alias

def get_client():
    if not api_key:
        raise EnvironmentError("Set CHAT_AI_API_KEY in your environment first.")
    return OpenAI(api_key=api_key, base_url=BASE_URL)

def main():
    client = get_client()
    completed = load_completed_keys(OUT_DIR)
    total = 0
    for model_id in SELECTED_MODELS:
        alias = model_alias(model_id)
        print(f"\n=== Running model: {model_id} (alias={alias}) ===")
        for product_id in PRODUCTS.keys():
            print(f"\n-- Product {product_id} --")
            for variant in VARIANTS:
                pids = [PARAPHRASE_IDS[0]] if variant == "GENERIC" else PARAPHRASE_IDS
                for pid in pids:
                    job_key = f"{product_id}__{variant}__p{pid}__{model_id}"
                    if job_key in completed:
                        print(f"skip {job_key}")
                        continue
                    print(f"generate {job_key}")
                    record = generate_one_message(
                        product_id=product_id,
                        variant=variant,
                        paraphrase_id=pid,
                        client=client,
                        model=model_id,
                        temperature=TEMPERATURE,
                    )
                    path = save_record(record)
                    total += 1
                    completed.add(job_key)
                    print(f"saved {path} words={record['self_checks']['approx_word_count_full_message']}")
    print(f"\nDone. Generated {total} messages.")