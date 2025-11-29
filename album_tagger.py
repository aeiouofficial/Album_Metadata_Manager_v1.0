import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from mutagen.id3 import ID3, TPE1, TIT2, TALB, TCON, TRCK, TDRC, APIC, error
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4

# --- CONFIGURATION ---
# Supported audio and image extensions
AUDIO_EXTS = ['.mp3', '.flac', '.m4a', '.mp4']
IMAGE_EXTS = ['.jpg', '.jpeg', '.png']
# Default genre tags for quick entry
DEFAULT_GENRE = "Imperial Underground"
# ---

def get_audio_files(directory: str) -> List[str]:
    """Scans the directory for supported audio files."""
    return sorted([
        f for f in os.listdir(directory)
        if any(f.lower().endswith(ext) for ext in AUDIO_EXTS)
    ])

def get_file_handler(file_path: str):
    """Returns the correct mutagen handler based on file extension."""
    if file_path.lower().endswith('.mp3'):
        return MP3(file_path, ID3=ID3)
    elif file_path.lower().endswith('.flac'):
        return FLAC(file_path)
    elif file_path.lower().endswith('.m4a') or file_path.lower().endswith('.mp4'):
        # Added M4A/MP4 support just in case, requires mutagen.mp4
        return MP4(file_path)
    else:
        return None

def determine_mime_type(file_name: str) -> str:
    """Returns the MIME type for supported image extensions."""
    if file_name.lower().endswith('.png'):
        return 'image/png'
    return 'image/jpeg'

def infer_album_title(directory: str) -> str:
    """Uses the folder name as a sensible default album title."""
    folder_name = os.path.basename(os.path.normpath(directory))
    return folder_name or "Untitled Album"

def prompt_for_manual_cover_art() -> Tuple[Optional[str], Optional[str]]:
    """Allows the user to manually pick a cover image via dialog or path input."""
    wants_manual = input("Would you like to select a cover image manually? (Y/n): ").strip().lower()
    if wants_manual and wants_manual.startswith('n'):
        return None, None

    selected_path: Optional[str] = None

    try:
        from tkinter import Tk, filedialog

        root = Tk()
        root.withdraw()
        try:
            selected_path = filedialog.askopenfilename(
                title="Select cover art image",
                filetypes=[("Image files", "*.jpg *.jpeg *.png")]
            )
        finally:
            root.destroy()
    except Exception as dialog_error:
        print(f"⚠️ Unable to open file picker ({dialog_error}).")
        selected_path = input("Enter full path to image file (or press Enter to skip): ").strip() or None

    if not selected_path:
        return None, None

    if not os.path.isfile(selected_path):
        print("⚠️ Provided cover art path does not exist. Skipping cover art.")
        return None, None

    mime = determine_mime_type(selected_path)
    print(f"\n✅ Using manual cover art: {selected_path}")
    return selected_path, mime

def confirm_tracklist(track_files: List[str]) -> List[Tuple[str, str]]:
    """Confirms track names and order, allowing tracks to be skipped."""
    print("\n--- TRACKLIST CONFIRMATION ---")
    confirmed_tracks = []
    
    for i, file_name in enumerate(track_files):
        current_name = os.path.splitext(file_name)[0]
        
        # 1. Ask if track should be included/renamed
        print(f"\n[{i+1}/{len(track_files)}] File: '{file_name}'")
        choice = input(
            f"  Include? (Y/n/rename): ").lower()
        
        if choice == 'n':
            print(f"  --> Skipping track: {file_name}")
            continue
        
        elif choice == 'rename' or choice == 'r':
            new_title = input(f"  Enter new title for track {i+1}: ")
            confirmed_tracks.append((file_name, new_title))
            
        else: # Default is 'Y' or Enter
            confirmed_tracks.append((file_name, current_name))
            
    print("\n--- FINAL TRACKLIST ---")
    for i, (file_name, title) in enumerate(confirmed_tracks):
        print(f"  {i+1}. {title} ({file_name})")
    
    confirm = input("Confirm final tracklist order? (Y/n): ").lower()
    if confirm != 'y' and confirm != '':
        print("Aborting. Please re-run the script to re-order/re-confirm.")
        return []
    
    return confirmed_tracks

def find_cover_art(directory: str) -> Tuple[Optional[str], Optional[str]]:
    """Finds or prompts for a cover art image."""
    images = [
        f for f in os.listdir(directory)
        if any(f.lower().endswith(ext) for ext in IMAGE_EXTS)
    ]

    if len(images) == 1:
        img_file = images[0]
        img_path = os.path.join(directory, img_file)
        mime = determine_mime_type(img_file)
        print(f"\n✅ Found cover art: {img_file}")
        return img_path, mime

    if len(images) > 1:
        print(f"\n⚠️ {len(images)} images detected. Please choose which one to embed:")
        for idx, name in enumerate(images, start=1):
            print(f"  {idx}. {name}")

        selection = input("Select image number or press Enter to use the first: ").strip()
        chosen_index = 0
        if selection.isdigit():
            numeric_choice = int(selection) - 1
            if 0 <= numeric_choice < len(images):
                chosen_index = numeric_choice
            else:
                print("⚠️ Invalid choice. Defaulting to the first image.")
        img_file = images[chosen_index]
        img_path = os.path.join(directory, img_file)
        mime = determine_mime_type(img_file)
        print(f"\n✅ Using cover art: {img_file}")
        return img_path, mime

    print("\n❌ No cover art image (*.jpg/*.png) detected in this folder.")
    return prompt_for_manual_cover_art()

