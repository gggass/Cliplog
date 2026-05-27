import subprocess
import time
import json
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk


class ClipboardMonitor:
    def __init__(self):
        self._stop_event = threading.Event()
        self._thread = None
        self._clip_exe = Path(__file__).parent / "clip.exe"

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def start(self):
        if self.running:
            return
        self._stop_event.clear()
        records_dir = Path(__file__).parent / "records"
        records_dir.mkdir(exist_ok=True)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2)

    def _run(self):
        last_text = ""
        while not self._stop_event.is_set():
            try:
                result = subprocess.run(
                    [str(self._clip_exe)],
                    capture_output=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=5
                )

                if result.returncode != 0:
                    time.sleep(1)
                    continue

                if result.stdout is None:
                    time.sleep(1)
                    continue
                text = result.stdout.strip()
                if text == last_text or text == "":
                    time.sleep(1)
                    continue

                date_str = datetime.now().strftime("%Y-%m-%d")
                record = {
                    "time": datetime.now().isoformat(),
                    "text": text,
                    "length": len(text)
                }

                filepath = str(
                    self._clip_exe.parent / "records" / f"{date_str}.jsonl"
                )
                with open(filepath, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")

                last_text = text
                print(f"[{record['time']}] recorded ({len(text)} chars)")

            except FileNotFoundError:
                print("[ERROR] clip.exe not found")
                break
            except subprocess.TimeoutExpired:
                pass
            except Exception as e:
                print(f"[ERROR] {e}")

            time.sleep(1)


def build_ui():
    monitor = ClipboardMonitor()

    root = tk.Tk()
    root.title("Cliplog")
    root.geometry("220x100")
    root.resizable(False, False)

    status_label = ttk.Label(root, text="Stopped", foreground="gray")
    status_label.pack(pady=(12, 4))

    btn_frame = ttk.Frame(root)
    btn_frame.pack()

    def on_start():
        monitor.start()
        status_label.config(text="Running", foreground="green")

    def on_stop():
        monitor.stop()
        status_label.config(text="Stopped", foreground="gray")

    start_btn = ttk.Button(btn_frame, text="Start", command=on_start)
    start_btn.pack(side="left", padx=4)

    stop_btn = ttk.Button(btn_frame, text="Stop", command=on_stop)
    stop_btn.pack(side="left", padx=4)

    root.mainloop()


if __name__ == "__main__":
    build_ui()
