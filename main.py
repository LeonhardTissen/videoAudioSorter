import tkinter as tk
from math import floor
from tkinter import filedialog
 
import numpy as np
from moviepy.editor import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
 
 
class VideoProcessor:
    def __init__(self, video_path):
        print("Initializing Video Processor...")
        self.video = VideoFileClip(video_path)
        self.fps = self.video.fps
        self.frame_interval = 1.0 / self.fps
        if not self.video.audio:
            raise ValueError("Video must have audio")
        self.audio_fps = self.video.audio.fps
        self.frame_data = []
 
    def calculate_audio_level(self, frame_audio):
        if frame_audio.size == 0:
            return 0
        return np.mean(np.sqrt((frame_audio ** 2).sum(axis=1)))
 
    def process_video(self):
        print("Processing video...")
        for frame_time in np.arange(0, self.video.duration, self.frame_interval):
            end_time = min(frame_time + self.frame_interval, self.video.duration)
            frame_audio_segment = self.video.audio.subclip(frame_time, end_time).to_soundarray(fps=self.audio_fps)
            audio_level = self.calculate_audio_level(frame_audio_segment)
 
            subclip = self.video.subclip(frame_time, end_time)
            self.frame_data.append((audio_level, subclip))
 
            frame_index = int(frame_time * self.fps)
            if frame_index % (int(self.fps) * 4) == 0 or frame_index == ((floor(self.video.duration * self.fps)) - 1):
                print(f"Processed frame {frame_index} out of {floor(self.video.duration * self.fps)}.")
 
        print("Sorting clips based on audio levels...")
        self.frame_data.sort(key=lambda x: x[0])
        return [clip for _, clip in self.frame_data]
 
def browse_for_video_file():
    print("Opening file dialog...")
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename()
 
print("Starting video rearrangement process...")
video_path = browse_for_video_file()
processor = VideoProcessor(video_path)
sorted_clips = processor.process_video()
final_clip = concatenate_videoclips(sorted_clips)
print("Writing final video file...")
final_clip.write_videofile("rearranged_video.mp4")
print("Process completed.")
