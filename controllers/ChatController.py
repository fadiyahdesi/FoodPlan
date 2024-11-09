from flask import request, jsonify
from models.models import initialize_llm, initialize_embeddings, initialize_vectorstore, create_rag_chain
from langchain_community.document_loaders import PyPDFLoader
import os
import re
import math
from collections import Counter

class ChatController:
    def __init__(self, app, api_key="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", pdf_path="../data/chatbot.pdf"):
        self.app = app
        self.api_key = api_key
        self.pdf_path = pdf_path
        self.llm = None
        self.retriever = None

        # Initialize model and retriever once at startup
        self.initialize_rag_model()

    def initialize_rag_model(self):
        """Initialize the RAG model and vector store retriever."""
        try:
            self.llm = initialize_llm(self.api_key)
            embeddings = initialize_embeddings()

            # Load and process PDF documents
            pdf_loader = PyPDFLoader(self.pdf_path)
            documents = pdf_loader.load()
            
            # Initialize vector store retriever
            self.retriever = initialize_vectorstore(documents, embeddings)
            print("Model and retriever initialized successfully.")
        except Exception as e:
            print(f"Error initializing model: {e}")
            raise e

    def simple_tokenize(self, text):
        # Tokenization by splitting on whitespace and punctuation
        return re.findall(r'\w+', text.lower())

    def calculate_bleu(self, reference, candidate, max_n=4):
        ref_tokens = self.simple_tokenize(reference)
        cand_tokens = self.simple_tokenize(candidate)

        # Menyimpan n-grams untuk setiap n dari 1 hingga max_n
        precisions = []
        for n in range(1, max_n + 1):
            ref_ngrams = Counter([tuple(ref_tokens[i:i + n]) for i in range(len(ref_tokens) - n + 1)])
            cand_ngrams = Counter([tuple(cand_tokens[i:i + n]) for i in range(len(cand_tokens) - n + 1)])

            numerator = sum(min(cand_ngrams[gram], ref_ngrams[gram]) for gram in cand_ngrams)
            denominator = sum(cand_ngrams.values())
            
            precisions.append(numerator / denominator if denominator > 0 else 0)

        # Hitung rata-rata geometris dari presisi
        geometric_mean = math.exp(sum(math.log(p) for p in precisions if p > 0) / max_n)
        bp = 1 if len(cand_tokens) > len(ref_tokens) else math.exp(1 - len(ref_tokens) / len(cand_tokens))
        
        return bp * geometric_mean

    def get_response(self):
        """Handle the chatbot response generation."""
        print(f"Using API Key: {self.api_key}")
        print("Received request for response.")
        data = request.get_json()
        message = data.get("message")
        print(f"Message received: {message}")

        if not message:
            print("No message received.")
            return jsonify({"error": "No input received."}), 400

        if not self.llm or not self.retriever:
            print("Model or retriever not initialized.")
            return jsonify({"error": "Model or retriever is not initialized."}), 500

        try:
            # Create the RAG chain with the retriever and llm
            rag_chain = create_rag_chain(self.retriever, self.llm)
            response = rag_chain.invoke({"input": message})
            answer = response['answer']
            
            # Calculate BLEU score for response quality
            bleu_score = self.calculate_bleu(message, answer)
            
            print(f"BLEU Score calculated: {bleu_score}")

            return jsonify({
                "answer": answer,
                "bleu_score": bleu_score
            })
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": f"Error processing response: {e}"}), 500