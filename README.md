---
title: AdSnap Studio
emoji: 🎨
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.32.0"
app_file: streamlit_app.py
pinned: false
---

# 🎨 AdSnap Studio

A powerful Streamlit app for generating professional product ads using Bria AI's advanced image generation and manipulation APIs.

## 🌟 Features

- 🖼️ Generate HD product images from text prompts
- 🎤 **Voice-to-Image**: Generate images from voice descriptions using Whisper AI
- 🎯 Remove backgrounds with custom colors
- 🌅 Add realistic shadows
- 🏠 Create lifestyle shots with text or reference images
- ✨ AI-powered prompt enhancement
- 📝 Optional CTA text overlay
- 🎮 Intuitive UI controls
- 💾 Easy image download

## 🚀 Quick Start

1. Clone the repository:
```bash
https://github.com/DewmikeAmarasinghe/adsnap-studio.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory:
```bash
BRIA_API_KEY=your_api_key_here
```

4. Run the app:
```bash
streamlit run app.py
```

## 💡 Usage

### Text-to-Image Generation
1. Enter a product description or upload an image
2. Configure generation options in the sidebar:
   - Enhance prompt with AI
   - Remove background
   - Add shadows
   - Generate lifestyle shots
3. Adjust advanced settings like background color and shadow intensity
4. Click "Generate Ad" to create your images
5. Download the results

### Voice-to-Image Generation
1. Navigate to the "🎤 Voice to Image" tab
2. Upload an audio file describing your product (WAV, MP3, M4A, FLAC, OGG)
3. Select Whisper model size and language (optional)
4. Click "Transcribe Audio" to convert speech to text
5. Review and enhance the generated prompt
6. Click "Generate Image from Voice" to create your image
7. Download the generated image

## 🔧 Configuration

The app supports various configuration options through the UI:

- **Voice-to-Image**: Convert voice descriptions to product images using OpenAI Whisper
- **Prompt Enhancement**: Improve your text prompts with AI
- **Background Removal**: Remove backgrounds with custom colors
- **Shadow Effects**: Add realistic shadows with adjustable intensity
- **Lifestyle Shots**: Place products in context using text or reference images
- **CTA Text**: Add optional call-to-action text overlays

## 🔧 Recent Improvements & Bug Fixes

This project has been enhanced with several key improvements and bug fixes:

### ✨ New Features Added:
- **🎤 Voice-to-Image Integration**: Complete implementation of speech-to-text functionality using OpenAI Whisper
- **🔄 Multi-Method Audio Transcription**: Robust fallback system for Windows compatibility and various audio formats
- **💾 Persistent Session State**: Transcription and enhanced prompts now persist across tab navigation and page refreshes
- **🖼️ Unified Image Preview**: Consistent image preview and download functionality across all generation tabs
- **🎯 Smart Prompt Enhancement**: AI-powered enhancement of voice transcriptions for better image generation

### 🐛 Critical Bug Fixes:
- **Fixed Create Packshot Error**: Resolved "No module named 'services.background_service'" by implementing proper background removal service
- **Fixed Audio Transcription Issues**: Resolved Windows file access errors with multi-method fallback approach
- **Fixed Image Generation Failures**: Improved API response parsing and URL extraction logic
- **Fixed Session State Persistence**: Resolved data loss issues when navigating between tabs
- **Fixed Import Dependencies**: Updated all service imports and exports for proper module resolution
### 🎨 UI/UX Improvements:
- **Enhanced Error Handling**: Added comprehensive error messages and debugging information
- **Improved File Management**: Clean codebase organization with proper file naming conventions
### 🔒 Security & Performance:
- **Secure API Key Handling**: Masked input fields and proper environment variable management
- **Optimized Audio Processing**: Efficient temporary file handling with automatic cleanup
- **Content Moderation**: Built-in safety features for generated content
- **Fallback Mechanisms**: Graceful degradation when APIs are unavailable
## 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
## 🙏 Acknowledgments
- [Bria AI](https://bria.ai) for their powerful image generation APIs
- [Streamlit](https://streamlit.io) for the amazing web framework
- [Ayush Singh](https://www.youtube.com/watch?v=yH1IdJAN7jA) for the inspiring YouTube tutorial that served as the foundation for the Voice-to-Image feature implementation
- [OpenAI Whisper](https://openai.com/research/whisper) for the speech-to-text transcription capabilities