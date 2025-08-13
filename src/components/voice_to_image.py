import os
import sys
import streamlit as st

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.voice_to_image import create_voice_to_image_service
from src.services.hd_image_generation import generate_hd_image
from src.services.prompt_enhancement import enhance_prompt
import time

def render_voice_to_image_section():
    """Render the voice-to-image section in the main app."""
    
    st.header("🎤 Voice to Image Generator")
    st.markdown("Upload an audio file describing your product, and we'll generate an image from your voice!")
    
    # Initialize voice service and ensure session state persistence
    if 'voice_service' not in st.session_state:
        st.session_state.voice_service = create_voice_to_image_service()
    
    # Ensure transcription session state variables are initialized and persistent
    if 'voice_original_prompt' not in st.session_state:
        st.session_state.voice_original_prompt = ""
    if 'voice_enhanced_prompt' not in st.session_state:
        st.session_state.voice_enhanced_prompt = ""
    if 'voice_transcription_info' not in st.session_state:
        st.session_state.voice_transcription_info = {}
    if 'voice_audio_uploaded' not in st.session_state:
        st.session_state.voice_audio_uploaded = False
    

    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📁 Upload Audio")
        
        # File uploader for audio
        uploaded_audio = st.file_uploader(
            "Choose an audio file",
            type=['wav', 'mp3', 'm4a', 'flac', 'ogg'],
            help="Upload an audio file (max 25MB) describing your product"
        )
        
        # Model size selection
        model_size = st.selectbox(
            "Whisper Model Size",
            options=["tiny", "base", "small", "medium", "large"],
            index=1,  # Default to "base"
            help="Larger models are more accurate but require more memory"
        )
        
        # Language selection (optional)
        language = st.selectbox(
            "Language (Optional - Auto-detect if not selected)",
            options=["Auto-detect", "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
            index=0,
            help="Select the language spoken in the audio for better accuracy"
        )
        
        # Convert language selection to None if auto-detect is selected
        selected_language = None if language == "Auto-detect" else language
        

        
        # Transcribe button
        if uploaded_audio and st.button("🎤 Transcribe Audio", type="primary"):
            if st.session_state.voice_service.validate_audio_file(uploaded_audio):
                # Load model if needed
                if st.session_state.voice_service.load_model(model_size):
                    # Transcribe audio
                    transcribed_text, transcription_info = st.session_state.voice_service.transcribe_audio(
                        uploaded_audio, selected_language
                    )
                    
                    if transcribed_text:
                        # Store in voice-specific session state variables
                        st.session_state.voice_original_prompt = transcribed_text
                        st.session_state.voice_enhanced_prompt = st.session_state.voice_service.enhance_voice_prompt(transcribed_text)
                        st.session_state.voice_transcription_info = transcription_info
                        st.session_state.voice_audio_uploaded = True
                        
                        # Also store in global session state for compatibility
                        st.session_state.original_prompt = transcribed_text
                        st.session_state.enhanced_prompt = st.session_state.voice_enhanced_prompt
                        
                        # Display transcription info
                        st.success("✅ Audio transcribed successfully!")
                        st.info(f"**Language detected:** {transcription_info.get('language', 'auto-detected')}")
                        st.info(f"**Model:** {transcription_info.get('model', 'Whisper')}")
                        st.info(f"**Device:** {transcription_info.get('device', 'CPU')}")
                        
                        st.rerun()
                    else:
                        st.error("❌ Failed to transcribe audio. Please try again.")
                else:
                    st.error("❌ Failed to load Whisper model. Please try again.")
            else:
                st.error("❌ Invalid audio file. Please check the file format and size.")
    
    with col2:
        # Check if we have transcription data
        has_transcription = (
            st.session_state.voice_original_prompt or 
            st.session_state.get('original_prompt', '')
        )
        
        if has_transcription:
            st.subheader("📝 Transcription Results")
            
            # Display original transcription
            current_original = st.session_state.voice_original_prompt or st.session_state.get('original_prompt', '')
            if current_original:
                st.markdown("**Original Transcription:**")
                st.text_area(
                    "Original text from audio",
                    value=current_original,
                    height=100,
                    disabled=True,
                    key="voice_original_display"
                )
            
            # Display enhanced prompt
            current_enhanced = st.session_state.voice_enhanced_prompt or st.session_state.get('enhanced_prompt', '')
            if current_enhanced:
                st.markdown("**Enhanced Prompt for Image Generation:**")
                enhanced_prompt = st.text_area(
                    "Enhanced prompt",
                    value=current_enhanced,
                    height=120,
                    help="You can edit this prompt before generating the image",
                    key="voice_enhanced_display"
                )
                
                # Update session state if user edits the enhanced prompt
                if enhanced_prompt != current_enhanced:
                    st.session_state.voice_enhanced_prompt = enhanced_prompt
                    st.session_state.enhanced_prompt = enhanced_prompt
                
                # Further enhance prompt with AI
                if st.checkbox("🧠 Further enhance prompt with AI", key="voice_further_enhance"):
                    if st.button("✨ Enhance Prompt"):
                        with st.spinner("Enhancing prompt with AI..."):
                            # Get API key from session state or environment
                            api_key = getattr(st.session_state, 'api_key', None) or os.getenv('BRIA_API_KEY')
                            if not api_key:
                                st.error("❌ API key not found. Please check your .env file or session state.")
                            else:
                                current_prompt = st.session_state.voice_enhanced_prompt or st.session_state.get('enhanced_prompt', '')
                                enhanced = enhance_prompt(api_key, current_prompt)
                                if enhanced and enhanced != current_prompt:
                                    st.session_state.voice_enhanced_prompt = enhanced
                                    st.session_state.enhanced_prompt = enhanced
                                    st.success("✅ Prompt enhanced!")
                                    st.rerun()
                                else:
                                    st.warning("⚠️ Prompt enhancement failed or returned the same prompt.")
            
            # Generate image button
            current_enhanced_prompt = st.session_state.voice_enhanced_prompt or st.session_state.get('enhanced_prompt', '')
            if st.button("🎨 Generate Image from Voice", type="primary", disabled=not current_enhanced_prompt):
                if current_enhanced_prompt:
                    with st.spinner("Generating image from your voice description..."):
                        try:
                            # Get API key from session state or environment
                            api_key = getattr(st.session_state, 'api_key', None) or os.getenv('BRIA_API_KEY')
                            if not api_key:
                                st.error("❌ API key not found. Please check your .env file or session state.")
                            else:
                                # Generate image using the enhanced prompt
                                result = generate_hd_image(current_enhanced_prompt, api_key)
                                
                                # Extract image URL from the result - handle multiple possible response formats
                                image_url = None
                                if result:
                                    # Try different possible response formats
                                    if isinstance(result, dict):
                                        # Format 1: {"result": [{"urls": ["..."]}]} or {"result": [{"url": "..."}]}
                                        if 'result' in result and result['result']:
                                            if isinstance(result['result'], list) and len(result['result']) > 0:
                                                first_result = result['result'][0]
                                                if isinstance(first_result, dict):
                                                    # Check for "urls" array first (actual API format)
                                                    if 'urls' in first_result and first_result['urls']:
                                                        image_url = first_result['urls'][0]
                                                    # Fallback to "url" single value
                                                    elif 'url' in first_result:
                                                        image_url = first_result['url']
                                            elif isinstance(result['result'], dict):
                                                if 'urls' in result['result'] and result['result']['urls']:
                                                    image_url = result['result']['urls'][0]
                                                elif 'url' in result['result']:
                                                    image_url = result['result']['url']
                                        
                                        # Format 2: {"result_url": "..."}
                                        elif 'result_url' in result:
                                            image_url = result['result_url']
                                        
                                        # Format 3: {"url": "..."}
                                        elif 'url' in result:
                                            image_url = result['url']
                                        
                                        # Format 4: {"result_urls": ["..."]}
                                        elif 'result_urls' in result and result['result_urls']:
                                            image_url = result['result_urls'][0]
                            
                            if image_url:
                                # Add to generated images
                                if 'generated_images' not in st.session_state:
                                    st.session_state.generated_images = []
                                
                                st.session_state.generated_images.append({
                                    'url': image_url,
                                    'prompt': current_enhanced_prompt,
                                    'source': 'voice',
                                    'timestamp': time.time()
                                })
                                
                                st.success("✅ Image generated successfully from your voice!")
                            else:
                                st.error("❌ Failed to generate image. Please try again.")
                                
                        except Exception as e:
                            st.error(f"❌ Error generating image: {str(e)}")
        else:
            st.info("👆 Upload an audio file and click 'Transcribe Audio' to get started!")
        
        # Add a clear transcription button if transcription exists
        if has_transcription:
            st.markdown("---")
            col_clear1, col_clear2 = st.columns([1, 1])
            with col_clear1:
                if st.button("🗑️ Clear Transcription", help="Clear the current transcription and start over"):
                    # Clear voice-specific session state
                    st.session_state.voice_original_prompt = ""
                    st.session_state.voice_enhanced_prompt = ""
                    st.session_state.voice_transcription_info = {}
                    st.session_state.voice_audio_uploaded = False
                    
                    # Clear global session state for compatibility
                    if 'original_prompt' in st.session_state:
                        st.session_state.original_prompt = ""
                    if 'enhanced_prompt' in st.session_state:
                        st.session_state.enhanced_prompt = ""
                    
                    st.success("✅ Transcription cleared!")
                    st.rerun()
            
            with col_clear2:
                # Show persistence status
                st.success("💾 Transcription persisted across tabs")
    
    # Display generated images from voice
    if 'generated_images' in st.session_state and st.session_state.generated_images:
        voice_generated = [img for img in st.session_state.generated_images if img.get('source') == 'voice']
        
        if voice_generated:
            st.subheader("🎨 Generated Images from Voice")
            
            for i, image_data in enumerate(voice_generated):
                with st.expander(f"Voice-generated Image {i+1} - {image_data['prompt'][:50]}..."):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.image(image_data['url'], caption="Generated Image", use_column_width=True)
                    
                    with col2:
                        st.markdown("**Original Voice Prompt:**")
                        st.text(image_data['prompt'])
                        
                        # Download button
                        try:
                            import requests
                            response = requests.get(image_data['url'])
                            if response.status_code == 200:
                                st.download_button(
                                    label="📥 Download Image",
                                    data=response.content,
                                    file_name=f"voice_image_{i+1}.png",
                                    mime="image/png"
                                )
                            else:
                                st.warning("Image not yet ready for download")
                        except Exception as e:
                            st.error(f"Download error: {str(e)}")
