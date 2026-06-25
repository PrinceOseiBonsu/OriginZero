import json
from unsloth import FastLanguageModel

# 1. Initialize the Tokenizer
# We load just the tokenizer to save time and VRAM
max_seq_length = 2048
_, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/gemma-4-E2B-it-unsloth-bnb-4bit",
    max_seq_length = max_seq_length,
    load_in_4bit = True,
)

# 2. Define the exact template used during training
gemma4_prompt_template = """<start_of_turn>user
Instruction: {}

Context: {}<end_of_turn>
<start_of_turn>model
{}<end_of_turn>"""

# 3. Process the dataset file and count tokens
total_dataset_tokens = 0
sample_count = 0

print("Counting tokens in 'originzero_gemma4_dataset.jsonl'...")

# Safely extract the actual text tokenizer if it is wrapped inside a Processor
actual_tokenizer = getattr(tokenizer, "tokenizer", tokenizer)

with open("../originzero_gemma4_dataset.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)

        # Reconstruct the exact string format fed to the model
        full_text = gemma4_prompt_template.format(
            data["instruction"],
            data["context"],
            data["response"]
        ) + actual_tokenizer.eos_token

        # Tokenize the string and measure its length
        tokens = actual_tokenizer.encode(full_text, add_special_tokens=False)
        total_dataset_tokens += len(tokens)
        sample_count += 1

# ==========================================
# 4. CALCULATE TRAINING METRICS
# ==========================================
# These parameters should match your TrainingArguments exactly
BATCH_SIZE = 2
GRADIENT_ACCUMULATION_STEPS = 4
MAX_STEPS = 60

# Calculate how many tokens are processed in a single weight update step
tokens_per_step = BATCH_SIZE * GRADIENT_ACCUMULATION_STEPS * max_seq_length
# Calculate the total mathematical capacity used by the trainer configuration
total_gradient_tokens = MAX_STEPS * tokens_per_step

print("\n" + "="*45)
print("ORIGINZERO TOKEN COUNT REPORT")
print("="*45)
print(f"Total Unique Samples:     {sample_count:,}")
print(f"Total Corpus Data Tokens: {total_dataset_tokens:,} tokens")
print(f"Average Tokens / Sample:  {round(total_dataset_tokens / sample_count, 1)} tokens")
print("-"*45)
print(f"Total Gradient Tokens:    {total_gradient_tokens:,} tokens")
print(f"*(Based on {MAX_STEPS} steps, batch size {BATCH_SIZE}, and context padding)*")
print("="*45)
