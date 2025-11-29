# Album Metadata Manager (v1.0)

Fully scriptable album tagger that keeps your library consistent by standardizing metadata and embedding cover art directly into your files.

## 1. Overview
Album Metadata Manager is a terminal-driven Python utility. Point it at a single album folder and it will walk you through confirming track names, collecting album-wide metadata, picking cover art, and writing consistent tags into MP3, FLAC, M4A, or MP4 files.

## 2. Feature Highlights
- Interactive confirmation for every track, with rename and skip controls.
- Global metadata application (Artist, Album, Genre, Year, track numbers) in one pass.
- Automatic cover discovery, multi-image selection, and a fallback system dialog so you can browse to artwork stored elsewhere.
- Smart defaults: folder name used as album title, "Unknown Smuggler" suggested for artist, and the current calendar year pre-filled.
- Timestamped session summary so you always know what was changed.

## 3. Prerequisites
- **Operating System**: Windows, macOS, or Linux with terminal access.
- **Python**: 3.8 or newer (3.11 recommended). Check with `python --version`.
- **Pip**: Installed alongside Python for dependency management.
- **Libraries**: [`mutagen`](https://mutagen.readthedocs.io/) plus the built-in `tkinter` module (ships with most desktop Python builds).

### Verify tkinter availability
Run the snippet below; if it prints a version number, you are set:
```bash
python - <<'PY'
import tkinter
print(tkinter.TkVersion)
PY
```
If tkinter is missing, install/reinstall Python using an installer that includes "tcl/tk and IDLE" (enabled by default on python.org builds).

## 4. Pre-Flight Checklist
1. Backup the album folder (metadata edits are destructive).
2. Ensure all tracks for one album are stored together; remove stray files you do not want tagged.
3. Collect cover art (`.jpg` or `.png`). If it lives elsewhere, note the path so you can browse to it during the run.
4. Confirm you have write permissions for the folder.
5. Optional: run `pip install mutagen` ahead of time to save a prompt during first launch.

## 5. Installation & Setup
1. **Install mutagen**
   ```bash
   pip install mutagen
   ```
2. **Copy the script**
   Place `album_tagger.py` directly inside the album folder you plan to tag.
3. **(Optional) Stage artwork**
   Drop a single image file into the folder if you already know which cover you want applied.

## 6. Usage Guide
1. Open a terminal inside the album folder.
2. Run the tool:
   ```bash
   python album_tagger.py
   ```
3. Follow the prompts:
   - **Tracklist confirmation**: Include, skip, or rename every detected track.
   - **Album metadata**: Accept defaults (press Enter) or supply custom Album/Artist/Genre/Year values.
   - **Cover art selection**: Pick from detected images or accept the offer to browse via the OS dialog.
   - **Summary**: Review the recap to verify what was written.

## 7. Example Session
```
🚀 AEiOU'S ALBUM METADATA MANAGER v1.0
Current Directory: D:\Music\MyAlbum
Session Timestamp: 2025-11-28 10:31:22
---------------------------------------

... prompts trimmed for brevity ...

--- SESSION SUMMARY ---
Album : Greatest Hits
Artist: My Artist
Genre : Rock
Year  : 2025
Cover : D:\Music\MyAlbum\alt-art.png

✅ All tracks tagged successfully. Execution complete.
```

## 8. Troubleshooting
- **No audio files found**: Confirm the folder only contains supported formats (`.mp3`, `.flac`, `.m4a`, `.mp4`).
- **Mutagen import errors**: Re-run `pip install mutagen` in the same Python environment you use to execute the script.
- **tkinter warnings or missing file dialog**: Ensure you are running a desktop build of Python with Tcl/Tk support (see verification snippet above). The script falls back to manual path entry if the dialog cannot open.
- **Permission denied**: Close media players using the files and make sure the folder is not read-only.

## 9. License
This tool is provided as-is for personal and educational use.
