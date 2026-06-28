# -*- coding: utf-8 -*-
import os
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
OUT="C:/tmp/vid"
clips=[]; total=0
for i in range(1,8):
    aud=AudioFileClip(f"{OUT}/a{i}.mp3")
    dur=aud.duration+0.7
    total+=dur
    clips.append(ImageClip(f"{OUT}/s{i}.png").with_duration(dur).with_audio(aud))
final=concatenate_videoclips(clips, method="chain")
dst="C:/Users/Dell/Desktop/SUMMER/docs/Primus_Speaker2_video.mp4"
final.write_videofile(dst, fps=24, codec="libx264", audio_codec="aac", preset="medium", bitrate="2500k", logger=None)
print(f"WROTE {dst}  | duration {total:.0f}s  | size {os.path.getsize(dst)//1024} KB")
