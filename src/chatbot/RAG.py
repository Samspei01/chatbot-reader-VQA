import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from cachetools import LRUCache
import asyncio
import time
import google.api_core.exceptions

MAX_TOKEN_LIMIT = 2048

class RAG:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=self.api_key)
        self.vector_store_path = "faiss_index"
        self.cache = LRUCache(maxsize=100)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        # Ensure the vector store directory exists
        if not os.path.exists(self.vector_store_path):
            os.makedirs(self.vector_store_path)

    def count_tokens(self, text):
        return len(text.split())

    def enforce_token_limit(self, text):
        if self.count_tokens(text) > MAX_TOKEN_LIMIT:
            raise ValueError(
                f"Input exceeds the maximum token limit of {MAX_TOKEN_LIMIT} tokens."
            )

    def get_pdf_text(self, pdf_docs):
        text = ""
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def get_text_chunks(self, text):
        splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=500)
        return splitter.split_text(text)

    def get_vector_store(self, chunks):
        batch_size = 16
        vector_store = None

        for i in range(0, len(chunks), batch_size):
            if vector_store is None:
                vector_store = self.create_faiss_index(chunks[i:i+batch_size])
            else:
                new_vector_store = self.create_faiss_index(chunks[i:i+batch_size])
                vector_store.merge_from(new_vector_store)
        vector_store.save_local(self.vector_store_path)

    def create_faiss_index(self, texts):
        retries = 3
        for attempt in range(retries):
            try:
                return FAISS.from_texts(texts, embedding=self.embeddings)
            except google.api_core.exceptions.ResourceExhausted as e:
                if attempt < retries - 1:
                    time.sleep(60)  # Wait for 60 seconds before retrying
                else:
                    raise e

    def get_conversational_chain(self):
        prompt_template = (
            "You are a helpful and informative chatbot that answers questions using text from the reference passage included below. "
            "Respond in a complete sentence and make sure that your response is easy to understand for everyone. "
            "Maintain a friendly and conversational tone. If the passage is irrelevant, feel free to ignore it.\n\n"
            "Context:\n {context}?\n"
            "Question: \n{question}\n"
            "ANSWER:"
        )

        model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.5)
        prompt = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
        return chain

    def cached_user_input(self, user_question):
        if user_question in self.cache:
            return self.cache[user_question]
        else:
            answer = self.user_input(user_question)
            self.cache[user_question] = answer
            return answer

    async def user_input(self, user_question):
        try:
            self.enforce_token_limit(user_question)
            # Check if the FAISS index exists, if not create it
            if not os.path.exists(os.path.join(self.vector_store_path, "index.faiss")):
                raise FileNotFoundError("FAISS index not found. Please upload documents to create the index.")
            new_db = FAISS.load_local(self.vector_store_path, self.embeddings, allow_dangerous_deserialization=True)
            docs = await asyncio.to_thread(new_db.similarity_search, user_question, k=3)
            chain = self.get_conversational_chain()
            response = await asyncio.to_thread(chain, {"input_documents": docs, "question": user_question}, return_only_outputs=True)

            return response["output_text"]

        except ValueError as ve:
            return f"Validation error: {ve}"
        except FileNotFoundError as fnfe:
            return str(fnfe)
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    async def main(self, pdf_docs, user_question):
        try:
            text = self.get_pdf_text(pdf_docs)
            chunks = self.get_text_chunks(text)
            self.get_vector_store(chunks)
            answer = await self.cached_user_input(user_question)
            return answer
        except ValueError as ve:
            return f"Error: {ve}"
        except Exception as e:
            return f"An unexpected error occurred during processing: {e}"

    async def model(self, pdf_docs, user_question):
        return await self.main([pdf_docs], user_question)

    def summarize(self, text):
        # Implement summarization logic using the LLM model
        # This is a placeholder implementation
        return "Summary of the text."