import os
import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from unsloth import FastLanguageModel

app = FastAPI(title="OriginZero Gemma-4 Inference Engine API")

max_seq_length = 2048
dtype = None
load_in_4bit = True

print("⏳ Loading Base Weights + Your Trained LoRA Adapters...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "AnthonyNwafor/originzero-gemma-4", 
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

FastLanguageModel.for_inference(model)

gemma4_prompt_template = """<start_of_turn>user
Instruction: {}

Context: {}<end_of_turn>
<start_of_turn>model
"""

class InferenceRequest(BaseModel):
    instruction: str
    context: str
    max_new_tokens: int = 256
    temperature: float = 0.3

@app.post("/v1/generate")
async def generate_narrative(request: InferenceRequest):
    try:
        prompt = gemma4_prompt_template.format(request.instruction, request.context)
        inputs = tokenizer(text=[prompt], return_tensors="pt").to("cuda")
        
        is_sampling = True if request.temperature > 0 else False
        
        # Switch to inference_mode (faster execution graph than no_grad)
        with torch.inference_mode():
            outputs = model.generate(
                **inputs, 
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature if is_sampling else None,
                do_sample=is_sampling, 
                use_cache=True,
                # Force termination parameters to halt generation early
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
            )
            
        generated_text = tokenizer.batch_decode(
            outputs[:, inputs.input_ids.shape[1]:], 
            skip_special_tokens=True
        )[0]
        
        return {"response": generated_text.strip()}
        
    except Exception as e:
        print("\n [SERVER ERROR IN GENERATION PIPELINE] 🚨")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))