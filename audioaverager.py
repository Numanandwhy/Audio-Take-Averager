import librosa
import numpy as np
import soundfile as sf
def detect_hits(y, sr):
    """Detect the hit times in the audio."""
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=True)
    return librosa.frames_to_time(onset_frames, sr=sr)

def volume_at_time(y, sr, time):
    """Calculate the volume at a specific time in the audio."""
    frame = librosa.time_to_samples(time, sr=sr)
    if 0 <= frame < len(y):
        window = y[frame:frame+int(sr*0.1)]  # 0.1s window
        amplitude = np.mean(window**2)  # Mean squared amplitude in the window
        amplitude = max(amplitude, 1e-10)  # Avoid log of zero
        return 10 * np.log10(amplitude)  # dB
    return None

def extract_hit(y, sr, time, duration=0.2, offset=0.01):
    """
    Extract a segment of audio centered around the hit time.
    'offset' is how much earlier before the hit time to start the segment.
    """
    start_frame = max(0, int((time - offset - duration/2) * sr))
    end_frame = min(len(y), int((time - offset + duration/2) * sr))
    return y[start_frame:end_frame]


if __name__ == "__main__":
    # File paths for the takes
    file_paths = [f'take{i+1}.wav' for i in range(6)]

    # Load the audio data for all takes
    takes_data = []
    for file_path in file_paths:
        try:
            audio, sr = librosa.load(file_path, sr=None)
            takes_data.append((audio, sr))
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    
    
    # Initialize lists to store all hit times and volumes from all takes
    all_hit_times = []
    all_volumes = []

    # Process each take
    for audio, sr in takes_data:
        # Detect hit times
        hit_times = detect_hits(audio, sr)
        all_hit_times.append(hit_times)

        # Measure volume at each hit time
        volumes = [volume_at_time(audio, sr, hit_time) for hit_time in hit_times]
        all_volumes.append(volumes)

    # Calculate the average hit time for each position
    # Ensuring all hit time lists are of the same length
    min_length = min(map(len, all_hit_times))
    all_hit_times = [hits[:min_length] for hits in all_hit_times]
    average_hit_times = np.mean(np.array(all_hit_times), axis=0)
    #make average hit times items = current value - the first items value
    average_hit_times = [time - average_hit_times[0] for time in average_hit_times]
    print(average_hit_times)

    # Calculate average volumes
    # Ensuring all volume lists are of the same length
    min_length = min(map(len, all_volumes))
    all_volumes = [vols[:min_length] for vols in all_volumes]
    volumes = np.array([[float(v) for v in vol_list] for vol_list in all_volumes])
    average_volumes = np.mean(volumes, axis=0)

    print("Average Hit Times (seconds):", [round(time, 2) for time in average_hit_times])
    print("Average Volumes for Each Hit Position:", [round(volume, 2) for volume in average_volumes])

    # Continue with the creation of the new take as outlined in the previous message...


    # Initialize new take as a silent array
    duration = max(average_hit_times) + 0.5  # Extend duration beyond the last hit
    new_take = np.zeros(int(duration * sr))

    # Process each hit
    # Process each hit
for i, (avg_time, avg_vol) in enumerate(zip(average_hit_times, average_volumes)):
    closest_diff = float('inf')
    closest_hit_segment = None
    for audio, sr in takes_data:
        hit_times = detect_hits(audio, sr)
        volumes = [volume_at_time(audio, sr, t) for t in hit_times]
        # Find the hit closest to the average volume
        for hit_time, volume in zip(hit_times, volumes):
            diff = abs(volume - avg_vol)
            if diff < closest_diff:
                closest_diff = diff
                closest_hit_segment = extract_hit(audio, sr, hit_time, offset=0.01)  # Adjusted call

    # Align the closest hit segment in the new take
    align_frame = int(avg_time * sr)
    segment_length = len(closest_hit_segment)
    end_frame = min(len(new_take), align_frame + segment_length)
    new_take[align_frame:end_frame] = closest_hit_segment[:end_frame-align_frame]

# Continue with saving the new take as before
sf.write('new_take3.wav', new_take, sr)


