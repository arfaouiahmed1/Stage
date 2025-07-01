from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
import os

# Optional: if using DeepSeek, set API key and base URL
# Comment these out if you're using real OpenAI
#os.environ["OPENAI_API_KEY"] = "sk-c4ab21567aaf41de8680eaec02220f0f"
#os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com"

# Load your PDF file
loader = PyPDFLoader("Evaluation_Question_Bank.pdf")  # Replace with your PDF filename
pages = loader.load()

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(pages)

# Use HuggingFace local embeddings (no API needed)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Build FAISS vector store
vectorstore = FAISS.from_documents(docs, embeddings)
retriever = vectorstore.as_retriever(search_type="similarity", k=3)

# Set up your LLM (either OpenAI or DeepSeek-compatible)
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",  # Or "deepseek-chat"
    temperature=0,
)

# Create QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

# Ask questions in a loop
print(" AI Question Assistant Ready. Type your query or 'exit' to quit.")
while True:
    query = input("\nYour prompt: ").strip()
    if query.lower() in ["exit", "quit", ""]:
        print("👋 Exiting. Goodbye!")
        break

    result = qa_chain.invoke({"query": query})
    print("\n Answer:")
    print(result["result"])
    print("\n" + "-"*50)
