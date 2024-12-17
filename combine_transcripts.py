"""
Combine Transcripts - A utility script to merge multiple transcript files into one.

This script provides functionality to:
1. Discover transcript files in a specified directory
2. Merge multiple transcripts into a single file
3. Add clear separators and headers for readability
4. Handle errors gracefully with informative messages

Author: OkhDev
Version: 1.0.1
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
    """
    Generate a unique output filename using current timestamp.
    
    Returns:
        Path: Path object with format 'combined_transcript_YYYYMMDD_HHMMSS.txt'
        
    Note:
        Ensures unique filenames to prevent overwriting previous combinations
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(f"combined_transcript_{timestamp}.txt")

# ============================================================================
# Core Functionality
# ============================================================================

class TranscriptCombiner:
    """
    Handles the combination of multiple transcript files into a single document.
    
    This class manages:
    1. File discovery and validation
    2. Content merging with proper formatting
    3. Output file generation with timestamps
    4. Error handling and user feedback
    
    Attributes:
        input_dir (Path): Source directory containing transcript files
        output_file (Path): Destination file for combined transcripts
    """
    
    def __init__(self, input_dir: Path = TRANSCRIPTS_DIR, output_file: Optional[Path] = None):
        """
        Initialize the TranscriptCombiner with input and output paths.
        
        Args:
            input_dir (Path): Directory containing transcript files to combine
            output_file (Optional[Path]): Custom output file path. If None, generates timestamped name
            
        Note:
            - Default input directory is 'transcripts/'
            - Default output uses timestamp for unique naming
        """
        self.input_dir = input_dir
        self.output_file = output_file or get_output_filename()
    
    def get_transcript_files(self) -> List[Path]:
        """
        Discover and validate transcript files in the input directory.
        
        Returns:
            List[Path]: Sorted list of paths to valid transcript files
            
        Note:
            - Only processes .txt files
            - Returns files in sorted order for consistent output
            - Provides feedback about number of files found
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
        """
        Merge multiple transcript files into a single document.
        
        Args:
            transcript_files (List[Path]): List of transcript files to combine
            
        Returns:
            bool: True if combination was successful, False if any errors occurred
            
        Process:
        1. Creates output file with unique name
        2. Processes each input file sequentially
        3. Adds headers and separators for clarity
        4. Handles encoding and file operations safely
        5. Provides progress feedback for each file
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
    """
    Main entry point for the transcript combination utility.
    
    Workflow:
    1. Initialize TranscriptCombiner
    2. Discover available transcript files
    3. Combine files if any are found
    4. Handle interruptions and errors gracefully
    5. Provide clear feedback throughout process
    """
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