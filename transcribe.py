"""
Media Transcription Tool - A command-line tool to convert audio and video files into text using OpenAI's Whisper API.

This script provides a robust solution for transcribing media files by:
1. Automatically handling both audio and video inputs
2. Splitting large files into processable chunks
3. Managing API interactions with OpenAI's Whisper
4. Providing real-time progress updates
5. Implementing error handling and cleanup

Author: OkhDev
Version: 1.0.1
"""

import os
import json
import math
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

import openai
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, AudioFileClip

# ============================================================================
# Constants and Configuration
# ============================================================================

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB in bytes
UPDATE_INTERVAL = 15  # seconds

SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.3gp'}
SUPPORTED_AUDIO_FORMATS = {'.mp3', '.wav', '.aac', '.ogg', '.wma', '.m4a', '.opus', '.flac', '.aiff', '.amr'}

class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class Symbols:
    """Unicode symbols for status messages."""
    CHECK = '✓'
    CROSS = '✗'
    INFO = 'ℹ'
    WARNING = '⚠'
    PROCESS = '⚙'
    TIME = '⏱'
    FILE = '⚄'
    FOLDER = '⚃'
    MEDIA = '▶'
    AUDIO = '♪'
    VIDEO = '◉'
    STAR = '★'
    SPARKLES = '✧'

# ============================================================================
# Utility Functions
# ============================================================================

