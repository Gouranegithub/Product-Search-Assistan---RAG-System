from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd 

# Check if Ollama is running and model is available
try:
    df = pd.read_csv("products-10000.csv")
    print(f"Loaded {len(df)} products from CSV")
    
    # Try to initialize embeddings
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    print("Embeddings initialized successfully")
    
    db_location = "./chroma_langchain_db"
    add_documents = not os.path.exists(db_location)
    
    if add_documents:
        print("Creating new vector database...")
        documents = []
        ids = []

        for i, row in df.iterrows():
            # Create comprehensive searchable content
            searchable_content = f"""
            Product: {row["Name"]}
            Description: {row["Description"]}
            Brand: {row["Brand"]}
            Category: {row["Category"]}
            Price: {row["Price"]} {row["Currency"]}
            Color: {row["Color"]}
            Size: {row["Size"]}
            Availability: {row["Availability"]}
            Stock: {row["Stock"]}
            """.strip()
            
            document = Document(
                page_content=searchable_content,
                metadata = {
                    "name": row["Name"],
                    "description": row["Description"],
                    "brand": row["Brand"],
                    "category": row["Category"],
                    "price": row["Price"], 
                    "currency": row["Currency"],
                    "color": row["Color"],
                    "size": row["Size"],
                    "availability": row["Availability"],
                    "stock": row["Stock"],
                    "ean": row["EAN"],
                    "internal_id": row["Internal ID"],
                    "id": str(i)
                }
            )
            ids.append(str(i))
            documents.append(document)
        
        print(f"Created {len(documents)} documents")

    vector_store = Chroma(
        collection_name="product_descriptions",
        persist_directory=db_location,
        embedding_function=embeddings
    )

    if add_documents:
        print("Adding documents to vector store...")
        vector_store.add_documents(documents=documents, ids=ids)
        print("Documents added successfully")

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 5}
    )
    
    print("Retriever created successfully")
    
except Exception as e:
    print(f"Error initializing vector store: {e}")
    # Fallback: create a dummy retriever
    retriever = None