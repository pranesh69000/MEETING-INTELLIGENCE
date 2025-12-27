import whisper
import os
import torch
import warnings

# Suppress FP16 warning for CPU if CUDA not available
warnings.filterwarnings("ignore")

class Transcriber:
    def __init__(self, model_size="base"):
        print(f"Loading Whisper model: {model_size}...")
        # Check if CUDA (GPU) is available, otherwise use CPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        self.model = whisper.load_model(model_size, device=device)
        print("Model loaded successfully.")

    def transcribe(self, file_path):
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        print(f"Transcribing {file_path}...")
        
        # Check if FFmpeg is available
        import shutil
        if not shutil.which("ffmpeg"):
            print("ERROR: FFmpeg not found in system PATH.")
            return {"error": "FFmpeg not detected. Please install FFmpeg."}

        # Transcribe with timestamps
        try:
            result = self.model.transcribe(file_path, fp16=False)
            print(f"DEBUG RAW TEXT: '{result['text']}'")
        except Exception as e:
            print(f"Transcription Error: {e}")
            return {"error": str(e)}
        
        # Format the segments
        # We can simulate diarization (Speaker X) if needed later, 
        # Format the segments with Heuristic Speaker Labels
        # Logic: If gap between segments > 1.0s, assume speaker change or pause.
        # Use simple toggling A/B for visual distinction.
        formatted_text = ""
        current_speaker = "Speaker A"
        last_end_time = 0
        
        for segment in result["segments"]:
            start = float(segment["start"])
            end = float(segment["end"])
            text = segment["text"].strip()
            
            # If gap is significant OR previous text was a question (Q&A), switch speaker
            gap = start - last_end_time
            is_question = text.endswith("?")
            print(f"Gap: {gap:.2f}s | Question: {is_question} | Current: {current_speaker}")
            
            if (gap > 0.5) or (is_question):
                current_speaker = "Speaker B" if current_speaker == "Speaker A" else "Speaker A"
                print(f"--> SWITCHED to {current_speaker}")
            
            formatted_text += f"[{int(start)}s] **{current_speaker}:** {text}\n"
            last_end_time = end
            
        return {
            "full_text": result["text"],
            "formatted_text": formatted_text,
            "segments": result["segments"]
        }
