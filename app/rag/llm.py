# app/rag/llm.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL = "tiiuae/falcon-7b-instruct"  # or your chosen model
DEVICE= "cuda" if torch.cuda.is_available() else "cpu"

tok   = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(MODEL, trust_remote_code=True).to(DEVICE)

def generate(query: str, contexts: list[dict], max_new_tokens: int=128):
    ctx = "\n\n".join([c["text"] for c in contexts])
    prompt = f"Context:\n{ctx}\n\nUser: {query}\nAssistant:"
    inputs  = tok(prompt, return_tensors="pt").to(DEVICE)
    outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)
    text = tok.decode(outputs[0], skip_special_tokens=True)
    return text.split("Assistant:")[-1].strip()
