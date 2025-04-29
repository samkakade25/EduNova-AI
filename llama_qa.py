import requests
import os

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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"   # <-- paste your key here or load from .env

# Ask a question to the document context
def ask_llama(question, context):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "llama3-8b-8192",   # or any model available in your Groq account
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
        ],
        "temperature": 0.2
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=body)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return "Error in LLM response."

# Summarize entire document
def summarize_document(context):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "llama3-8b-8192",  # or your selected model
        "messages": [
            {"role": "system", "content": "You are a helpful summarizer. Provide concise summaries within 500 tokens."},
            {"role": "user", "content": f"Please provide a concise summary of the following document in no more than 500 tokens:\n\n{context}"}
        ],
        "temperature": 0.3,
        "max_tokens": 500  # Explicitly limit the response to 500 tokens
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=body)

def ask_llm(question, context):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "llama3-8b-8192",   # or any model available in your Groq account
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=body)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return "Error in summarization."
