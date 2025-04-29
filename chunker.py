def chunk_text(text, max_tokens=500):
    sentences = text.split('.')
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_tokens:
            current_chunk += sentence + '.'
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + '.'
    if current_chunk:
        chunks.append(current_chunk)
    return chunks
