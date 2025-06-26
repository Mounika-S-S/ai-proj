import os
from dotenv import load_dotenv
load_dotenv()

# Using transformers and llama for local inference
from transformers import LlamaTokenizer, LlamaForCausalLM
import torch

# Load GPT-Neo model and tokenizer (free and publicly available)
from transformers import GPTNeoForCausalLM, GPT2Tokenizer

model_name_or_path = "EleutherAI/gpt-neo-125M"
tokenizer = GPT2Tokenizer.from_pretrained(model_name_or_path)
model = GPTNeoForCausalLM.from_pretrained(model_name_or_path)

def generate_text_with_gptneo(prompt, max_length=300):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=max_length, do_sample=True, temperature=0.7)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text

def generate_personal_statement(prompt):
    system_prompt = "You are an expert at writing personal statements."
    full_prompt = f"{system_prompt}\nUser: {prompt}\nPersonal Statement:"
    return generate_text_with_gptneo(full_prompt, max_length=300)

def generate_team_members(prompt):
    system_prompt = (
        "You are an AI that generates team members based on project details. "
        "Reply with a concise list of 3 to 4 single-word roles only, separated by commas, "
        "such as 'Frontend, Backend, Designer'. "
        "Do not include any additional text or explanation."
    )
    full_prompt = f"{system_prompt}\nUser: {prompt}\nTeam Roles:"
    output = generate_text_with_gptneo(full_prompt, max_length=150)

    roles = []
    # Split output by commas and strip whitespace
    role_names = [role.strip() for role in output.replace('\n', ',').split(',') if role.strip()]
    # Filter to keep only single-word roles
    single_word_roles = [role for role in role_names if ' ' not in role]
    emp_id = 100  # Dummy starting employee ID
    for role_name in single_word_roles[:4]:  # Limit to 4 roles
        roles.append({"employee_id": emp_id, "role": role_name})
        emp_id += 1
    return roles
