from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

app = FastAPI()

# Mistral model ID (ensure you've been granted access on Hugging Face)
model_id = "mistralai/Mistral-7B-Instruct-v0.3"

print("Loading tokenizer and model...")

# Load tokenizer and model in FP16 precision
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.float16,
    trust_remote_code=True
)

# Initialize text generation pipeline
llm = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    return_full_text=False,
)

print("Model loaded and ready.")


# Request body format
class PromptRequest(BaseModel):
    prompt: str
    max_tokens: int = 256
    temperature: float = 0.7


# Text generation endpoint
@app.post("/generate")
def generate_text(data: PromptRequest):
    output = llm(
        data.prompt,
        max_new_tokens=data.max_tokens,
        temperature=data.temperature,
        do_sample=True
    )
    return {"response": output[0]["generated_text"].strip()}