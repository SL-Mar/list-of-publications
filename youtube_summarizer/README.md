# YouTube Transcript Summarizer

A Python script to extract structured summaries from YouTube videos using OpenAI's GPT-4 API. The tool is designed for financial, academic, or technical video content. It retrieves the transcript, summarizes it in segments, and formats the result as a Markdown and optional PDF article.

---

## 📦 Features

- Transcript retrieval via `youtube-transcript-api`
- Summarization using OpenAI GPT-4 (`gpt-4o`)
- Two personas: financial analyst or theoretical physicist
- Markdown and PDF export

---

## 💠 Setup

### 1. Clone the repository

```bash
git clone https://github.com/SL-Mar/Coding_and_Writing_Works.git
cd youtube-summarizer
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=your_openai_key_here
```

### 5. Enable PDF export

Install [`wkhtmltopdf`](https://wkhtmltopdf.org/):
  ```
- On Windows:
  Install to one of the following paths:
  ```
  C:\Program Files\wkhtmltopdf\bin\
  C:\Program Files (x86)\wkhtmltopdf\bin\
  ```

---

## ▶️ Usage

Run the script and follow the prompts:

```bash
python youtube_summarizer.py
```

**Example input:**
```
🎥 Enter YouTube video ID: 69YOJFvL1-M
🌐 Enter transcript language code (e.g. en or fr): en
```

**Output:**
- `69YOJFvL1-M.md` — Markdown summary
- `69YOJFvL1-M.pdf` — PDF summary (if enabled)

---

## 🧠 Prompt Personas

This project uses predefined GPT prompts. You can toggle between them in the code:

### Financial Analyst Persona (default)

For macro, investment, and market-related content.

### Physics/Science Persona

For technical or theoretical talks.

---

## 📄 Example

Video: [Bloomberg Invest 2025 — Bruce Flatt (Brookfield CEO)](https://www.youtube.com/watch?v=69YOJFvL1-M)

Sample output (excerpt):

```markdown
## Executive Summary

Brookfield CEO Bruce Flatt outlines strategic investment priorities across global infrastructure, focusing on energy transition, urbanization, and inflation-linked assets.

## Strategy & Implications

Brookfield continues to deploy capital across secular growth sectors, with an emphasis on long-term value amid interest rate volatility and capital repricing cycles.
```

---

## 🔍 License

This project is open source and intended for research and educational use. No data is stored or shared beyond your local machine.

---

## 📬 Contact

For suggestions or collaboration, feel free to open an issue or submit a pull request.