def get_user_metadata(default_artist: str, default_album_title: str) -> Dict[str, str]:
    """Collects album metadata with quality-of-life defaults."""
    print("\n--- ALBUM METADATA ---")

    album_title = input(
        f"Enter Album Title (Default: {default_album_title}): "
    ).strip() or default_album_title

    artist_name = input(
        f"Enter Artist Name (Default: {default_artist}): "
    ).strip() or default_artist

    genre_tag = input(
        f"Enter Genre (Default: {DEFAULT_GENRE}): "
    ).strip() or DEFAULT_GENRE

    current_year = str(datetime.now().year)
    album_year = input(
        f"Enter Release Year (Default: {current_year}): "
    ).strip() or current_year

    return {
        'title': album_title,
        'artist': artist_name,
        'genre': genre_tag,
        'year': album_year
    }

def apply_tags(
    tracklist: List[Tuple[str, str]],
    album_meta: Dict[str, str],
    cover_art_path: Optional[str],
    mime_type: Optional[str]
) -> None:
    """Applies all gathered metadata and cover art to the audio files."""
    print("\n--- APPLYING TAGS ---")
    
    total_tracks = len(tracklist)
    embed_cover = bool(cover_art_path and mime_type)
    
    for i, (file_name, track_title) in enumerate(tracklist):
        track_number = i + 1
        file_path = os.path.join(os.getcwd(), file_name)
        
        try:
            audio = get_file_handler(file_path)
            if audio is None:
                print(f"  [SKIPPED] Cannot handle file type for {file_name}")
                continue

            print(f"  [{track_number}/{total_tracks}] Tagging: {track_title}...")
            
            # Use 'tags' property for FLAC/MP4, or ID3 directly for MP3
            
            if isinstance(audio, MP3):
                audio.delete() # Clear existing tags for clean application
                audio.add_tags()
                tags = audio.tags
                tags.add(TPE1(encoding=3, text=[album_meta['artist']]))
                tags.add(TIT2(encoding=3, text=[track_title]))
                tags.add(TALB(encoding=3, text=[album_meta['title']]))
                tags.add(TCON(encoding=3, text=[album_meta['genre']]))
                tags.add(TRCK(encoding=3, text=[f"{track_number}/{total_tracks}"]))
                tags.add(TDRC(encoding=3, text=[album_meta['year']]))
                
                if embed_cover:
                    with open(cover_art_path, 'rb') as f:
                        tags.add(APIC(
                            encoding=3,
                            mime=mime_type,
                            type=3, # 3 is Front Cover
                            desc=u'Cover',
                            data=f.read()
                        ))
            
            elif isinstance(audio, (FLAC, MP4)):
                if audio.tags is None:
                    audio.add_tags()
                tags = audio.tags
                tags['artist'] = [album_meta['artist']]
                tags['title'] = [track_title]
                tags['album'] = [album_meta['title']]
                tags['genre'] = [album_meta['genre']]
                tags['tracknumber'] = [str(track_number)]
                tags['date'] = [album_meta['year']]

                if isinstance(audio, FLAC) and embed_cover:
                    from mutagen.flac import Picture
                    image = Picture()
                    image.type = 3
                    image.mime = mime_type
                    with open(cover_art_path, 'rb') as f:
                        image.data = f.read()
                    audio.add_picture(image)
                
            audio.save()
            
        except error as e:
            print(f"  [ERROR] Mutagen error on {file_name}: {e}")
        except Exception as e:
            print(f"  [ERROR] Unexpected error on {file_name}: {e}")

def main():
    current_dir = os.getcwd()
    print("---------------------------------------")
    print("🚀 AEiOU'S ALBUM METADATA MANAGER v1.0")
    print(f"Current Directory: {current_dir}")
    print(f"Session Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("---------------------------------------")

    track_files = get_audio_files(current_dir)
    if not track_files:
        supported = ', '.join(AUDIO_EXTS)
        print(f"❌ No supported audio files ({supported}) found.")
        return

    # 1. Confirm Tracklist
    confirmed_tracklist = confirm_tracklist(track_files)
    if not confirmed_tracklist:
        return
    
    # Use 'Unknown Smuggler' as default artist from context
    default_artist = "Unknown Smuggler" 
    default_album_title = infer_album_title(current_dir)

    # 2. Gather Album Metadata
    album_meta = get_user_metadata(default_artist, default_album_title)

    # 3. Find Cover Art
    cover_art_path, mime_type = find_cover_art(current_dir)

    # 4. Apply Tags
    apply_tags(confirmed_tracklist, album_meta, cover_art_path, mime_type)
    
    print("\n--- SESSION SUMMARY ---")
    print(f"Album : {album_meta['title']}")
    print(f"Artist: {album_meta['artist']}")
    print(f"Genre : {album_meta['genre']}")
    print(f"Year  : {album_meta['year']}")
    if cover_art_path:
        print(f"Cover : {cover_art_path}")
    else:
        print("Cover : (not embedded)")

    print("\n✅ All tracks tagged successfully. Execution complete.")

if __name__ == "__main__":
    main()
