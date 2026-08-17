from moviepy import VideoFileClip
from tkinter.filedialog import askopenfilename

vid = askopenfilename()

video = VideoFileClip(vid)

audio = video.audio

audio.write_audiofile("demo.mp3")

print("---Saved---")