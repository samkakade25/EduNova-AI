import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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"   # <-- paste your key here or load from .env

# Ask a question to the document context
def ask_llama(question, context=None, max_tokens=500):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        if context:
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant. Use the provided context to answer questions accurately."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
            ]
        else:
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": question}
            ]

        body = {
            "model": "llama3-8b-8192",
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": max_tokens
        }

        logger.info(f"Sending request to Groq API with context: {context is not None}")
        response = requests.post(GROQ_API_URL, headers=headers, json=body)
        
        if response.status_code != 200:
            logger.error(f"Groq API error: {response.status_code} - {response.text}")
            raise Exception(f"Groq API error: {response.status_code} - {response.text}")
            
        response_data = response.json()
        if "choices" not in response_data or len(response_data["choices"]) == 0:
            logger.error("Invalid response format from Groq API")
            raise Exception("Invalid response format from Groq API")
            
        return response_data["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error in LLM request: {str(e)}")
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in LLM request: {str(e)}")
        raise Exception(f"Error processing LLM request: {str(e)}")

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
