import os
import torch
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
import dotenv

dotenv.load_dotenv()

# ==========================================
# 1. MODEL CONFIGURATION & INITIALIZATION
# ==========================================
max_seq_length = int(os.getenv("MAX_SEQ_LENGTH", 2048))  # Adjust based on your context requirements
dtype = None           # None automatically detects your GPU architecture (Float16/Bfloat16)
load_in_4bit = True    # Keep True for ultra-low memory usage on free Colab tier (T4 GPU)

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/gemma-4-E2B-it-unsloth-bnb-4bit", # Fast 4-bit baseline variant
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# Apply LoRA adapter layers targeting parameters for rapid adaptation
model = FastLanguageModel.get_peft_model(
    model,
    r = 32, # Higher numbers mean more trainable parameters (8, 16, 32, 64)
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 64,
    lora_dropout = 0, # Optimized by Unsloth to be 0
    bias = "none",    # Optimized by Unsloth to be none
    use_gradient_checkpointing = "unsloth", # Reduces VRAM usage drastically
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
)

# ==========================================
# 2. DATASET INGESTION & CHAT TEMPLATING
# ==========================================
# Define how Gemma-4 should visualize your Instruction, Context, and Response tokens
gemma4_prompt_template = """<start_of_turn>user
Instruction: {}

Context: {}<end_of_turn>
<start_of_turn>model
{}<end_of_turn>"""

def format_prompts(examples):
    instructions = examples["instruction"]
    contexts     = examples["context"]
    responses    = examples["response"]
    texts = []
    for instruction, context, response in zip(instructions, contexts, responses):
        # Must apply the EOS token at the very end so the model knows when to stop generating
        text = gemma4_prompt_template.format(instruction, context, response) + tokenizer.eos_token
        texts.append(text)
    return { "text" : texts }

# Load your generated data lines file
dataset = load_dataset("json", data_files="originzero_gemma4_dataset.jsonl", split="train")

# Map the raw dataset strings into standard token layouts
dataset = dataset.map(format_prompts, batched=True)

print(f"Dataset successfully mapped! Training Sample Counts: {len(dataset)}")

# ==========================================
# 3. TRAINER CONFIGURATION & EXECUTION
# ==========================================
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False, # Set to True to bundle short sequences together to speed up training
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60, # Scale this up to (len(dataset) * epochs) when running larger scrapes
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
    ),
)

# Execute the training loop
print("\n Commencing OriginZero Gemma-4 Fine-Tuning Optimization...")
trainer_stats = trainer.train()
print("Training Completed Successfully!")

# ==========================================
# 4. EXPORTING THE ADAPTER WEIGHTS
# ==========================================
# Save the final fine-tuned model checkpoint locally in your Colab instance
model.save_pretrained("originzero_gemma4_lora_model")
tokenizer.save_pretrained("originzero_gemma4_lora_model")

print("\nModel adapter parameters compiled and saved locally to directory: 'originzero_gemma4_lora_model'")

# Sign into Hugging Face via terminal or code
# !huggingface-cli login

model.push_to_hub(os.getenv("HF_MODEL_NAME"), token=os.getenv("HF_TOKEN"))
tokenizer.push_to_hub(os.getenv("HF_MODEL_NAME"), token=os.getenv("HF_TOKEN"))
model.push_to_hub_merged(
    os.getenv("HF_MODEL_NAME_MERGED"),
    tokenizer,
    save_method = "merged_4bit_forced",
    token = os.getenv("HF_TOKEN")
)