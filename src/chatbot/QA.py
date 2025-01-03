from transformers import ViltProcessor, ViltForQuestionAnswering
from PIL import Image

class VisualQuestionAnswering:
    def __init__(self):
        self.processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
        self.model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa")

    def answer_question(self, image_path, question):
        # Open the image
        image = Image.open(image_path)

        # Process image and question
        encoding = self.processor(image, question, return_tensors="pt")

        # Get model predictions
        outputs = self.model(**encoding)
        logits = outputs.logits

        # Get the predicted answer's index
        predicted_id = logits.argmax(-1).item()

        # Map index to label (answer)
        answer = self.model.config.id2label[predicted_id]

        return answer
