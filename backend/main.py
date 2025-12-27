from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from recorder import AudioRecorder
from transcriber import Transcriber
from drive_sync import DriveManager
from intelligence import MeetingIntelligence

app = FastAPI()

# Enable CORS for React Frontend (Port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
recorder = AudioRecorder()
transcriber = None # Load lazily or on startup
drive_manager = None 
intelligence = None
latest_file = None

class ProcessingStatus:
    is_recording = False
    is_processing = False
    last_transcript = ""
    status_message = "Ready"

state = ProcessingStatus()

@app.on_event("startup")
async def startup_event():
    # Load model on startup to avoid delay during request
    global transcriber, drive_manager, intelligence
    transcriber = Transcriber()
    intelligence = MeetingIntelligence()
    
    # Initialize Drive Manager (might prompt browser login on first run)
    # Initialize Drive Manager (might prompt browser login on first run)
    try:
        drive_manager = DriveManager()
    except Exception as e:
        print(f"Drive Auth Warning: {e}")

@app.post("/start")
def start_recording():
    if state.is_recording:
        raise HTTPException(status_code=400, detail="Already recording")
    
    global latest_file
    latest_filename = recorder.start_recording()
    latest_file = os.path.join(recorder.output_dir, latest_filename)
    
    state.is_recording = True
    state.status_message = "Recording in progress..."
    return {"status": "started", "file": latest_filename}

@app.post("/stop")
def stop_recording(background_tasks: BackgroundTasks):
    if not state.is_recording:
        raise HTTPException(status_code=400, detail="Not recording")
    
    saved_filename = recorder.stop_recording()
    
    # Update latest_file to point to the actual saved (mixed) file
    # This fixes the bug where we processed the 'start' timestamp instead of 'end'
    if saved_filename:
        # Construct absolute path to the saved file
        # output_dir is already absolute in recorder
        global latest_file
        latest_file = os.path.join(recorder.output_dir, saved_filename)
        
    state.is_recording = False
    state.status_message = "Recording saved. Starting transcription..."
    
    # Trigger background transcription with the CORRECT file
    if latest_file and os.path.exists(latest_file):
        background_tasks.add_task(process_recording, latest_file)
    else:
        state.status_message = "Error: Recording file not found."
        
    return {"status": "stopped", "message": "Processing started in background"}

def process_recording(file_path):
    state.is_processing = True
    try:
        print(f"Processing: {file_path}")
        result = transcriber.transcribe(file_path)
        
        if "error" in result:
             state.status_message = f"Transcription failed: {result['error']}"
             return

        # Generate Intelligent Report
        if intelligence:
            print("Generating Intelligence Report...")
            full_report = intelligence.generate_report(result["full_text"], result["formatted_text"])
        else:
            full_report = result["formatted_text"]

        state.last_transcript = full_report # Show report in UI preview too
        state.status_message = "Transcription & Intelligence Complete. Ready to Sync."
        
        # Save to local file
        txt_path = file_path.replace(".wav", ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(full_report)
            
        # Sync to Drive
        if drive_manager:
            state.status_message = "Uploading to Drive..."
            res = drive_manager.upload_file(txt_path)
            if "link" in res:
                state.status_message = f"Done! Saved to Drive: {res['link']}"
            else:
                state.status_message = f"Transcribed, but Drive Upload failed: {res.get('error')}"
        else:
             state.status_message = "Transcribed (Local Only - No Drive Credentials)"
            
    except Exception as e:
        print(f"Error processing: {e}")
        state.status_message = f"Error: {str(e)}"
    finally:
        state.is_processing = False

@app.post("/upload_last")
def upload_last():
    if not state.last_transcript:
        return {"message": "No transcript available to upload"}
    
    if drive_manager and latest_file:
        txt_path = latest_file.replace(".wav", ".txt")
        if os.path.exists(txt_path):
             res = drive_manager.upload_file(txt_path)
             return {"message": "Uploaded", "link": res.get("link")}
    
    return {"message": "Upload failed or not configured"}

@app.get("/status")
def get_status():
    return {
        "is_recording": state.is_recording,
        "is_processing": state.is_processing,
        "message": state.status_message,
        "last_transcript": state.last_transcript if state.last_transcript else ""
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