def format_time(seconds: float) -> str:
    """Format time duration into a human-readable string."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    elif minutes > 0:
        return f"{minutes}m {secs:02d}s"
    else:
        return f"{secs}s"

def print_status(message: str, status: str = "info") -> None:
    """Print a formatted status message with appropriate color and symbol."""
    status_config = {
        "success": (Colors.GREEN, Symbols.CHECK),
        "error": (Colors.RED, Symbols.CROSS),
        "warning": (Colors.YELLOW, Symbols.WARNING),
        "info": (Colors.RESET, Symbols.INFO),
        "process": (Colors.BLUE, Symbols.PROCESS),
    }
    
    color, symbol = status_config.get(status, (Colors.RESET, Symbols.INFO))
    print(f"{color}{symbol} {message}{Colors.RESET}")

def print_header(title: str = "Media Transcription Tool") -> None:
    """Print a styled header for the application."""
    print(f"\n{Colors.BLUE}{Symbols.MEDIA}  {title}  {Symbols.AUDIO}{Colors.RESET}")
    print(f"{Colors.BLUE}{'─' * 40}{Colors.RESET}")

def print_divider() -> None:
    """Print a divider line for visual separation."""
    print(f"\n{Colors.BLUE}{'─' * 60}{Colors.RESET}\n")

# ============================================================================
# Progress Tracking
# ============================================================================

class ProgressTracker:
    """Handles progress tracking and status updates during processing."""
    
    def __init__(self):
        self.processing = False
        self.last_update = 0
        self.operation_start_time = 0
    
    def show_processing_status(self, message: str) -> None:
        """Show processing status at regular intervals."""
        self.processing = True
        self.last_update = time.time()
        self.operation_start_time = time.time()
        
        while self.processing:
            current_time = time.time()
            if current_time - self.last_update >= UPDATE_INTERVAL:
                elapsed_time = current_time - self.operation_start_time
                elapsed_str = format_time(elapsed_time)
                print(f"{Colors.YELLOW}{Symbols.PROCESS} Still {message.lower()} (Elapsed: {elapsed_str}){Colors.RESET}", end='\r')
                self.last_update = current_time
            time.sleep(1)
    
    def start(self, message: str) -> threading.Thread:
        """Start progress tracking in a separate thread."""
        thread = threading.Thread(target=self.show_processing_status, args=(message,))
        thread.daemon = True
        thread.start()
        return thread
    
    def stop(self) -> None:
        """Stop progress tracking."""
        self.processing = False
        time.sleep(0.1)

# ============================================================================
# Environment Setup
# ============================================================================

class EnvironmentSetup:
    """Handles environment configuration and directory setup."""
    
    @staticmethod
    def check_env_setup() -> bool:
        """Check and setup environment variables."""
        env_path = Path('.env')
        
        if not env_path.exists():
            print_status("No .env file found. Creating one for you...", "error")
            with open(env_path, 'w') as f:
                f.write("# OpenAI API Configuration\nOPENAI_API_KEY=your_api_key_here")
            print_status("Created .env file. Please add your OpenAI API key.", "error")
            return False
        
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key or api_key == "your_api_key_here":
            print_status("No valid API key found in .env file.", "error")
            print_status("Please ensure your .env file contains: OPENAI_API_KEY=your_actual_api_key", "error")
            return False
        
        print_status("Environment variables loaded successfully", "success")
        return True
    
    @staticmethod
    def setup_directories() -> None:
        """Create necessary directories for operation."""
        try:
            Path('media-files').mkdir(exist_ok=True)
            print_status("Created media-files directory", "success")
            
            Path('transcripts').mkdir(exist_ok=True)
            print_status("Created transcripts directory", "success")
            
            Path('temp').mkdir(exist_ok=True)
            print_status("Created temporary directory", "success")
            
        except Exception as e:
            print_status(f"Error creating directories: {str(e)}", "error")
            raise

# ============================================================================
# Media Processing
# ============================================================================

class MediaProcessor:
    """
    Handles media file processing and chunking.
    
    This class is responsible for:
    1. Discovering supported media files
    2. Extracting audio from video files
    3. Splitting large files into API-compatible chunks
    4. Managing temporary file operations
    """
    
    def __init__(self):
        self.progress = ProgressTracker()
    
    def get_media_files(self) -> List[Path]:
        """
        Discover and validate media files in the media-files directory.
        
        Returns:
            List[Path]: A list of paths to supported media files.
            
        Note:
            - Checks file extensions against SUPPORTED_VIDEO_FORMATS and SUPPORTED_AUDIO_FORMATS
            - Logs unsupported files for user awareness
        """
        media_dir = Path('media-files')
        supported_files = []
        unsupported_files = []
        
        for file_path in media_dir.iterdir():
            if file_path.is_file():
                extension = file_path.suffix.lower()
                if extension in SUPPORTED_VIDEO_FORMATS or extension in SUPPORTED_AUDIO_FORMATS:
                    supported_files.append(file_path)
                else:
                    unsupported_files.append(file_path)
        
        if supported_files:
            print_status(f"Found {len(supported_files)} supported media file(s)", "success")
        
        if unsupported_files:
            print_status(f"Skipping {len(unsupported_files)} unsupported file(s):", "warning")
            for file in unsupported_files:
                print(f"{Colors.YELLOW}   {Symbols.WARNING} Skipping: {file.name}{Colors.RESET}")
        
        return supported_files
    
    def extract_audio(self, media_path: Path) -> List[tuple]:
        """
        Extract and chunk audio from a media file.
        
        Args:
            media_path (Path): Path to the source media file
            
        Returns:
            List[tuple]: List of (chunk_path, start_time, end_time) for each audio segment
            
        Note:
            - Automatically detects video vs audio input
            - Splits files larger than MAX_FILE_SIZE
            - Creates temporary files in the temp directory
            - Handles cleanup of intermediate files
        """
        try:
            is_video = media_path.suffix.lower() in SUPPORTED_VIDEO_FORMATS
            file_type = "video" if is_video else "audio"
            
            print_status(f"Loading {file_type} file...", "process")
            progress_thread = self.progress.start(f"Loading {file_type} file")
            
            clip = VideoFileClip(str(media_path)) if is_video else AudioFileClip(str(media_path))
            self.progress.stop()
            
            audio = clip.audio if hasattr(clip, 'audio') else clip
            duration = clip.duration
            
            print_status(f"Media duration: {format_time(duration)}", "info")
            
            # Analyze file size
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False, dir='temp') as temp_file:
                temp_path = temp_file.name
            
            progress_thread = self.progress.start("Analyzing file size")
            audio.write_audiofile(temp_path, verbose=False, logger=None)
            self.progress.stop()
            
            total_size = os.path.getsize(temp_path)
            os.unlink(temp_path)
            
            num_chunks = math.ceil(total_size / MAX_FILE_SIZE)
            chunk_duration = duration / num_chunks
            
            print_status(f"File size: {total_size / (1024*1024):.1f}MB, Splitting into {num_chunks} chunks", "info")
            
            chunk_files = []
            
            for i in range(num_chunks):
                start_time = i * chunk_duration
                end_time = min((i + 1) * chunk_duration, duration)
                
                print_status(f"Extracting chunk {i+1}/{num_chunks}", "process")
                progress_thread = self.progress.start(f"Processing chunk {i+1}/{num_chunks}")
                
                audio_chunk = audio.subclip(start_time, end_time)
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False, dir='temp') as temp_file:
                    temp_path = temp_file.name
                
                audio_chunk.write_audiofile(temp_path, verbose=False, logger=None)
                self.progress.stop()
                
                chunk_size = os.path.getsize(temp_path)
                if chunk_size > MAX_FILE_SIZE:
                    print_status(f"Warning: Chunk {i+1} exceeds 25MB limit. File will be skipped.", "warning")
                    for chunk_path, _, _ in chunk_files:
                        try:
                            os.unlink(chunk_path)
                        except:
                            pass
                    return []
                
                chunk_files.append((temp_path, start_time, end_time))
                print_status(f"Chunk {i+1} ready ({chunk_size / (1024*1024):.1f}MB)", "success")
            
            return chunk_files
            
        except Exception as e:
            self.progress.stop()
            print_status(f"Audio extraction failed: {str(e)}", "error")
            return []
            
        finally:
            if 'clip' in locals():
                clip.close()
                if hasattr(clip, 'audio') and clip.audio is not None:
                    clip.audio.close()

# ============================================================================
# Transcription
# ============================================================================

class Transcriber:
    """
    Handles the transcription process using OpenAI's Whisper API.
    
    This class manages:
    1. API communication with OpenAI
    2. Chunk-by-chunk transcription
    3. Result aggregation and file output
    4. Progress tracking and error handling
    """
    
    def __init__(self):
        self.progress = ProgressTracker()
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def transcribe_chunk(self, chunk_path: str) -> Optional[str]:
        """
        Transcribe a single audio chunk using Whisper API.
        
        Args:
            chunk_path (str): Path to the audio chunk file
            
        Returns:
            Optional[str]: Transcribed text if successful, None if failed
            
        Note:
            - Uses OpenAI's Whisper-1 model
            - Implements progress tracking
            - Handles API errors gracefully
        """
        try:
            progress_thread = self.progress.start("Transcribing audio chunk")
            with open(chunk_path, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    response_format="verbose_json"
                )
            self.progress.stop()
            return response.text.strip()
            
        except Exception as e:
            self.progress.stop()
            print_status(f"Error transcribing chunk: {str(e)}", "error")
            return None

    def create_transcript_file(self, video_name: str) -> Path:
        """Create and return the transcript file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return Path('transcripts') / f"{video_name}_{timestamp}.txt"

    def append_to_transcript(self, file_path: Path, text: str) -> None:
        """Append text to the transcript file."""
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(text + '\n\n')

