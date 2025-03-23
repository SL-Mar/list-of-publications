import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

# Optional PDF tools
try:
    import markdown
    import pdfkit
    pdf_enabled = True
except ImportError:
    pdf_enabled = False

# Load .env file for API key and initialize OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Fetch and join transcript text for a given YouTube video ID
def get_transcript(video_id, language="en"):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        print(f"❌ Error fetching transcript: {e}")
        return None

# Retrieve the video's publish date (used for article header context)
def get_publish_date(video_id):
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        return yt.publish_date.strftime("%Y-%m-%d") if yt.publish_date else "unknown_date"
    except Exception as e:
        print(f"⚠️ Could not fetch publish date: {e}")
        return "unknown_date"

# Generator to split transcript into manageable chunks for summarization
def split_text(text, max_words=1000):
    words = text.split()
    for i in range(0, len(words), max_words):
        yield " ".join(words[i:i + max_words])

# Send a single transcript chunk to the LLM for summarization
def summarize_chunk(chunk, model="gpt-4o-2024-11-20"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": f"Summarize the following part of a YouTube transcript:\n\n{chunk}"}
        ]
    )
    return response.choices[0].message.content

# Summarize the full transcript and generate a markdown article using a persona-based prompt
def summarize_transcript(transcript_text, video_id, publish_date="unknown_date"):
    summaries = [summarize_chunk(chunk) for chunk in split_text(transcript_text)]
    title = f"YouTube Video {video_id}"

    # 📘 PHYSICS PERSONA — use for science/academic content
    physics_combined_prompt = (
        f"You are a theoretical physicist and mathematician with expertise in science communication. "
        f"You are analyzing a talk titled \"{title}\" published on {publish_date} on YouTube.\n\n"
        "Based on the transcript summaries below, write a comprehensive and structured article in markdown format. "
        "This should be suitable for publishing on Medium and aimed at a highly educated audience. "
        "Structure your article with clear sections (e.g., ## Introduction, ## Key Insights, ## Technical Perspectives, ## Implications, ## Conclusion). "
        "Aim for an article around 1000 words. Include deep insights, analytical reasoning, and intellectual context where relevant.\n\n"
        "Transcript summaries:\n\n" + "\n\n".join(summaries)
    )

    # 💼 FINANCE PERSONA — use for financial, economic, or market content
    active_prompt = (
        f"You are a senior financial analyst and macro strategist with expertise in institutional investing, market trends, and global economics. "
        f"You are analyzing a talk titled \"{title}\" published on {publish_date} on YouTube.\n\n"
        "Based on the transcript summaries below, write a professional, insightful, and structured article in markdown format. "
        "Your audience includes mainly informed retail investors who follow Bloomberg, Financial Times, and Wall Street Journal content.\n\n"
        "The article should include key macro and microeconomic themes, sector and asset class insights, market sentiment, and any notable forecasts or strategic implications. "
        "Where appropriate, highlight risk factors, valuation considerations, or actionable perspectives.\n\n"
        "Structure your article with clear sections (e.g., ## Executive Summary, ## Market Outlook, ## Sector Insights, ## Strategy & Implications, ## Conclusion). "
        "Aim for an article around 1000 words. Provide well-reasoned analysis and connect ideas to broader economic or financial contexts.\n\n"
        "Transcript summaries:\n\n" + "\n\n".join(summaries)
    )

    # ✳️ Choose which prompt to use: swap active_prompt <-> physics_combined_prompt as needed
    final_response = client.chat.completions.create(
        model="gpt-4o-2024-11-20",
        messages=[{"role": "user", "content": active_prompt}],
        max_tokens=3000
    )

    # Add title and publish date as a markdown header
    markdown_header = f"# {title}\n\n*Published on {publish_date}*\n\n"
    return markdown_header + final_response.choices[0].message.content

# Locate wkhtmltopdf if available on Windows
def auto_find_wkhtmltopdf():
    possible_paths = [
        r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
        r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return pdfkit.configuration(wkhtmltopdf=path)
    raise FileNotFoundError("wkhtmltopdf not found in standard locations. Install it or pass the path manually.")

# Save the markdown article to a .md and (optionally) .pdf file
def export_to_markdown_and_pdf(summary_text, base_filename):
    md_path = f"{base_filename}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(summary_text)
    print(f"\n✅ Markdown saved to: {md_path}")

    if pdf_enabled:
        try:
            html_body = markdown.markdown(summary_text)
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body>
{html_body}
</body>
</html>"""
            pdf_path = f"{base_filename}.pdf"
            config = auto_find_wkhtmltopdf()
            pdfkit.from_string(html, pdf_path, configuration=config, options={"encoding": "UTF-8"})
            print(f"📄 PDF exported to: {pdf_path}")
        except Exception as e:
            print(f"⚠️ PDF export failed: {e}")
    else:
        print("⚠️ PDF export not available (missing markdown, pdfkit, or wkhtmltopdf).")

# Main CLI entry point
if __name__ == "__main__":
    video_id = input("🎥 Enter YouTube video ID: ").strip()
    language = input("🌐 Enter transcript language code (e.g. en or fr): ").strip()

    print(f"\n📅 Analyzing video ID: {video_id}")
    transcript_text = get_transcript(video_id, language)

    if transcript_text:
        publish_date = get_publish_date(video_id)
        print(f"📆 Publish date: {publish_date}")

        print("\n⏳ Summarizing transcript...\n")
        summary = summarize_transcript(transcript_text, video_id, publish_date)
        export_to_markdown_and_pdf(summary, base_filename=video_id)
    else:
        print("⚠️ Transcript could not be retrieved.")
