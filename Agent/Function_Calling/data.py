"""
    Fucntion Calling模型如何训练？
    并不是让模型具备执行函数的能力，而是让模型学会输出包含函数调用信息的回复：
    {函数名、函数参数...}
    处理数据、训练模型、评估模型、部署模型...关键在于“数据如何制备”
"""


from enum import Enum
from functools import partial
import pandas as pd
import torch
import json

from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
from datasets import load_dataset
from trl import SFTConfig, SFTTrainer
from peft import LoraConfig, TaskType

seed = 42
set_seed(seed)

import os

import subprocess
import os

# 这是 aistackdc 用于 Github/huggingface 下载加速的方式
result = subprocess.run('bash -c "source /etc/network/turbo && env | grep proxy"', shell=True, capture_output=True, text=True)
output = result.stdout
for line in output.splitlines():
    if '=' in line:
        var, value = line.split('=', 1)
        os.environ[var] = value


model_name = "Qwen/Qwen2.5-0.5B-Instruct"
dataset_name = "Jofthomas/hermes-function-calling-thinking-V1"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 备注：这里的 model 
tokenizer.chat_template = "{{ bos_token }}{% if messages[0]['role'] == 'system' %}{{ raise_exception('System role not supported') }}{% endif %}{% for message in messages %}{{ '<|im_start|>' + message['role'] + '\n' + message['content'] | trim + '<|im_end|>\n' }}{% endfor %}{% if add_generation_prompt %}{{'<|im_start|>assistant\n'}}{% endif %}"


def preprocess(sample):
    messages = sample["messages"]
    first_message = messages[0]

    # Instead of adding a system message, we merge the content into the first user message
    if first_message["role"] == "system":
        system_message_content = first_message["content"]
        # Merge system content with the first user message
        messages[1]["content"] = system_message_content + "Also, before making a call to a function take the time to plan the function to take. Make that thinking process between <think>{your thoughts}</think>\n\n" + messages[1]["content"]
        # Remove the system message from the conversation
        messages.pop(0)

    return {"text": tokenizer.apply_chat_template(messages, tokenize=False)}


dataset = load_dataset(dataset_name)
dataset = dataset.rename_column("conversations", "messages")

print(preprocess(dataset["train"][0]))

def convert_model_to_assistant(sample):
    messages = sample["messages"]
    for message in messages:
        if message["role"] == "model":
            message["role"] = "assistant"
        if message["role"] == "human":
            message["role"] = "user"
    return sample

dataset = dataset.map(convert_model_to_assistant)

print(dataset['train'][0])

dataset = dataset.map(preprocess, remove_columns="messages")
dataset = dataset["train"].train_test_split(0.1)
print(dataset)

print(dataset["train"][8]["text"])

# Sanity check
print(tokenizer.pad_token)
print(tokenizer.eos_token)

class ChatmlSpecialTokens(str, Enum):
    tools = "<tools>"
    eotools = "</tools>"
    think = "<think>"
    eothink = "</think>"
    tool_call="<tool_call>"
    eotool_call="</tool_call>"
    tool_response="<tool_reponse>"
    eotool_response="</tool_reponse>"
    pad_token = "<|endoftext|>"
    eos_token = "<|im_end|>"
    @classmethod
    def list(cls):
        return [c.value for c in cls]

tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        pad_token=ChatmlSpecialTokens.pad_token.value,
        additional_special_tokens=ChatmlSpecialTokens.list()
    )
tokenizer.chat_template = "{{ bos_token }}{% if messages[0]['role'] == 'system' %}{{ raise_exception('System role not supported') }}{% endif %}{% for message in messages %}{{ '<|im_start|>' + message['role'] + '\n' + message['content'] | trim + '<|im_end|>\n' }}{% endfor %}{% if add_generation_prompt %}{{'<|im_start|>assistant\n'}}{% endif %}"

