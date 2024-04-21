from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import Pinecone 
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

# Loads PDF files available in a directory with pypdf
def load_docs(directory):
    try:
        loader = PyPDFDirectoryLoader(directory)
        documents = loader.load()
        return documents
    except FileNotFoundError:
        return None
    
# Split document Into Smaller Chunks
def split_docs(documents, chunk_size=800, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(documents)
    return docs
