import os
import glob

def combine_transcript_files():
    # Get all txt files from the transcripts directory
    transcript_files = glob.glob('transcripts/*.txt')
    
    # Sort files to ensure consistent ordering
    transcript_files.sort()
    
    # Create or overwrite the combined file
    with open('combined_transcript.txt', 'w', encoding='utf-8') as outfile:
        # Iterate through each transcript file
        for i, transcript_file in enumerate(transcript_files):
            try:
                with open(transcript_file, 'r', encoding='utf-8') as infile:
                    # Write the content of the current file
                    outfile.write(infile.read())
                    
                    # Add two newlines between files (except for the last file)
                    if i < len(transcript_files) - 1:
                        outfile.write('\n\n')
                        
            except Exception as e:
                print(f"Error processing {transcript_file}: {str(e)}")
                
    print(f"Successfully combined {len(transcript_files)} transcript files into 'combined_transcript.txt'")

if __name__ == "__main__":
    combine_transcript_files() 