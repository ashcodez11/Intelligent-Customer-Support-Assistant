import os
from dotenv import load_dotenv

# Load secret keys
load_dotenv()
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import models
from database import engine, get_db
import shutil

# Initialize FastAPI App & SQL Database
models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="GlowAura Cosmetics AI Support")

# Allows video to show
app.mount("/static", StaticFiles(directory="static"), name="static")

class CustomerQuery(BaseModel):
    user_id: str
    message: str

# 1. Load the "Brain" (100% FREE & LOCAL)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vector_db.as_retriever(search_kwargs={"k": 4})

# 2. Setup OpenRouter FREE AI Model
# PASTE YOUR REAL OPENROUTER KEY BELOW (the one starting with sk-or-v1-...)
# Setup the FREE OpenRouter AI Model securely
llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"), 
    base_url="https://openrouter.ai/api/v1",
    model="openai/gpt-oss-20b:free",
    temperature=0.3
)

# 3. AI Instructions (Relaxed for better recommendations)
system_prompt = (
    "You are a helpful, polite, and luxury beauty advisor for GlowAura Cosmetics. "
    "Use the Company Facts provided below to answer the customer's question. "
    "If they ask for product recommendations, use the facts to suggest the best products for their skin type. "
    "If the customer asks a question that is COMPLETELY unrelated to cosmetics, skincare, or GlowAura's policies, "
    "or if you truly do not have the answer in the facts, reply EXACTLY with the word: ESCALATE_TO_HUMAN\n\n"
    "Company Facts:\n{context}"
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{message}")
])

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("index.html", "r") as f:
        return f.read()

@app.post("/ask")
def ask_assistant(query: CustomerQuery, db: Session = Depends(get_db)):
    try:
        # Search the Vector DB
        docs = retriever.invoke(query.message)
        context = "\n".join([doc.page_content for doc in docs])

        # Ask the FREE OpenRouter AI!
        chain = prompt_template | llm
        response = chain.invoke({"context": context, "message": query.message})
        ai_text = response.content
        
        # Escalation Logic
        if "ESCALATE_TO_HUMAN" in ai_text:
            new_ticket = models.Ticket(
                customer_name=query.user_id,
                issue_summary=query.message,
                status="Open"
            )
            db.add(new_ticket)
            db.commit()
            db.refresh(new_ticket)
            
            ai_text = f"I'm sorry, I don't have the information to help with that. I have escalated this to our human support team. Your Ticket ID is #{new_ticket.id}."

        return {
            "user_query": query.message,
            "ai_response": ai_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickets")
def view_tickets(db: Session = Depends(get_db)):
    tickets = db.query(models.Ticket).all()
    return tickets

@app.post("/admin/upload")
async def upload_knowledge_document(file: UploadFile = File(...)):
    try:
        with open("faq.txt", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"message": f"Successfully uploaded '{file.filename}' and updated the AI Knowledge Base!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))