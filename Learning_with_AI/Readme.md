Virtual Italian Teacher 🎓🇮🇹

Table of Contents

    Description
    Features
    Demo
    Installation
    Configuration
    Usage
    Contributing
    License
    Contact
    Acknowledgments

Description

Virtual Italian Teacher is an interactive chatbot designed to help users learn Italian through conversational practice. Leveraging OpenAI's language models, speech recognition, and text-to-speech technologies, this application provides a seamless and engaging learning experience. Users can converse in Italian, receive corrections, and save their conversation history for later review.
Features

    Conversational Practice: Engage in real-time conversations with an AI-powered Italian teacher.
    Speech Recognition: Speak directly to the chatbot using your microphone, with voice-to-text transcription.
    Text-to-Speech: Listen to the chatbot's responses in Italian through synthesized speech.
    Conversation History: Save your interactions as a DOCX file for future reference.
    Customizable AI Behavior: Define the teacher's role and behavior through customizable prompts.
    Robust Error Handling: Gracefully handles transcription and audio playback errors.
    Logging: Detailed logging for monitoring and debugging purposes.

Demo

Illustration of the Virtual Italian Teacher in action.
Installation

Follow these steps to set up the Virtual Italian Teacher on your local machine.
Prerequisites

    Python 3.7 or higher: Ensure Python is installed. Download Python
    Git: For cloning the repository. Download Git
    Microphone: For speech input.

Steps

    Clone the Repository:

    bash

git clone https://github.com/SL-Mar/virtual-italian-teacher.git

Navigate to the Project Directory:

bash

cd virtual-italian-teacher

Create and Activate a Virtual Environment (Optional but Recommended):

bash

python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

Install Dependencies:

bash

    pip install -r requirements.txt

Configuration

    Set Up Environment Variables:

    Create a .env file in the root directory of the project and add your OpenAI API key:

    env

    OPENAI_API_KEY=your_openai_api_key_here

    Replace your_openai_api_key_here with your actual OpenAI API key. You can obtain an API key by signing up at OpenAI.

Usage

Run the application to start interacting with the Virtual Italian Teacher.

bash

python app.py

How to Use

    Start the Application:

    Upon running the script, the application will initialize and prompt you to start speaking.

    Interact via Microphone:
        Speak in Italian: Use your microphone to converse with the teacher.
        Commands:
            END: Terminates the conversation.
            SAVE: Saves the current conversation history to a DOCX file.

    Conversation Flow:
        User Input: Speak into the microphone. The speech will be transcribed to text.
        AI Response: The chatbot responds in Italian, both in text and synthesized speech.
        Save Conversation: Use the SAVE command to export the dialogue.

    Exit:
        Use the END command to gracefully exit the application.

Contributing

Contributions are welcome! Please follow these steps to contribute to the project:

    Fork the Repository

    Create a New Branch:

    bash

git checkout -b feature/YourFeature

Commit Your Changes:

bash

git commit -m "Add some feature"

Push to the Branch:

bash

    git push origin feature/YourFeature

    Open a Pull Request

Please ensure your contributions adhere to the project's Code of Conduct.
License

This project is licensed under the MIT License.
Contact

For any inquiries or support, please reach out:

    GitHub: SL-MAR

Acknowledgments

    OpenAI for providing the language models.
    LangChain for the conversational AI framework.
    gTTS for text-to-speech conversion.
    SpeechRecognition for speech-to-text functionality.
    Pygame for audio playback.
    Python Dotenv for environment variable management.
    Docx for generating DOCX files.
