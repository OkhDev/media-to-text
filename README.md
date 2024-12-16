<div align="center">

# media-to-text 🎥 ➡️ 📝

**AI-Powered Media Transcription Using OpenAI's Whisper**

[![Version](https://img.shields.io/badge/Version-1.0.0-red?logo=github&logoColor=white)](https://github.com/OkhDev/media-to-text/releases)
[![OpenAI](https://img.shields.io/badge/OpenAI-Whisper-green?logo=openai&logoColor=white)](https://openai.com/research/whisper)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)](https://www.python.org)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-required-red?logo=ffmpeg&logoColor=white)](https://ffmpeg.org)

</div>

---

### 🎯 Overview

A command-line tool that uses AI to automatically:
- Convert any audio/video to text with high accuracy
- Split large files into 25MB chunks (OpenAI's limit)
- Show real-time progress with elegant terminal output
- Handle errors gracefully with automatic cleanup
- Combine multiple transcripts into a single file

### ⚡️ Quick Start

1. **Install FFmpeg**
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

2. **Get the Code**
```bash
git clone https://github.com/OkhDev/media-to-text.git
cd media-to-text
pip install -r requirements.txt
```

3. **Add Your API Key**
```bash
# The script will create .env for you
# Just add your OpenAI API key:
OPENAI_API_KEY=your_key_here
```

4. **Run It**
```bash
# Transcribe media files
python transcribe.py

# Combine transcripts (optional)
python combine_transcripts.py
```

### 📁 Supported Formats

<div align="left">

| Video Formats 🎥 | Audio Formats 🎵 |
|:---------------:|:---------------:|
| `.mp4` `.mkv` | `.mp3` `.wav` |
| `.webm` `.avi` | `.flac` `.aac` |
| `.mov` `.wmv` | `.m4a` `.ogg` |
| `.flv` `.m4v` | `.opus` `.wma` |
| `.3gp` | `.aiff` `.amr` |

</div>

### 📦 Requirements

- Python 3.8+
- FFmpeg
- OpenAI API key
- Required packages:
  ```
  openai>=1.3.5
  python-dotenv>=1.0.0
  moviepy>=1.0.3
  httpx>=0.24.1
  ```

### 💡 Pro Tips

**For Best Results:**
- Use clear audio with minimal background noise
- Ensure sufficient disk space for temporary files
- Monitor your OpenAI API usage/costs

**File Processing:**
- Larger files are automatically split into chunks
- Each chunk must be under 25MB (OpenAI limit)
- Processing time depends on file size

**Transcript Combination:**
- All transcripts are saved in the `transcripts/` directory
- Use `combine_transcripts.py` to merge multiple transcripts
- Combined file includes headers and separators for clarity
- Output includes timestamp for easy tracking

### 📂 Project Structure
```
media-to-text/
├── transcribe.py         # Main transcription script
├── combine_transcripts.py # Transcript combiner
├── requirements.txt      # Dependencies
├── .env                 # API key
├── media-files/         # Input files
├── transcripts/         # Individual transcripts
└── temp/               # Processing files
```

### 🤝 Contributing

Found a bug or want to contribute? Feel free to:
- Open an issue
- Submit a pull request
- Suggest improvements

### 📄 License

MIT License - Use it, modify it, share it.

---

<div align="center">

**Made with ❤️ by [OkhDev](https://github.com/OkhDev)**

</div>
