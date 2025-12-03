# 🎬 YouTube Transcript Summarizer

A lightweight Streamlit web app that extracts transcripts from YouTube videos and generates structured summaries using OpenAI's GPT models.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **Transcript Extraction**: Fetches transcripts from YouTube videos using `youtube-transcript-api`
- **AI Summarization**: Generates structured summaries with executive summary, key points, and notable quotes
- **Smart Chunking**: Handles long videos (2+ hours) by intelligently chunking and merging summaries
- **Multiple Export Formats**: Download summaries as TXT, Markdown, or PDF
- **Clean UI**: Modern, responsive single-column layout

---

## 🚀 Deploy to Streamlit Cloud

### 1. Fork or Push to GitHub

Push this repository to your GitHub account.

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your repository, branch (`main`), and main file (`app.py`)
4. Click **"Deploy"**

### 3. Configure Secrets

After deployment, add your OpenAI API key:

1. Go to your app dashboard on Streamlit Cloud
2. Click **"Settings"** → **"Secrets"**
3. Add the following (TOML format):

```toml
OPENAI_API_KEY = "sk-your-api-key-here"
OPENAI_MODEL = "gpt-4o"
```

4. Click **"Save"**

Your app will automatically restart with the new secrets.

---

## 💻 Local Development

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd yt_sum

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Secrets

Create `.streamlit/secrets.toml` for local development:

```toml
OPENAI_API_KEY = "sk-your-api-key-here"
OPENAI_MODEL = "gpt-4o"
```

Or use a `.env` file (python-dotenv fallback):

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o
```

### 3. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📖 Usage

1. **Paste URL**: Enter a YouTube video URL in the input field
2. **Extract**: Click "Extract Transcript" to fetch the video's transcript
3. **Review**: Optionally expand and review the raw transcript
4. **Summarize**: Click "Generate Summary" to create a structured summary
5. **Download**: Select your preferred format (TXT, MD, PDF) and download

---

## 🏗️ Project Structure

```
yt_sum/
├── app.py                    # Main Streamlit application
├── modules/
│   ├── __init__.py
│   ├── transcript.py         # YouTube transcript extraction
│   ├── summarize.py          # LLM API wrapper + chunking
│   └── export.py             # TXT/MD/PDF file generation
├── .streamlit/
│   └── config.toml           # Streamlit theme & config
├── requirements.txt          # Python dependencies
├── secrets.toml.example      # Example secrets file
└── README.md
```

---

## 🔧 Configuration

| Secret | Required | Default | Description |
|--------|----------|---------|-------------|
| `OPENAI_API_KEY` | **Yes** | — | Your OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o` | Model for summarization |

---

## 📊 Summary Structure

Generated summaries follow this structure:

1. **Executive Summary**: 3-7 bullet points with key takeaways
2. **Key Points**: Main themes and arguments, logically grouped
3. **Notable Quotes & Facts**: Direct quotes and specific data points

---

## ⚠️ Limitations

- Videos without transcripts will show an error
- Very long transcripts (50k+ characters) may hit API rate limits
- Summary quality depends on the chosen LLM model
- YouTube API changes may affect transcript availability

---

## 📝 License

MIT License - feel free to use and modify for your own projects.

---

Built with ❤️ using [Streamlit](https://streamlit.io) and [OpenAI](https://openai.com)
