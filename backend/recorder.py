import soundcard as sc
import soundfile as sf
import numpy as np
import threading
import os
import time

class AudioRecorder:
    def __init__(self, output_dir="../recordings", sample_rate=44100):
        # 44.1kHz is more compatible with Windows microphones than 16kHz
        # Output dir is now ../recordings to avoid triggering uvicorn reload in ./backend
        self.output_dir = os.path.abspath(output_dir)
        self.sample_rate = sample_rate
        self.is_recording = False
        self.frames_system = []
        self.frames_mic = []
        self.threads = []
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def _get_loopback_mic(self):
        """Finds system output (what you hear)."""
        try:
            default_speaker = sc.default_speaker()
            mics = sc.all_microphones(include_loopback=True)
            for mic in mics:
                if mic.name == default_speaker.name and mic.isloopback:
                    return mic
            for mic in mics:
                if mic.isloopback:
                    return mic
            return sc.default_microphone()
        except:
            return sc.default_microphone()

    def _get_user_mic(self):
        """Finds user input (physical microphone), avoiding Stereo Mix."""
        try:
            default = sc.default_microphone()
            # If default is Stereo Mix (which catches system audio), switch to real mic
            if "Stereo Mix" in default.name:
                all_mics = sc.all_microphones(include_loopback=False)
                for mic in all_mics:
                    if "Microphone" in mic.name and "Stereo Mix" not in mic.name:
                        print(f"Switched Mic from {default.name} to {mic.name}")
                        return mic
            return default
        except:
            print("Error finding default mic")
            return None

    def _record_stream(self, source, frame_storage, source_name):
        """Generic recording loop for a specific source."""
        if not source:
            print(f"Source {source_name} not available.")
            return

        print(f"Started recording: {source_name} ({source.name})")
        try:
            with source.recorder(samplerate=self.sample_rate) as recorder:
                while self.is_recording:
                    try:
                        # Record chunks (blocksize)
                        data = recorder.record(numframes=1024)
                        # soundcard returns [samples, channels]. We want mono for mixing.
                        if data.shape[1] > 1:
                            data = np.mean(data, axis=1)
                        else:
                            data = data.flatten()
                            
                        frame_storage.append(data)
                    except Exception as loop_err:
                        # If one chunk fails, don't crash the thread, just log
                        # print(f"Frame drop in {source_name}: {loop_err}")
                        pass
        except Exception as e:
            print(f"Critical error recording {source_name}: {e}")

    def start_recording(self):
        if self.is_recording:
            return "Already recording"
        
        self.is_recording = True
        self.frames_system = []
        self.frames_mic = []
        self.threads = []
        
        filename = f"meeting_{int(time.time())}.wav"
        
        # Thread 1: System Audio
        sys_mic = self._get_loopback_mic()
        t1 = threading.Thread(target=self._record_stream, args=(sys_mic, self.frames_system, "System Audio"))
        self.threads.append(t1)
        
        # Thread 2: User Microphone
        user_mic = self._get_user_mic()
        t2 = threading.Thread(target=self._record_stream, args=(user_mic, self.frames_mic, "User Mic"))
        self.threads.append(t2)
        
        # Start both
        for t in self.threads:
            t.start()
            
        return filename

    def stop_recording(self):
        if not self.is_recording:
            return "Not recording"
            
        self.is_recording = False
        # Wait for threads to finish
        for t in self.threads:
            try:
                t.join(timeout=2.0) # Don't block forever if thread hangs
            except:
                pass
            
        return self._save_mixed_audio()

    def _save_mixed_audio(self):
        """Mixes the two streams and saves to file."""
        filename = f"meeting_{int(time.time())}.wav"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # Convert lists to arrays
            if not self.frames_system and not self.frames_mic:
                print("No audio recorded from either source.")
                return None

            # Handle empty streams (e.g. if mic failed)
            sys_audio = np.concatenate(self.frames_system) if self.frames_system else np.array([])
            mic_audio = np.concatenate(self.frames_mic) if self.frames_mic else np.array([])
            
            print(f"Mixing Audio - System Frames: {len(sys_audio)}, Mic Frames: {len(mic_audio)}")
            
            # If one is empty, use the other
            if len(sys_audio) == 0 and len(mic_audio) == 0:
                 return None
            elif len(sys_audio) == 0:
                 mixed_audio = mic_audio
            elif len(mic_audio) == 0:
                 mixed_audio = sys_audio
            else:
                # Pad to equal length
                max_len = max(len(sys_audio), len(mic_audio))
                
                if len(sys_audio) < max_len:
                    pad_width = max_len - len(sys_audio)
                    sys_audio = np.pad(sys_audio, (0, pad_width))
                    
                if len(mic_audio) < max_len:
                    pad_width = max_len - len(mic_audio)
                    mic_audio = np.pad(mic_audio, (0, pad_width))
                    
                # Mix (Average)
                mixed_audio = (sys_audio + mic_audio) / 2.0
            
            sf.write(file=filepath, data=mixed_audio, samplerate=self.sample_rate)
            print(f"Mixed recording saved to {filepath}")
            return filename
            
        except Exception as e:
            print(f"Error saving audio: {e}")
            return None
