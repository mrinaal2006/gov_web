"""Records the real dashboard demo as screenshots, on a throwaway copy of the project.

Usage: python capture.py <project_copy_dir> <output_dir>
"""
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
project, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
PORT = 8502

COMPLAINTS = [
    "ডুমুরগ্রাম গ্রামে ৩ দিন ধরে টিউবওয়েলের জল নোংরা, শিশুরা অসুস্থ হয়ে পড়ছে",
    "Dumurgram gram-e 3 din dhore jol ashche na",
    "Tubewell water in Dumurgram has been dirty for 2 days",
    "ডুমুরগ্রাম গ্রামে ৪ দিন ধরে টিউবওয়েলের জল নোংরা",
    "Dumurgram gram-e 4 din dhore jol ashche na, baccha-ra osustho hocche",
    "No drinking water supply in Dumurgram for 3 days",
    "Dumurgrm gram-e 2 din dhore jol ashche na",
    "Tubewell water in Dumurgram has been dirty for 4 days, children are falling sick",
]

server = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.headless", "true",
     "--server.port", str(PORT), "--browser.gatherUsageStats", "false"],
    cwd=project, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        page = browser.new_page(viewport={"width": 1600, "height": 900}, color_scheme="dark")
        for _ in range(30):
            try:
                page.goto(f"http://localhost:{PORT}", timeout=5000)
                break
            except Exception:
                time.sleep(1)
        page.get_by_text("Samasya Radar: District Dashboard").wait_for(timeout=90000)
        page.get_by_text("Complaint heat map").wait_for(timeout=60000)
        time.sleep(6)

        def shot(name):
            page.screenshot(path=out / f"{name}.png")
            print("shot", name)

        def scroll_to(text):
            page.get_by_text(text, exact=True).first.scroll_into_view_if_needed()
            page.evaluate(
                """t => { const h = [...document.querySelectorAll('h1,h2,h3')].find(e => e.innerText.includes(t));
                          if (h) h.scrollIntoView({block: 'start'}); }""", text)
            time.sleep(3)

        shot("overview")
        scroll_to("Complaint heat map")
        time.sleep(5)
        shot("map")
        scroll_to("Priority list: pending, most urgent first")
        shot("priority")
        scroll_to("Department scorecard")
        shot("scorecard")

        box = page.locator('[data-testid="stSidebar"] textarea')
        button = page.locator('[data-testid="stSidebar"] button', has_text="Analyse")
        for i, text in enumerate(COMPLAINTS, 1):
            box.fill(text)
            box.press("Control+Enter")
            time.sleep(1.5)
            if i == 1:
                shot("typed")
            button.click()
            time.sleep(5)
            side = page.locator('[data-testid="stSidebar"]').inner_text().replace("\n", " ")
            alert = page.get_by_text("hotspot(s) need attention").count()
            print(i, side[side.find("Department:", 20):][:80], "| alert", alert)
            if i == 1:
                shot("result")
            if i == 7:
                scroll_to("Samasya Radar: District Dashboard")
                shot("before_alert")
        page.get_by_text("hotspot(s) need attention").wait_for(timeout=20000)
        scroll_to("Samasya Radar: District Dashboard")
        time.sleep(2)
        shot("alert")
        browser.close()
finally:
    server.terminate()
