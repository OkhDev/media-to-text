"""
Combine Transcripts - A utility script to merge multiple transcript files into one.
Author: OkhDev
Version: 1.0.0
"""

import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# ============================================================================
# Constants and Configuration
# ============================================================================

TRANSCRIPTS_DIR = Path("transcripts")
DEFAULT_OUTPUT = Path("combined_transcript.txt")

class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

class Symbols:
    """Unicode symbols for status messages."""
    CHECK = '✓'
    CROSS = '✗'
    WARNING = '⚠'
    INFO = 'ℹ'

# ============================================================================
# Utility Functions
# ============================================================================

def print_status(message: str, status: str = "info") -> None:
    """Print a formatted status message with appropriate color and symbol."""
    status_config = {
        "success": (Colors.GREEN, Symbols.CHECK),
        "error": (Colors.RED, Symbols.CROSS),
        "warning": (Colors.YELLOW, Symbols.WARNING),
        "info": (Colors.RESET, Symbols.INFO),
    }
    
    color, symbol = status_config.get(status, (Colors.RESET, Symbols.INFO))
    print(f"{color}{symbol} {message}{Colors.RESET}")

def get_output_filename() -> Path:
    """Generate output filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(f"combined_transcript_{timestamp}.txt")

# ============================================================================
# Core Functionality
# ============================================================================

class TranscriptCombiner:
    """Handles the combination of multiple transcript files."""
    
    def __init__(self, input_dir: Path = TRANSCRIPTS_DIR, output_file: Optional[Path] = None):
        """Initialize the TranscriptCombiner.
        
        Args:
            input_dir: Directory containing transcript files
            output_file: Optional custom output file path
        """
        self.input_dir = input_dir
        self.output_file = output_file or get_output_filename()
    
    def get_transcript_files(self) -> List[Path]:
        """Get all transcript files from the input directory.
        
        Returns:
            List of paths to transcript files
        """
        if not self.input_dir.exists():
            print_status(f"Directory '{self.input_dir}' not found", "error")
            return []
        
        transcript_files = sorted(self.input_dir.glob("*.txt"))
        
        if not transcript_files:
            print_status("No transcript files found", "warning")
        else:
            print_status(f"Found {len(transcript_files)} transcript file(s)", "success")
        
        return transcript_files
    
    def combine_files(self, transcript_files: List[Path]) -> bool:
        """Combine multiple transcript files into one.
        
        Args:
            transcript_files: List of transcript files to combine
            
        Returns:
            bool: True if combination was successful, False otherwise
        """
        if not transcript_files:
            return False
        
        try:
            print_status("Starting file combination...", "info")
            
            with open(self.output_file, 'w', encoding='utf-8') as outfile:
                for i, transcript_file in enumerate(transcript_files):
                    try:
                        # Add file header
                        outfile.write(f"# Transcript from: {transcript_file.name}\n")
                        outfile.write("=" * 80 + "\n\n")
                        
                        # Write file content
                        with open(transcript_file, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read().strip())
                        
                        # Add separator between files
                        if i < len(transcript_files) - 1:
                            outfile.write("\n\n" + "=" * 80 + "\n\n")
                        
                        print_status(f"Processed: {transcript_file.name}", "success")
                        
                    except Exception as e:
                        print_status(f"Error processing {transcript_file.name}: {str(e)}", "error")
                        return False
            
            print_status(
                f"Successfully combined {len(transcript_files)} files into '{self.output_file}'",
                "success"
            )
            return True
            
        except Exception as e:
            print_status(f"Error creating output file: {str(e)}", "error")
            return False

# ============================================================================
# Main Entry Point
# ============================================================================

def main() -> None:
    """Main function to run the transcript combiner."""
    try:
        # Initialize combiner with default or custom paths
        combiner = TranscriptCombiner()
        
        # Get transcript files
        transcript_files = combiner.get_transcript_files()
        
        # Combine files
        if transcript_files:
            combiner.combine_files(transcript_files)
        else:
            print_status("Please add transcript files to the 'transcripts' directory", "info")
            
    except KeyboardInterrupt:
        print_status("\nOperation interrupted by user", "warning")
    except Exception as e:
        print_status(f"An unexpected error occurred: {str(e)}", "error")

if __name__ == "__main__":
    main() 