# ============================================================================
# Main Application
# ============================================================================

class TranscriptionApp:
    """
    Main application orchestrator for the transcription process.
    
    Responsibilities:
    1. Coordinating the overall transcription workflow
    2. Managing environment setup and validation
    3. Handling file processing and cleanup
    4. Providing user feedback and progress updates
    5. Error handling and recovery
    """
    
    def __init__(self):
        self.env_setup = EnvironmentSetup()
        self.media_processor = MediaProcessor()
        self.transcriber = Transcriber()
    
    def process_media_file(self, media_path: Path) -> Optional[Path]:
        """
        Process a single media file through the complete transcription pipeline.
        
        Args:
            media_path (Path): Path to the media file to process
            
        Returns:
            Optional[Path]: Path to the transcript file if successful, None if failed
            
        Workflow:
        1. Extract audio from media
        2. Split into chunks if needed
        3. Transcribe each chunk
        4. Combine results
        5. Clean up temporary files
        """
        try:
            print_header(f"Processing: {media_path.name}")
            transcript_file = self.transcriber.create_transcript_file(media_path.stem)
            
            chunk_files = self.media_processor.extract_audio(media_path)
            if not chunk_files:
                return None
            
            for i, (chunk_path, start_time, end_time) in enumerate(chunk_files, 1):
                formatted_start = format_time(start_time)
                formatted_end = format_time(end_time)
                print(f"\n{Colors.BLUE}Chunk {i}/{len(chunk_files)} ({formatted_start} → {formatted_end}){Colors.RESET}")
                
                text = self.transcriber.transcribe_chunk(chunk_path)
                if text:
                    self.transcriber.append_to_transcript(transcript_file, text)
                    print_status(f"Chunk {i}/{len(chunk_files)} completed", "success")
                else:
                    print_status(f"Failed to transcribe chunk {i}/{len(chunk_files)}", "error")
                
                os.unlink(chunk_path)
            
            return transcript_file
            
        except Exception as e:
            print_status(f"Error processing {media_path.name}: {str(e)}", "error")
            return None
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        try:
            for file in Path('temp').glob('*'):
                try:
                    os.unlink(file)
                except:
                    pass
            print_status("Cleared temp directory", "success")
        except Exception as e:
            print_status(f"Error cleaning up: {str(e)}", "warning")
    
    def run(self) -> None:
        """Run the transcription application."""
        print_header()
        
        if not self.env_setup.check_env_setup():
            return
        
        try:
            self.env_setup.setup_directories()
            media_files = self.media_processor.get_media_files()
            
            if not media_files:
                print_status("No supported media files found", "warning")
                print_status("Add media files to the 'media-files' folder", "info")
                return
            
            total_files = len(media_files)
            print(f"\n{Colors.BLUE}Starting Transcription - {total_files} file(s){Colors.RESET}")
            
            successful = 0
            failed_files = []
            
            for i, media_path in enumerate(media_files, 1):
                if i > 1:
                    print_divider()
                
                try:
                    if self.process_media_file(media_path):
                        successful += 1
                    else:
                        failed_files.append(media_path)
                except Exception as e:
                    print_status(f"Error processing {media_path.name}: {str(e)}", "error")
                    failed_files.append(media_path)
            
            print_divider()
            print_status(
                f"Processing complete! Successfully transcribed {successful}/{total_files} files",
                "success" if successful == total_files else "warning"
            )
            
            if failed_files:
                print_status("The following files could not be processed:", "error")
                for file in failed_files:
                    print_status(f"• {file.name}", "error")
                    
        except KeyboardInterrupt:
            print_status("\nTranscription interrupted by user", "warning")
        except Exception as e:
            print_status(f"An unexpected error occurred: {str(e)}", "error")
        finally:
            self.cleanup()

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    app = TranscriptionApp()
    app.run() 