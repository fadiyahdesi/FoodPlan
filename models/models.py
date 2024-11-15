from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

def initialize_llm(groq_api_key=None):
    llm = ChatGroq(temperature=0, model_name="llama3-8b-8192", groq_api_key=groq_api_key)
    return llm

def initialize_embeddings():
    model_name = "BAAI/bge-small-en"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": True}
    embeddings = HuggingFaceBgeEmbeddings(
                model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
    )
    return embeddings

def apply_semantic_chunking(documents):
    text_splitter = SemanticChunker(GPT4AllEmbeddings())
    chunked_texts = text_splitter.split_documents(documents)
    return chunked_texts

def initialize_vectorstore(chunked_texts, embeddings):
    vectorstore = FAISS.from_documents(chunked_texts, embeddings)
    retriever = vectorstore.as_retriever()
    return retriever

def create_rag_chain(retriever, llm):
    system_prompt = (
        "Anda memiliki peran sebagai asisten untuk menjawab berbagai pertanyaan. "
        "Jawaban yang diberikan harus berdasarkan konteks yang tersedia. "
        "Pastikan untuk menggunakan bahasa Indonesia dalam setiap jawaban. "
        "Jika konteks tidak mencakup informasi yang diperlukan, Anda dapat mengatakan 'saya tidak tahu'. "
        "Selanjutnya, berikan jawaban yang relevan dan sesuai dengan pertanyaan. "
        "Jawaban yang diberikan harus singkat dan jelas. "
        "Usahakan untuk membatasi jawaban hingga tiga kalimat agar tetap ringkas.\n\n"
        "{context}"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    return rag_chain