# -*- coding: utf-8 -*-
"""ENT CHATBOT.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1AhPz1Bv2S-eV2yRCkHQ5DEhcHNBWf5Ep
"""

!pip install Gradio

!pip install langchain groq sentence-transformers faiss-cpu langchain_community langchain==0.2.11 langchain-community==0.2.10 langchain-text-splitters==0.2.2 langchain-groq==0.1.6 transformers==4.43.2 sentence-transformers==3.0.1 unstructured==0.15.0 unstructured[pdf]==0.15.0 langchain.text_splitters

import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
import requests
import gradio as gr

os.environ["GROQ_API_KEY"] = "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"

# Load the document
loader = TextLoader('/content/Medical data.txt', encoding='utf-8')
documents = loader.load()

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# Load embeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(texts, embedding_model)

# Create retriever
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# Set up Groq LLM
llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0  # Adjust as needed
)

# Define the prompt template
prompt_template = """
You are an assistant for answering questions based on the provided context.
If you don't know the answer, say you don't know.
Provide concise and informative responses.

Question: {question}

Context:
{context}

Answer:
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["question", "context"])

# Create the RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt}
)

# Gradio interface
def answer_question(question):
    return qa_chain.run(question)

interface = gr.Interface(
    fn=answer_question,
    inputs="text",
    outputs="text",
    title="RAG-based Question Answering with Groq LLM",
    description="Ask any question related to the provided document."
)

if __name__ == "__main__":
    interface.launch()

# Function to handle user queries
def chat(question, history):
    # Use the qa_chain to get the answer based on the user's question
    response = qa_chain.run(question)
    return response

# Create the Gradio Chat Interface
demo = gr.ChatInterface(
    fn=chat,  # The function that handles the input and returns a response
    title="Welcome to Your Personal ENT Medical Chatbot",  # Title of the interface
    description="Ask questions related to the medical data provided.",  # Description of the interface
    theme="dark",  # Dark theme for a modern look
    examples=["What is the treatment for condition X?", "Explain the symptoms of Y.", "How do I manage condition Z?"]  # Example questions to guide users
)

# Launch the Gradio interface
if __name__ == "__main__":
    demo.launch(debug=True)