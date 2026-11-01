"""Builds the promo video from the screenshots made by capture.py.

Usage: python build_video.py <screenshots_dir> <work_dir> <output.mp4>
Needs Windows (narration uses System.Speech), Edge, playwright and imageio-ffmpeg.
"""
import subprocess
import sys
import wave
from pathlib import Path

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

shots, work, output = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
work.mkdir(parents=True, exist_ok=True)
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 30

CSS = """
*{box-sizing:border-box;margin:0}
body{width:1920px;height:1080px;background:#0e1117;color:#fafafa;overflow:hidden;
     font-family:'Segoe UI','Nirmala UI',sans-serif;position:relative}
.center{height:100%;display:flex;flex-direction:column;justify-content:center;padding:0 170px}
.big{font-size:104px;font-weight:700;line-height:1.14;letter-spacing:-2px}
.mid{font-size:50px;line-height:1.35;color:#c9ccd3;margin-top:36px}
.red{color:#ff5c5c}
.kicker{font-size:30px;font-weight:600;color:#ff5c5c;letter-spacing:3px;text-transform:uppercase;margin-bottom:28px}
.note{font-size:30px;color:#9aa0ab;margin-top:44px}
.screen{position:absolute;left:160px;top:24px;width:1600px;height:900px;border-radius:12px;
        overflow:hidden;box-shadow:0 0 0 1px #2a2f3a}
.screen img{display:block}
.mark{position:absolute;border:5px solid #ff5c5c;border-radius:10px;box-shadow:0 0 34px #ff5c5c88}
.caption{position:absolute;left:160px;right:160px;top:946px;font-size:46px;font-weight:600;line-height:1.2}
.badge{position:absolute;right:160px;top:1022px;font-size:24px;color:#9aa0ab}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:40px}
.card{background:#1a1e27;border-left:7px solid #ff5c5c;border-radius:10px;padding:18px 26px;height:158px}
.card.hide{visibility:hidden}
.tag{font-size:22px;font-weight:700;color:#ff9b9b;letter-spacing:2px}
.text{font-size:31px;line-height:1.28;margin-top:6px}
.count{font-size:74px;font-weight:700}
.split{display:flex;gap:80px;align-items:center;height:100%;padding:0 150px}
.steps{font-size:50px;line-height:1.2;font-weight:600}
.steps div{margin:44px 0;padding-left:34px;border-left:7px solid #ff5c5c}
.steps small{display:block;font-size:32px;font-weight:400;color:#b5b9c2;margin-top:8px}
.who{display:grid;grid-template-columns:1fr 1fr 1fr;gap:36px;margin-top:60px}
.who>div{background:#1a1e27;border-radius:14px;padding:44px 38px;height:330px}
.who b{font-size:44px;display:block;margin-bottom:22px}
.who span{font-size:34px;line-height:1.32;color:#c9ccd3}
"""


def img(name):
    return (shots / f"{name}.png").as_uri()


def screen(name, caption, marks=()):
    boxes = "".join(f'<div class="mark" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"></div>'
                    for x, y, w, h in marks)
    return (f'<div class="screen"><img src="{img(name)}">{boxes}</div>'
            f'<div class="caption">{caption}</div><div class="badge">Demo with simulated data</div>')


def title(big, mid="", kicker="", note=""):
    return (f'<div class="center">{f"<div class=kicker>{kicker}</div>" if kicker else ""}'
            f'<div class="big">{big}</div>{f"<div class=mid>{mid}</div>" if mid else ""}'
            f'{f"<div class=note>{note}</div>" if note else ""}</div>')


COMPLAINTS = [
    ("BENGALI", "ডুমুরগ্রাম গ্রামে ৩ দিন ধরে টিউবওয়েলের জল নোংরা, শিশুরা অসুস্থ হয়ে পড়ছে"),
    ("BANGLISH", "Dumurgram gram-e 3 din dhore jol ashche na"),
    ("ENGLISH", "Tubewell water in Dumurgram has been dirty for 2 days"),
    ("BENGALI", "ডুমুরগ্রাম গ্রামে ৪ দিন ধরে টিউবওয়েলের জল নোংরা"),
    ("BANGLISH", "Dumurgram gram-e 4 din dhore jol ashche na, baccha-ra osustho hocche"),
    ("ENGLISH", "No drinking water supply in Dumurgram for 3 days"),
    ("BANGLISH + TYPO", "Dumurgrm gram-e 2 din dhore jol ashche na"),
    ("ENGLISH", "Tubewell water in Dumurgram has been dirty for 4 days, children are falling sick"),
]


def cards(shown):
    items = "".join(
        f'<div class="card{"" if i < shown else " hide"}"><div class="tag">{t}</div><div class="text">{x}</div></div>'
        for i, (t, x) in enumerate(COMPLAINTS))
    return (f'<div class="center" style="padding:0 150px"><div class="count">{shown} of 8 '
            f'<span style="font-size:42px;font-weight:400;color:#b5b9c2">water complaints from one village</span></div>'
            f'<div class="cards">{items}</div></div>')


RESULT = f"""<div class="split">
<div style="flex:none;width:640px;height:760px;border-radius:14px;overflow:hidden;box-shadow:0 0 0 1px #2a2f3a">
  <img src="{img('result')}" style="width:3200px;margin:-740px 0 0 -6px"></div>
<div class="steps">
  <div>Reads the language<small>Bengali, English or Banglish</small></div>
  <div>Picks the department<small>Water</small></div>
  <div>Finds the village<small>Dumurgram</small></div>
  <div>Scores the urgency<small>Out of 100</small></div>
</div></div><div class="badge">Demo with simulated data</div>"""

