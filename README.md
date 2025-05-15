# Chatbot-Reader-VQA


# LLM-Powered Chatbot Application

This project is a Streamlit application that leverages a large language model (LLM) powered by Ollama to create an interactive chatbot. The chatbot supports question-answering and summarization of various document types, including PDF, CSV, and arXiv documents. It also features memory functionality to retain context during conversations and displays the entire conversation history.

## Features

- **Question-Answering**: Users can ask questions related to the content of PDF, CSV, and arXiv documents.
- **Summarization**: The chatbot can summarize the contents of the uploaded documents.
- **Memory Functionality**: The chatbot retains context and previous interactions, enhancing the conversation experience.
- **Conversation History**: Displays the entire conversation between the user and the chatbot for reference.

## Project Structure

```
llm-chatbot-app
├── src
│   ├── app.py                # Main entry point for the Streamlit application
│   ├── chatbot
│   │   ├── __init__.py       # Initializes the chatbot package
│   │   ├── memory.py         # Implements memory functionality
│   │   ├── pdf_handler.py     # Handles PDF document processing
│   │   ├── csv_handler.py     # Handles CSV file processing
│   │   ├── arxiv_handler.py   # Manages arXiv document handling
│   │   └── chatbot.py         # Main chatbot class and logic
│   ├── utils
│   │   ├── __init__.py       # Initializes the utils package
│   │   └── helpers.py        # Utility functions for the application
│   └── types
│       └── index.py          # Defines custom types and interfaces
├── requirements.txt           # Lists project dependencies
└── README.md                  # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Samspei01/Chatbot-Reader-VQA.git
   cd llm-chatbot-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the Streamlit application, execute the following command:
```
streamlit run src/app.py
```

Open your web browser and navigate to `http://localhost:8501` to interact with the chatbot.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## Contact

For any questions or collaborations, feel free to reach out:

- **Abdelrhman Saeed** - [abdosaaed749@gmail.com](mailto:abdosaaed749@gmail.com)
- **Fouad Ouda**
- [foad.ouda546@gmail.com]
- (mailto:foad.ouda546gmail.com)

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
>>>>>>> 06a5349 (selected  topics)
