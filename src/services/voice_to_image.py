import tempfile
import os
import streamlit as st
from typing import Optional, Tuple, Dict, Any
import torch
import numpy as np
import soundfile as sf
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration

class VoiceToImageService:
    def __init__(self):
        """Initialize the Whisper model for speech-to-text conversion."""
        self.model = None
        self.processor = None
        self.model_loaded = False
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
    def load_model(self, model_size: str = "base") -> bool:
        """
        Load the Whisper model from Hugging Face.
        
        Args:
            model_size: Size of the model ('tiny', 'small', 'base', 'medium', 'large')
            
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            if not self.model_loaded or self.model is None:
                with st.spinner(f"Loading Whisper {model_size} model... This may take a few minutes on first run."):
                    model_name = f"openai/whisper-{model_size}"
                    self.processor = WhisperProcessor.from_pretrained(model_name)
                    self.model = WhisperForConditionalGeneration.from_pretrained(model_name)
                    self.model = self.model.to(self.device)
                    self.model_loaded = True
                st.success(f"Whisper {model_size} model loaded successfully!")
            return True
        except Exception as e:
            st.error(f"Error loading Whisper model: {str(e)}")
            return False
    
    def transcribe_audio(self, audio_file, language: Optional[str] = None) -> Tuple[str, dict]:
        """
        Transcribe audio file to text using Hugging Face's Whisper.
        
        Args:
            audio_file: Uploaded audio file from Streamlit
            language: Language code (e.g., 'en', 'es', 'fr'). If None, auto-detect.
            
        Returns:
            Tuple[str, dict]: (transcribed_text, transcription_info)
        """
        if not self.model_loaded:
            if not self.load_model():
                return "", {"error": "Failed to load Whisper model"}
            
        try:
            # Save the uploaded file to a temporary file
            with tempfile.NamedTemporaryFile(suffix=os.path.splitext(audio_file.name)[1], delete=False) as tmp_file:
                tmp_file.write(audio_file.getvalue())
                tmp_path = tmp_file.name
                
            try:
                # Read audio file
                audio_data, sample_rate = sf.read(tmp_path)
                
                # Convert to mono if stereo
                if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
                    audio_data = np.mean(audio_data, axis=1)
                
                # Resample to 16kHz if needed
                if sample_rate != 16000:
                    audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
                
                # Prepare inputs
                input_features = self.processor(
                    audio_data, 
                    sampling_rate=16000, 
                    return_tensors="pt"
                ).input_features.to(self.device)
                
                # Generate token ids
                generate_kwargs = {}
                if language:
                    generate_kwargs["language"] = language
                
                predicted_ids = self.model.generate(
                    input_features,
                    task="transcribe",
                    **generate_kwargs
                )
                
                # Decode token ids to text
                transcription = self.processor.batch_decode(
                    predicted_ids, 
                    skip_special_tokens=True
                )[0]
                
                return transcription, {
                    "language": language or "auto-detected",
                    "model": "openai/whisper",
                    "device": str(self.device)
                }
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
        except Exception as e:
            return "", {"error": f"Error during transcription: {str(e)}"}
        
        tmp_file_path = None
        try:
            with st.spinner("Transcribing audio..."):
                # Reset audio file pointer to beginning
                audio_file.seek(0)
                
                # Debug: Check audio file info
                st.info(f"Audio file name: {audio_file.name}")
                st.info(f"Audio file type: {audio_file.type}")
                
                # Save uploaded file to temporary location and preprocess with librosa
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    audio_data = audio_file.read()
                    st.info(f"Audio data size: {len(audio_data)} bytes")
                    tmp_file.write(audio_data)
                    tmp_file.flush()  # Ensure data is written to disk
                    original_tmp_path = tmp_file.name
                
                # Debug: Check temp file info
                st.info(f"Original temp file path: {original_tmp_path}")
                
                # Verify the temporary file exists and has content
                if not os.path.exists(original_tmp_path):
                    raise FileNotFoundError(f"Temporary file was not created: {original_tmp_path}")
                
                file_size = os.path.getsize(original_tmp_path)
                st.info(f"Original temp file size: {file_size} bytes")
                if file_size == 0:
                    raise ValueError("Temporary file is empty")
                
                # Preprocess audio with librosa to ensure compatibility
                try:
                    st.info("Preprocessing audio with librosa...")
                    # Load audio with librosa (this handles various formats and normalizes)
                    audio_array, sample_rate = librosa.load(original_tmp_path, sr=16000)  # Whisper expects 16kHz
                    
                    # Create a new temporary file for the preprocessed audio
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as processed_tmp_file:
                        tmp_file_path = processed_tmp_file.name
                    
                    # Save the preprocessed audio
                    sf.write(tmp_file_path, audio_array, sample_rate)
                    
                    st.info(f"Preprocessed temp file path: {tmp_file_path}")
                    st.info(f"Preprocessed temp file size: {os.path.getsize(tmp_file_path)} bytes")
                    st.info(f"Audio array shape: {audio_array.shape}, Sample rate: {sample_rate}")
                    
                except Exception as preprocess_error:
                    st.warning(f"Audio preprocessing failed: {str(preprocess_error)}")
                    # Fall back to original file
                    tmp_file_path = original_tmp_path
                    audio_array = None
                
                # Multi-method transcription fallback
                result = None
                try:
                    # Method 1: Try with preprocessed file
                    st.info("Attempting transcription with preprocessed file...")
                    if language:
                        result = self.model.transcribe(tmp_file_path, language=language, fp16=False)
                    else:
                        result = self.model.transcribe(tmp_file_path, fp16=False)
                    st.success("File-based transcription successful!")
                except Exception as file_error:
                    st.warning(f"File-based transcription failed: {str(file_error)}")
                    
                    # Method 2: Try with audio array (if available)
                    if audio_array is not None:
                        try:
                            st.info("Attempting transcription with audio array...")
                            if language:
                                result = self.model.transcribe(audio_array, language=language, fp16=False)
                            else:
                                result = self.model.transcribe(audio_array, fp16=False)
                            st.success("Array-based transcription successful!")
                        except Exception as array_error:
                            st.warning(f"Array-based transcription failed: {str(array_error)}")
                    
                    # Method 3: Try with CPU-only mode and verbose output
                    if result is None:
                        try:
                            st.info("Attempting transcription with CPU-only mode...")
                            # Force CPU usage
                            if torch.cuda.is_available():
                                device = "cpu"
                                self.model = self.model.to(device)
                            
                            if language:
                                result = self.model.transcribe(tmp_file_path, language=language, fp16=False, verbose=True)
                            else:
                                result = self.model.transcribe(tmp_file_path, fp16=False, verbose=True, word_timestamps=False)
                            st.success("Verbose mode transcription successful!")
                        except Exception as final_error:
                            st.error(f"All transcription methods failed. Final error: {str(final_error)}")
                            raise final_error
                
                transcribed_text = result["text"].strip()
                transcription_info = {
                    "language": result.get("language", "unknown"),
                    "confidence": result.get("avg_logprob", 0),
                    "duration": result.get("duration", 0)
                }
                
                return transcribed_text, transcription_info
                
        except Exception as e:
            st.error(f"Error transcribing audio: {str(e)}")
            return "", {}
        finally:
            # Clean up temporary files
            for temp_path in [locals().get('original_tmp_path'), locals().get('tmp_file_path')]:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass  # File might already be deleted
    
    def enhance_voice_prompt(self, transcribed_text: str) -> str:
        """
        Enhance the transcribed text to make it more suitable for image generation.
        
        Args:
            transcribed_text: Raw transcribed text from audio
            
        Returns:
            str: Enhanced prompt for image generation
        """
        if not transcribed_text:
            return ""
        
        # Basic enhancement rules
        enhanced_prompt = transcribed_text
        
        # Add common product photography keywords if not present
        photography_keywords = [
            "professional", "high quality", "studio lighting", "clean background",
            "product photography", "commercial", "advertising"
        ]
        
        # Check if any photography keywords are already present
        has_photography_keywords = any(keyword in enhanced_prompt.lower() for keyword in photography_keywords)
        
        if not has_photography_keywords:
            enhanced_prompt += ", professional product photography, studio lighting, clean background"
        
        # Ensure proper capitalization and punctuation
        enhanced_prompt = enhanced_prompt.capitalize()
        if not enhanced_prompt.endswith(('.', '!', '?')):
            enhanced_prompt += '.'
        
        return enhanced_prompt
    
    def validate_audio_file(self, audio_file) -> bool:
        """
        Validate uploaded audio file.
        
        Args:
            audio_file: Uploaded audio file from Streamlit
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        if audio_file is None:
            return False
        
        # Check file size (max 25MB for Whisper)
        audio_file.seek(0, 2)  # Seek to end
        file_size = audio_file.tell()
        audio_file.seek(0)  # Reset to beginning
        
        if file_size > 25 * 1024 * 1024:  # 25MB limit
            st.error("Audio file too large. Please upload a file smaller than 25MB.")
            return False
        
        # Check file extension
        allowed_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
        file_extension = os.path.splitext(audio_file.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            st.error(f"Unsupported audio format. Please upload: {', '.join(allowed_extensions)}")
            return False
        
        return True

def create_voice_to_image_service() -> VoiceToImageService:
    """Factory function to create VoiceToImageService instance."""
    return VoiceToImageService()
