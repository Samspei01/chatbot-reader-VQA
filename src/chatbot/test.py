from QA import VisualQuestionAnswering
from PIL import Image

def main():

    vqa = VisualQuestionAnswering()


    image_path = "/home/samsepi0l/TErm 7/Selected proj/llm-chatbot-app/src/chatbot/cats.jpg"  # Replace with the actual path to your image


    question = "What is in the image?"  

    # Get the answer
    answer = vqa.answer_question(image_path, question)

    # Print the answer
    print(f"Question: {question}")
    print(f"Answer: {answer}")

if __name__ == "__main__":
    main()