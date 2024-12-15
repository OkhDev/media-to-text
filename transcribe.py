import os
import json
from pathlib import Path
from datetime import datetime
import openai
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, AudioFileClip
import tempfile
import math

# Constants
MAX_CHUNK_DURATION = 10 * 60  # 10 minutes in seconds

# Load environment variables
load_dotenv()
print("Environment variables loaded ✓")

# Configure OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print("OpenAI client configured ✓")

def setup_directories():
    """Create necessary directories if they don't exist."""
    Path('videos').mkdir(exist_ok=True)
    Path('transcripts').mkdir(exist_ok=True)
    Path('temp').mkdir(exist_ok=True)
    print("Directories ready ✓")

def get_video_files():
    """Get all MP4 files from the videos directory."""
    video_dir = Path('videos')
    files = list(video_dir.glob('*.mp4'))
    if files:
        print(f"\nFound {len(files)} video(s) to process ✓")
    return files

def extract_audio(video_path):
    """Extract audio from video and split into chunks."""
    print(f"Extracting audio...")
    
    # Load video and extract audio
    video = VideoFileClip(str(video_path))
    audio = video.audio
    
    # Get duration and calculate number of chunks
    duration = video.duration
    num_chunks = math.ceil(duration / MAX_CHUNK_DURATION)
    chunk_files = []
    
    # Create chunks
    for i in range(num_chunks):
        start_time = i * MAX_CHUNK_DURATION
        end_time = min((i + 1) * MAX_CHUNK_DURATION, duration)
        
        # Extract audio chunk
        audio_chunk = audio.subclip(start_time, end_time)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False, dir='temp')
        temp_path = temp_file.name
        temp_file.close()
        
        audio_chunk.write_audiofile(temp_path, verbose=False, logger=None)
        chunk_files.append((temp_path, start_time, end_time))
    
    # Clean up
    video.close()
    audio.close()
    
    return chunk_files

def transcribe_chunk(chunk_path):
    """Transcribe a single chunk of audio."""
    try:
        with open(chunk_path, 'rb') as audio_file:
            response = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                response_format="verbose_json"
            )
        
        # Get the full text from the response
        return response.text.strip()
        
    except Exception as e:
        print(f"\n❌ Error transcribing chunk: {str(e)}")
        return None

def create_transcript_file(video_name):
    """Create and return the transcript file path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path('transcripts') / f"{video_name}_{timestamp}.txt"

def append_to_transcript(file_path, text):
    """Append text to the transcript file."""
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(text + '\n\n')

def transcribe_video(video_path):
    """Transcribe the entire video file in chunks."""
    try:
        print(f"\nProcessing: {video_path.name}")
        
        # Create transcript file
        transcript_file = create_transcript_file(video_path.stem)
        print(f"Created transcript file: {transcript_file.name}")
        
        # Extract audio and split into chunks
        chunk_files = extract_audio(video_path)
        print(f"Split into {len(chunk_files)} chunks")
        
        # Process each chunk
        for i, (chunk_path, _, _) in enumerate(chunk_files, 1):
            print(f"\nTranscribing chunk {i} of {len(chunk_files)}...")
            
            # Transcribe chunk
            chunk_text = transcribe_chunk(chunk_path)
            if chunk_text:
                # Immediately append to transcript file
                append_to_transcript(transcript_file, chunk_text)
                print(f"✓ Chunk {i} transcribed and saved")
            
            # Clean up chunk file
            os.unlink(chunk_path)
        
        return transcript_file
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None
    finally:
        # Clean up any remaining temporary files
        for file in Path('temp').glob('*'):
            try:
                os.unlink(file)
            except:
                pass

def main():
    print("\n🎬 Video Transcription Script")
    print("="*30)
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found")
        return

    # Setup directories
    setup_directories()
    
    # Get video files
    video_files = get_video_files()
    
    if not video_files:
        print("\n❌ No MP4 files found in videos directory")
        return
    
    # Process each video
    for i, video_path in enumerate(video_files, 1):
        print(f"\nFile {i} of {len(video_files)}")
        print("="*30)
        
        output_file = transcribe_video(video_path)
        if output_file:
            print(f"\n✓ Transcription complete: {output_file.name}")
    
    print("\n✨ All files processed!")

if __name__ == "__main__":
    main() 