WHO = title("Who it's for") .replace("</div></div>", "</div>" + """
<div class="who">
 <div><b>District officers</b><span>See hotspots and compare departments across blocks.</span></div>
 <div><b>Block teams</b><span>Start with the pending complaints that score highest.</span></div>
 <div><b>Helplines and portals</b><span>Send complaints in through the API.</span></div>
</div></div>""")

# (html or list of html frames, narration). "Suh-muss-yah" and "Beer-bhoom" steer the speech engine.
SCENES = [
    (title("One complaint about dirty water <span class=red>looks small.</span>"),
     "One complaint about dirty water looks small."),
    (title("Eight from one village in two days <span class=red>could be a warning.</span>",
           "But they can arrive in different languages, worded in different ways."),
     "Eight from one village in two days could be a warning. But they can arrive in different languages, "
     "worded in different ways."),
    (title("Samasya Radar", "Helps district teams spot the pattern in citizen complaints, "
                            "in Bengali, English and Banglish."),
     "Suh-muss-yah Radar helps district teams spot that pattern, in Bengali, English and Banglish."),
    (title("A water problem in one village", kicker="Use case",
           note="Example scenario in Birbhum district. All complaints in this demo are simulated."),
     "Here is an example scenario from Beer-bhoom district. Every complaint in this demo is simulated."),
    (RESULT,
     "A resident reports dirty tubewell water, in Bengali. Suh-muss-yah Radar assigns it to the Water department, "
     "finds the village, and gives it an urgency score."),
    ([cards(i) for i in range(2, 9)],
     "More reports arrive, in Bengali, English and Banglish. Even a misspelled village name is matched."),
    (screen("alert", "The 8th complaint in 48 hours raises a <span class=red>hotspot alert.</span>",
            [(380, 302, 1140, 144)]),
     "On the eighth water complaint within forty eight hours, a hotspot alert appears, naming the village "
     "and the department."),
    (screen("map", "The heat map shows where complaints concentrate."),
     "The heat map shows where complaints are concentrated across the district."),
    (screen("priority", "The priority list puts the highest urgency scores first.", [(1332, 122, 64, 388)]),
     "The priority list puts pending complaints with the highest urgency scores at the top, "
     "so officers know where to look first."),
    (screen("scorecard", "The scorecard tracks resolution time, block by block.", [(886, 122, 304, 388)]),
     "The scorecard tracks complaints and resolution times, block by block, "
     "and a weekly PDF report sums it up for review meetings."),
    (WHO,
     "It is built for district officers, block teams, and helplines, and portals can send complaints in through its API."),
    (title("Samasya Radar", "See the pattern sooner.",
           note="Working prototype, ready for real-world testing."),
     "Suh-muss-yah Radar. See the pattern sooner. A working prototype, ready for real-world testing."),
]


def run(*args):
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", *map(str, args)], check=True)


def speak(text, path):
    script = ("Add-Type -AssemblyName System.Speech;"
              "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
              "$s.SelectVoice('Microsoft Zira Desktop');$s.Rate=0;"
              f"$s.SetOutputToWaveFile('{path}');$s.Speak('{text.replace(chr(39), chr(39) * 2)}');$s.Dispose()")
    subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True)
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    page = browser.new_page(viewport={"width": 1920, "height": 1080})

    def render(html, path):
        source = path.with_suffix(".html")
        source.write_text(f'<!doctype html><meta charset="utf-8"><style>{CSS}</style><body>{html}', encoding="utf-8")
        page.goto(source.as_uri())
        page.wait_for_load_state("networkidle")
        page.screenshot(path=path)

    parts = []
    for n, (html, narration) in enumerate(SCENES, 1):
        wav, clip = work / f"s{n:02d}.wav", work / f"s{n:02d}.mp4"
        seconds = speak(narration, wav) + 1.3
        fade = f"fade=in:st=0:d=0.3,fade=out:st={seconds - 0.3:.2f}:d=0.3,format=yuv420p"
        audio = ["-i", wav, "-af", "adelay=500:all=1,apad,aresample=48000", "-ac", "2", "-c:a", "aac", "-b:a", "160k"]
        if isinstance(html, list):
            # Reveal frames evenly across the narration, then hold the last one
            step = seconds / (len(html) + 1)
            lines = []
            for i, frame in enumerate(html):
                png = work / f"s{n:02d}_{i}.png"
                render(frame, png)
                hold = step * 2 if i == len(html) - 1 else step
                lines += [f"file '{png.as_posix()}'", f"duration {hold:.3f}"]
            lines.append(f"file '{png.as_posix()}'")
            listing = work / f"s{n:02d}.txt"
            listing.write_text("\n".join(lines), encoding="utf-8")
            run("-f", "concat", "-safe", 0, "-i", listing, *audio, "-vf", f"fps={FPS},{fade}",
                "-t", f"{seconds:.2f}", "-c:v", "libx264", "-crf", 19, clip)
        else:
            png = work / f"s{n:02d}.png"
            render(html, png)
            frames = int(seconds * FPS)
            zoom = (f"scale=3840:-1,zoompan=z='1+0.025*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                    f":d={frames}:s=1920x1080:fps={FPS},{fade}")
            run("-i", png, *audio, "-vf", zoom, "-t", f"{seconds:.2f}", "-c:v", "libx264", "-crf", 19, clip)
        parts.append(clip)
        print(f"scene {n}: {seconds:.1f}s")
    browser.close()

listing = work / "all.txt"
listing.write_text("\n".join(f"file '{c.as_posix()}'" for c in parts), encoding="utf-8")
output.parent.mkdir(parents=True, exist_ok=True)
run("-f", "concat", "-safe", 0, "-i", listing, "-c", "copy", "-movflags", "+faststart", output)
print("wrote", output)
