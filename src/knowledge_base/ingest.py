import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def build_knowledge_base():
    print("1. Loading Cosmetics FAQ data...")
    loader = TextLoader("faq.txt")
    documents = loader.load()

    print("2. Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    print("3. Saving to Vector Database (Chroma)...")
    # Using the FREE HuggingFace model instead of OpenAI!
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    print("✅ Cosmetics Knowledge base built successfully!")

if __name__ == "__main__":
    build_knowledge_base()
