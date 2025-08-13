"""
speech_to_text.py
Service to convert audio files to text using OpenAI Whisper.
"""
import os
import warnings
import shutil
from typing import Optional

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

try:
    import torch
    import whisper
except ImportError:
    raise ImportError(
        "Please install openai-whisper and torch first: pip install openai-whisper torch"
    )

class SpeechToTextService:
    def __init__(self, model_name: str = "base"):
        try:
            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = whisper.load_model(model_name).to(device)
            print(f"Loaded Whisper model on {device}")
        except Exception as e:
            raise Exception(f"Error loading Whisper model: {str(e)}")

    def transcribe(self, audio_path: str) -> Optional[str]:
        print(f"[DEBUG] Checking if audio file exists: {audio_path}")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found at path: {audio_path}")
        print(f"[DEBUG] Audio file exists. Size: {os.path.getsize(audio_path)} bytes")
        try:
            # Double-check file is readable
            with open(audio_path, 'rb') as f:
                f.read(10)
            # Use context manager to suppress specific warnings during transcription
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                print(f"Starting transcription of file: {audio_path}")
                result = self.model.transcribe(audio_path)
                text = result.get("text", None)
                print(f"Transcription completed. Text length: {len(text) if text else 0}")
                return text
        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            raise Exception(f"Error transcribing audio: {str(e)}")
        finally:
            try:
                # Clean up the temporary file
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    print(f"Cleaned up temporary file: {audio_path}")
            except Exception as e:
                print(f"Warning: Could not clean up temporary file {audio_path}: {str(e)}")

# Example usage:
# stt = SpeechToTextService()
# text = stt.transcribe("path/to/audio.wav")
# print(text)
