# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch

# # Your chosen model path
# MODEL_PATH = "tiiuae/falcon-7b-instruct"
# DEVICE     = "cuda" if torch.cuda.is_available() else "cpu"

# # Load once at import time
# tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
# model     = AutoModelForCausalLM.from_pretrained(MODEL_PATH).to(DEVICE)

# def generate(query: str, contexts: list[dict], max_new_tokens: int = 128) -> str:
#     """
#     Build a prompt that forces precise extraction.
#     If the exact answer isn’t in the contexts, reply "Information not available".
#     """
#     context_text = "\n\n".join([c["text"] for c in contexts])
#     prompt = f"""
# You are a precise assistant. Use ONLY the information below to answer the question.
# If the exact answer isn’t present, reply "Information not available".

# Context:
# {context_text}

# Question: {query}

# Answer:
# """
#     inputs  = tokenizer(prompt, return_tensors="pt").to(DEVICE)
#     outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)
#     return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

import re, time, requests, os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()
HF_TOKEN = os.getenv("HF_API_TOKEN", "")
MODEL_ID = "HuggingFaceH4/zephyr-7b-beta"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

def _post_with_retry(url, headers, payload, n_retry=5):
    for _ in range(n_retry):
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code == 503:
            time.sleep(resp.json().get("estimated_time", 5) + 0.5)
            continue
        return resp
    return resp

def _extract_answer(text: str) -> str:
    parts = re.split(r'(?i)answer:', text, maxsplit=1)
    answer = parts[1] if len(parts) == 2 else text
    for stop in ("\n\n", "\n###", "</s>"):
        answer = answer.split(stop, 1)[0]
    return answer.strip()

def generate(query: str, contexts: list[dict], max_new_tokens: int = 128, mode: str = "strict") -> str:
    context_text = "\n\n".join(c["text"] for c in contexts)
    if mode == "strict":
        prompt = (
            "You are a precise assistant. Use ONLY the information below to answer the question.\n"
            "If the exact answer isn’t present, reply exactly: Information not available.\n\n"
            f"Context:\n{context_text}\n\n"
            f"Question: {query}\n\n"
            "Answer:"
        )
    else:
        prompt = (
            "You are a helpful and engaging assistant. Use the context below if relevant, otherwise answer freely.\n\n"
            f"Context:\n{context_text}\n\n"
            f"User: {query}\nAssistant:"
        )

    headers = {
        **({"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}),
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": 0.6 if mode == "chat" else 0.1,
            "top_p": 0.9,
        },
    }

    resp = _post_with_retry(API_URL, headers, payload)

    if resp.status_code != 200:
        try:
            detail = resp.json().get("error", resp.text)
        except ValueError:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=f"HF Inference error: {detail}")

    try:
        body = resp.json()
    except ValueError:
        return _extract_answer(resp.text)

    if isinstance(body, list) and body and isinstance(body[0], dict):
        return _extract_answer(body[0].get("generated_text", ""))
    if isinstance(body, dict):
        return _extract_answer(body.get("generated_text", ""))

    raise HTTPException(status_code=500, detail=f"Unexpected HF response format: {body}")

