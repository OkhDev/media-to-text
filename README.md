# Transcriber Project

A Python-based utility for processing and managing transcript files. This project includes tools for transcribing audio files and combining multiple transcript files into a single document.

## Features

- **Transcript Generation**: Utilizes OpenAI's Whisper API to transcribe audio files into text format
- **Transcript Combination**: Combines multiple transcript files into a single consolidated document

## Project Structure

```
transcriber/
├── transcripts/         # Directory containing individual transcript files
├── combine_transcripts.py   # Script to combine multiple transcripts
├── transcribe.py           # Script for audio transcription
├── .env                   # Environment variables (not tracked in git)
└── .env-example          # Example environment file with placeholders
```

## Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd transcriber
```

2. Set up your environment variables:
```bash
cp .env-example .env
```
Then edit `.env` with your actual OpenAI API key.

## Usage

### Transcribing Audio Files
```bash
python transcribe.py [audio-file-path]
```
This will create a transcript file in the `transcripts` directory.

### Combining Transcript Files
To combine all transcript files in the `transcripts` directory into a single file:
```bash
python combine_transcripts.py
```
This will create a `combined_transcript.txt` file in the root directory, containing all transcripts with proper spacing between each file's content.

## Requirements

- Python 3.x
- OpenAI API key (for transcription)
- Required Python packages (specified in requirements.txt)

## Notes

- Transcript files are stored in the `transcripts` directory
- Combined output is saved as `combined_transcript.txt`
- The `.env` file containing your API key should never be committed to version control

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request