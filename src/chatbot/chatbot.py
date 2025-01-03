from .RAG import RAG
from .QA import VisualQuestionAnswering
import asyncio

class Chatbot:
    def __init__(self, memory, pdf_handler, csv_handler, arxiv_handler):
        self.memory = memory
        self.pdf_handler = pdf_handler
        self.csv_handler = csv_handler
        self.arxiv_handler = arxiv_handler
        self.conversation_history = []
        self.rag = RAG()  # Initialize the RAG class
        self.vqa = VisualQuestionAnswering()  # Initialize the VQA class

    def process_input(self, user_input):
        self.conversation_history.append({"user": user_input})
        response = self.generate_response(user_input)
        self.conversation_history.append({"bot": response})
        return response

    def generate_response(self, user_input):
        # Logic to determine if the input is a question, a request for summarization, or a VQA task
        if self.is_question(user_input):
            return self.answer_question(user_input)
        elif self.is_summarization_request(user_input):
            return self.summarize_content(user_input)
        elif self.is_vqa_request(user_input):
            return self.answer_vqa(user_input)
        else:
            return "I'm sorry, I didn't understand that."

    def is_question(self, user_input):
        # Implement logic to identify questions
        return user_input.endswith('?')

    def is_summarization_request(self, user_input):
        # Implement logic to identify summarization requests
        return "summarize" in user_input.lower()

    def is_vqa_request(self, user_input):
        # Implement logic to identify VQA requests
        return "vqa" in user_input.lower()

    def answer_question(self, question):
        # Use RAG to answer questions
        response = asyncio.run(self.rag.user_input(question))
        return response

    def summarize_content(self, request):
        # Implement logic to summarize content based on the request
        return "Summary of the content."

    def answer_vqa(self, request):
        # Extract image path and question from the request
        parts = request.split('|')
        if len(parts) != 3:
            return "Invalid VQA request format. Use 'vqa|<image_path>|<question>'."
        _, image_path, question = parts[0].strip(), parts[1].strip(), parts[2].strip()
        answer = self.vqa.answer_question(image_path, question)
        return answer

    def get_conversation_history(self):
        return self.conversation_history

    def get_response(self, user_input):
        return self.process_input(user_input)

    def process_document(self, uploaded_file):
        if uploaded_file.type == "application/pdf":
            text = self.pdf_handler["extract_text_from_pdf"](uploaded_file)
            chunks = self.rag.get_text_chunks(text)
            self.rag.get_vector_store(chunks)  # Create the FAISS index
            summary = self.pdf_handler["summarize_pdf"](text, self.rag)  # Pass the RAG model
            return summary
        elif uploaded_file.type == "text/csv":
            data = self.csv_handler["read_csv"](uploaded_file)
            chunks = self.rag.get_text_chunks(data.to_string())
            self.rag.get_vector_store(chunks)  # Create the FAISS index
            summary = self.csv_handler["summarize_csv"](data)
            return summary
        else:
            return "Unsupported file format."