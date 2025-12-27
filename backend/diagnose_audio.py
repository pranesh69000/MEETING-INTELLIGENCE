import soundcard as sc
import numpy as np

print("=== AUDIO DIAGNOSTIC TOOL ===")

try:
    default_mic = sc.default_microphone()
    print(f"Default Microphone: {default_mic.name}")
    print(f"ID: {default_mic.id}")
except Exception as e:
    print(f"Error finding default mic: {e}")

print("\n--- All Microphones ---")
try:
    all_mics = sc.all_microphones(include_loopback=True)
    for m in all_mics:
        print(f" - {m.name} (Loopback: {m.isloopback})")
except Exception as e:
    print(f"Error listing mics: {e}")

print("\n--- Testing Recording (3 seconds) ---")
try:
    mic = sc.default_microphone()
    with mic.recorder(samplerate=44100) as recorder:
        print("Recording...")
        data = recorder.record(numframes=44100*3)
        print("Stopped.")
        
        # Check integrity
        # Mono conversion
        if data.shape[1] > 1:
            data = np.mean(data, axis=1)
        else:
            data = data.flatten()
            
        max_amp = np.max(np.abs(data))
        print(f"Max Amplitude: {max_amp}")
        
        if max_amp == 0:
            print("WARNING: Recorded total silence (0 amplitude). Mic might be muted or blocked.")
        else:
            print("SUCCESS: Audio signal detected.")
            
except Exception as e:
    print(f"RECORDING FAILED: {e}")

print("=============================")
