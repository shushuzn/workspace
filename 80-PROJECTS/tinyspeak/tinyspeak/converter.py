"""
Audio Converter - Convert between audio formats
"""
import os
from pathlib import Path
from typing import Optional
from pydub import AudioSegment


class AudioConverter:
    """Convert between audio formats"""

    SUPPORTED_FORMATS = {
        "mp3": "mp3",
        "wav": "wav",
        "ogg": "ogg",
        "flac": "flac",
        "aac": "aac",
        "m4a": "m4a"
    }

    @staticmethod
    def convert(
        input_file: str,
        output_file: Optional[str] = None,
        format: Optional[str] = None,
        bitrate: str = "128k",
        sample_rate: Optional[int] = None
    ) -> str:
        """
        Convert audio file to different format
        
        Args:
            input_file: Input audio file path
            output_file: Output file path (auto-generated if None)
            format: Output format (mp3, wav, ogg, flac, aac, m4a)
            bitrate: Audio bitrate (e.g., "128k", "192k", "320k")
            sample_rate: Sample rate (e.g., 22050, 44100, 48000)
            
        Returns:
            Path to converted audio file
        """
        input_path = Path(input_file)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Auto-detect format from extension
        if not format:
            format = input_path.suffix.lstrip(".")

        # Auto-generate output filename
        if not output_file:
            output_file = str(input_path.with_suffix(f".{format}"))

        # Load audio
        audio = AudioSegment.from_file(str(input_path))

        # Apply sample rate if specified
        if sample_rate:
            audio = audio.set_frame_rate(sample_rate)

        # Export
        audio.export(
            output_file,
            format=format,
            bitrate=bitrate
        )

        return output_file

    @staticmethod
    def merge(audio_files: list, output_file: str) -> str:
        """
        Merge multiple audio files into one
        
        Args:
            audio_files: List of audio file paths
            output_file: Output file path
            
        Returns:
            Path to merged audio file
        """
        combined = AudioSegment.empty()

        for file in audio_files:
            audio = AudioSegment.from_file(file)
            combined += audio

        combined.export(output_file, format="mp3")
        return output_file

    @staticmethod
    def split(
        input_file: str,
        output_dir: str,
        chunk_duration_ms: int = 60000
    ) -> list:
        """
        Split audio file into chunks
        
        Args:
            input_file: Input audio file path
            output_dir: Output directory
            chunk_duration_ms: Chunk duration in milliseconds
            
        Returns:
            List of output file paths
        """
        audio = AudioSegment.from_file(input_file)

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)

        input_stem = Path(input_file).stem
        chunks = []

        for i in range(0, len(audio), chunk_duration_ms):
            chunk = audio[i:i + chunk_duration_ms]
            output_file = output_path / f"{input_stem}_part{i // chunk_duration_ms + 1}.mp3"
            chunk.export(str(output_file), format="mp3")
            chunks.append(str(output_file))

        return chunks

    @staticmethod
    def get_info(input_file: str) -> dict:
        """Get audio file information"""
        audio = AudioSegment.from_file(input_file)

        return {
            "duration_seconds": len(audio) / 1000,
            "duration_formatted": f"{len(audio) // 60000}:{(len(audio) % 60000) // 1000:02d}",
            "channels": audio.channels,
            "sample_rate": audio.frame_rate,
            "frame_count": audio.frame_count(),
            "sample_width": audio.sample_width,
            "rms": audio.rms,
            "dBFS": audio.dBFS
        }


# CLI integration
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: converter.py <input> <output> [format]")
        sys.exit(1)

    converter = AudioConverter()
    result = converter.convert(sys.argv[1], sys.argv[2])
    print(f"Converted: {result}")