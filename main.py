from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import streamlit as st
from vector import retriever

# Streamlit page setup
st.set_page_config(page_title="Groq LLaMA3 Chat", page_icon="🧠", layout="centered")
st.title("🧠 Product Search Assistant")
st.write("Built with **LangChain + Streamlit + Groq**")

# Load your API key from the .env file
load_dotenv()

# Initialize the Groq LLaMA 3 model
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",  
    temperature=0.7,
)

# Initialize chat history
if "history" not in st.session_state:
    st.session_state["history"] = []

# Chat input
user_input = st.chat_input("Ask me anything...")

# Display previous messages
for msg in st.session_state["history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle new input
if user_input:
    # Add user message
    st.session_state["history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response
    with st.chat_message("assistant"):
        if retriever is not None:
            try:
                # Get relevant documents from retriever
                relevant_docs = retriever.invoke(user_input)
                
                if relevant_docs:
                    # Format the retrieved information with better structure
                    context_parts = []
                    for i, doc in enumerate(relevant_docs, 1):
                        context_parts.append(f"Product {i}:\n{doc.page_content}")
                    
                    context = "\n\n".join(context_parts)
                    
                    prompt = ChatPromptTemplate.from_template("""
                    You are a helpful product recommendation assistant. Based on the following product information, answer the user's question about products.
                    
                    Available Products:
                    {context}
                    
                    User Question: {question}
                    
                    Please provide helpful and detailed information about the products that match the user's query. Include product names, descriptions, prices, and availability when relevant.
                    """)
                    
                    chain = prompt | llm
                    response = chain.invoke({"context": context, "question": user_input})
                    st.markdown(response.content)
                    
                    # Add model reply to history
                    st.session_state["history"].append({"role": "assistant", "content": response.content})
                else:
                    st.markdown("I couldn't find any relevant products in the database. Please try a different search term.")
                    st.session_state["history"].append({"role": "assistant", "content": "I couldn't find any relevant products in the database. Please try a different search term."})
            except Exception as e:
                st.markdown(f"Error retrieving products: {str(e)}")
                st.session_state["history"].append({"role": "assistant", "content": f"Error retrieving products: {str(e)}"})
        else:
            st.markdown("Vector database is not available. Please check if Ollama is running and the embedding model is installed.")
            st.session_state["history"].append({"role": "assistant", "content": "Vector database is not available. Please check if Ollama is running and the embedding model is installed."})
