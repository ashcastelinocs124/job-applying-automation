# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("text-generation", model="microsoft/DialoGPT-medium")
result = pipe("Who are you?")
print(result[0]["generated_text"])
    