from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import Response
from pdf_reader import extract_text_from_pdf
from chunker import chunk_text
from embedder import get_embedding
from vector_store import create_faiss_index, save_faiss, load_faiss
from llama_qa import ask_llama, summarize_document
from pdf_generator import create_student_report_pdf
import os
import numpy as np
from db import get_student_data
from prompts import STUDENT_FEEDBACK_PROMPT, LEARNING_RESOURCES_PROMPT
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

API_KEY = "mysecretkey123"  # change this to your secret

texts = []
index = None

def verify_key(key: str):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...), key: str = Form(...)):
    verify_key(key)
    
    global texts, index
    
    file_location = f"temp/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, "wb+") as f:
        f.write(await file.read())

    text = extract_text_from_pdf(file_location)
    chunks = chunk_text(text)
    embeddings = [get_embedding(chunk) for chunk in chunks]
    index = create_faiss_index(embeddings)
    save_faiss(index, chunks)
    texts = chunks
    
    return {"message": f"Processed {len(chunks)} chunks."}

@app.post("/ask/")
async def ask_question(question: str = Form(...), key: str = Form(...)):
    verify_key(key)
    
    global texts, index
    if index is None:
        index, texts = load_faiss()
    
    question_vector = np.array([get_embedding(question)])
    distances, indices = index.search(question_vector, k=3)
    relevant_chunks = " ".join([texts[i] for i in indices[0]])
    
    answer = ask_llama(question, relevant_chunks)
    return {"answer": answer}

@app.post("/summarize/")
async def summarize(key: str = Form(...)):
    verify_key(key)
    
    global texts
    full_text = " ".join(texts)
    summary = summarize_document(full_text)
    return {"summary": summary}

@app.get("/feedback/{student_id}")
async def get_feedback(
    student_id: int, 
    key: str = Query(..., description="API key for authentication"),
    format: str = Query("json", description="Response format: 'json' or 'pdf'")
):
    try:
        verify_key(key)
        
        try:
            student, marks, assignments, attendance = get_student_data(student_id)
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error fetching student data: {str(e)}")
            raise HTTPException(status_code=500, detail="Error fetching student data")

        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        try:
            # Format the data using named tuple attributes
            marks_text = "\n".join(f"{m.subject} - {m.score}" for m in marks)
            assignments_text = "\n".join(f"{a.title} - {a.grade}" for a in assignments)
            attendance_text = "\n".join(f"{a.subject} - {a.percentage}%" for a in attendance)

            prompt = STUDENT_FEEDBACK_PROMPT.format(
                name=student.name,
                year=student.year,
                department=student.department,
                marks=marks_text or "No marks available",
                assignments=assignments_text or "No assignments available",
                attendance=attendance_text or "No attendance records available"
            )
        except Exception as e:
            logger.error(f"Error formatting student data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing student data: {str(e)}")

        try:
            feedback = ask_llama(prompt, "")
            
            if format.lower() == 'pdf':
                # Prepare data for PDF generation
                student_data = {
                    'name': student.name,
                    'year': student.year,
                    'department': student.department,
                    'marks': [{'subject': m.subject, 'score': m.score} for m in marks],
                    'assignments': [{'title': a.title, 'grade': a.grade} for a in assignments],
                    'attendance': [{'subject': a.subject, 'percentage': a.percentage} for a in attendance]
                }
                
                # Generate PDF
                pdf = create_student_report_pdf(student_data, feedback)
                return Response(
                    content=pdf,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"attachment; filename=student_{student_id}_report.pdf"
                    }
                )
            else:
                return {"student_id": student_id, "feedback": feedback}
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise HTTPException(status_code=500, detail="Error generating response")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.post("/get_learning_resources/")
async def get_learning_resources(student_id: int = Form(...), key: str = Form(...)):
    try:
        verify_key(key)
        
        try:
            student, marks, assignments, attendance = get_student_data(student_id)
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Error fetching student data: {str(e)}")
            raise HTTPException(status_code=500, detail="Error fetching student data")

        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        try:
            # Get student feedback first
            marks_text = "\n".join(f"{m.subject} - {m.score}" for m in marks)
            assignments_text = "\n".join(f"{a.title} - {a.grade}" for a in assignments)
            attendance_text = "\n".join(f"{a.subject} - {a.percentage}%" for a in attendance)

            feedback_prompt = STUDENT_FEEDBACK_PROMPT.format(
                name=student.name,
                year=student.year,
                department=student.department,
                marks=marks_text or "No marks available",
                assignments=assignments_text or "No assignments available",
                attendance=attendance_text or "No attendance records available"
            )
            
            feedback = ask_llama(feedback_prompt, "")
            
            # Generate learning resources
            resources_prompt = LEARNING_RESOURCES_PROMPT.format(
                name=student.name,
                year=student.year,
                department=student.department,
                feedback=feedback
            )
            
            resources = ask_llama(resources_prompt, "")
            
            if not resources or resources.strip() == "":
                raise HTTPException(status_code=500, detail="Empty response from AI model")
            
            # Parse the JSON response
            import json
            try:
                # Try to clean the response if it's not valid JSON
                cleaned_response = resources.strip()
                if not cleaned_response.startswith('{'):
                    # Try to find the first '{' and last '}'
                    start = cleaned_response.find('{')
                    end = cleaned_response.rfind('}')
                    if start != -1 and end != -1:
                        cleaned_response = cleaned_response[start:end+1]
                
                resources_data = json.loads(cleaned_response)
                
                # Validate the response structure
                if not isinstance(resources_data, dict):
                    raise ValueError("Response is not a dictionary")
                if 'articles' not in resources_data or 'statistics' not in resources_data:
                    raise ValueError("Missing required fields in response")
                if not isinstance(resources_data['articles'], list) or not isinstance(resources_data['statistics'], list):
                    raise ValueError("Articles and statistics must be arrays")
                
                # Validate each article
                for i, article in enumerate(resources_data['articles']):
                    required_fields = ['title', 'source', 'description', 'url']
                    if not all(field in article for field in required_fields):
                        raise ValueError(f"Article {i} missing required fields: {required_fields}")
                
                # Validate each statistic
                for i, stat in enumerate(resources_data['statistics']):
                    required_fields = ['metric', 'value', 'description']
                    if not all(field in stat for field in required_fields):
                        raise ValueError(f"Statistic {i} missing required fields: {required_fields}")
                
                return resources_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse learning resources response as JSON: {str(e)}")
                raise HTTPException(status_code=500, detail="Error processing learning resources: Invalid JSON format")
            except ValueError as e:
                logger.error(f"Invalid response structure: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error processing learning resources: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error generating resources: {str(e)}")
            raise HTTPException(status_code=500, detail="Error generating learning resources")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")