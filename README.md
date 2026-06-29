cat << 'EOF' > README.md
# GlowAura Cosmetics - AI Customer Support Assistant

An enterprise-grade AI-powered customer support platform designed for luxury skincare brands.

## Project Overview

GlowAura is an intelligent customer support system that uses Retrieval-Augmented Generation (RAG) to provide instant, accurate answers from company documents. The platform reduces customer support workload, improves response speed, and escalates complex issues to human agents.

## Key Features

- **AI Chatbot:** Natural language understanding with LangChain
- **RAG System:** Retrieves answers from company knowledge base
- **Product Recommendations:** AI suggests products based on skin type
- **Knowledge Upload:** Admin dashboard to update company documents
- **Human Escalation:** Automatic ticket creation for unresolved queries
- **SQL Ticketing:** Track customer escalations in database
- **Luxury UI:** Premium, responsive frontend with animations

## Technologies

**Backend:** Python, FastAPI, SQLAlchemy, SQLite
**AI/ML:** LangChain, ChromaDB, HuggingFace Embeddings, OpenRouter API
**Frontend:** HTML5, CSS3, JavaScript
**Database:** SQLite

## System Architecture

1. Customer submits question via chatbot
2. System searches ChromaDB vector database for relevant company documents
3. AI (via OpenRouter) generates response using retrieved context
4. If answer not found, system creates SQL ticket for human agent
5. Admin can upload new documents to continuously train the AI

## How to Run

```bash
cd "Intelligent Customer Support Assistant"
source venv/bin/activate
pip install -r requirements.txt
export OPENROUTER_API_KEY=your_key_here
uvicorn main:app --reload
