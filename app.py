import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import numpy as np
import tempfile
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ═══════════════════════════════════════════════════════════════
# Page Config
# ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="Thom's Riffs", page_icon="🎸", layout="centered")

# ═══════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Standard tuning: index 0 = low E (6th string) → index 5 = high e (1st string)
TUNING = [4, 9, 2, 7, 11, 4]  # E=4, A=9, D=2, G=7, B=11, E=4
STRING_NAMES = ['E (low)', 'A', 'D', 'G', 'B', 'e (high)']

# Krumhansl-Schmuckler key-finding profiles
MAJOR_PROFILE = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
MINOR_PROFILE = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

# Scale definitions (semitone intervals from root)
SCALES = {
    'Minor Pentatonic': {
        'intervals': [0, 3, 5, 7, 10],
        'description': 'The "rock & blues" scale — 5 notes, no wrong moves.',
        'vibe': 'Think Led Zeppelin, BB King, or any blues solo you\'ve ever heard.',
        'emoji': '🔥'
    },
    'Major Pentatonic': {
        'intervals': [0, 2, 4, 7, 9],
        'description': 'The "feel-good" scale — sweet, melodic, country-friendly.',
        'vibe': 'Think Allman Brothers, Grateful Dead, classic country licks.',
        'emoji': '🌅'
    },
    'Blues Scale': {
        'intervals': [0, 3, 5, 6, 7, 10],
        'description': 'Minor Pentatonic + one magic "blue note" for extra grit.',
        'vibe': 'That extra note adds the stank. Dig in and bend those strings.',
        'emoji': '😎'
    }
}

# Chord family definitions
MAJOR_CHORD_DEGREES = [(0, 'maj'), (2, 'min'), (4, 'min'), (5, 'maj'), (7, 'maj'), (9, 'min'), (11, 'dim')]
MAJOR_NUMERALS = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii°']

MINOR_CHORD_DEGREES = [(0, 'min'), (2, 'dim'), (3, 'maj'), (5, 'min'), (7, 'min'), (8, 'maj'), (10, 'maj')]
MINOR_NUMERALS = ['i', 'ii°', 'III', 'iv', 'v', 'VI', 'VII']

# Chords that are easy open shapes for beginners
EASY_OPEN_CHORDS = {'C', 'G', 'D', 'E', 'A', 'Am', 'Em', 'Dm', 'A7', 'D7', 'E7', 'G7', 'C7'}

# ═══════════════════════════════════════════════════════════════
# Song Database — curated beginner-friendly songs by key
# (song_title, artist, beginner_tip)
# ═══════════════════════════════════════════════════════════════
SONG_DB = {
    ('C', 'Major'): [
        ("Let It Be", "The Beatles", "C→G→Am→F — the most famous progression in music"),
        ("Stand By Me", "Ben E. King", "C→Am→F→G — timeless and dead simple"),
        ("No Woman No Cry", "Bob Marley", "Same four chords, laid-back strumming"),
        ("Good Riddance (Time of Your Life)", "Green Day", "Great for fingerpicking practice"),
    ],
    ('G', 'Major'): [
        ("Knockin' on Heaven's Door", "Bob Dylan", "G→D→Am→C, repeat forever"),
        ("Sweet Home Alabama", "Lynyrd Skynyrd", "Classic D→C→G riff everyone knows"),
        ("Wish You Were Here", "Pink Floyd", "Iconic intro, all open chords"),
        ("Wagon Wheel", "Old Crow Medicine Show", "The ultimate campfire song"),
    ],
    ('D', 'Major'): [
        ("Bad Moon Rising", "CCR", "D→A→G — three chords, whole song, done"),
        ("Free Fallin'", "Tom Petty", "Easy strumming, singalong guarantee"),
        ("Brown Eyed Girl", "Van Morrison", "Fun riff, all in open position"),
        ("Horse with No Name", "America", "Two chords. Seriously, just two."),
    ],
    ('A', 'Major'): [
        ("Wild Thing", "The Troggs", "A→D→E — possibly the simplest rock song ever"),
        ("La Bamba", "Ritchie Valens", "Three chords, great energy"),
        ("Margaritaville", "Jimmy Buffett", "Laid-back island strum"),
        ("Twist and Shout", "The Beatles", "A→D→E, pure energy"),
    ],
    ('E', 'Major'): [
        ("Mustang Sally", "Wilson Pickett", "Heavy E groove, fun to riff on"),
        ("Brown Sugar", "Rolling Stones", "E-based classic rock"),
        ("Johnny B. Goode", "Chuck Berry", "The riff that started it all"),
    ],
    ('F', 'Major'): [
        ("Let It Be (capo 5 in C shape)", "The Beatles", "Capo at fret 5, play C shapes"),
        ("Hey Jude", "The Beatles", "F→C→Bb→F — use a capo to simplify"),
    ],
    ('E', 'Minor'): [
        ("Heart of Gold", "Neil Young", "THE quintessential Em song"),
        ("Nothing Else Matters", "Metallica", "Beautiful open-string fingerpicking"),
        ("Hey Joe", "Jimi Hendrix", "Classic rock, great to noodle over"),
        ("Losing My Religion", "R.E.M.", "Arpeggiated picking, very recognizable"),
    ],
    ('A', 'Minor'): [
        ("House of the Rising Sun", "The Animals", "Classic Am arpeggio — everyone should know this"),
        ("All Along the Watchtower", "Bob Dylan", "Am→G→F→G, powerful and simple"),
        ("Stairway to Heaven (intro)", "Led Zeppelin", "The Am fingerpicking intro everyone tries"),
        ("Californication", "Red Hot Chili Peppers", "Am-based verse, very recognizable"),
    ],
    ('D', 'Minor'): [
        ("Riders on the Storm", "The Doors", "Moody Dm groove"),
        ("Another Brick in the Wall", "Pink Floyd", "Iconic Dm riff"),
        ("Sultans of Swing", "Dire Straits", "Stretching, but great to strum along"),
    ],
    ('B', 'Minor'): [
        ("Hotel California", "Eagles", "Capo trick: capo 2, play Am shapes"),
        ("Dust in the Wind", "Kansas", "Fingerpicking workout"),
    ],
    ('G', 'Minor'): [
        ("Black Magic Woman", "Santana/Fleetwood Mac", "Great minor key jam feel"),
    ],
    ('C', 'Minor'): [
        ("The Thrill Is Gone", "BB King", "Classic blues in Cm territory"),
    ],
}

DEFAULT_SONGS = {
    'Major': [("💡 Capo trick", "", "Slap a capo on and shift into G, C, D, or A — tons of beginner songs in those keys")],
    'Minor': [("💡 Capo trick", "", "Slap a capo on and shift into Am or Em — the friendliest minor keys for guitar")],
}


# ═══════════════════════════════════════════════════════════════
# Key Detection (librosa + Krumhansl-Schmuckler)
# ═══════════════════════════════════════════════════════════════
def detect_key(audio_bytes, filename):
    """Analyze uploaded audio → returns (key_name, mode, confidence_score)."""
    import librosa

    suffix = os.path.splitext(filename)[1] if filename else '.wav'
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        y, sr = librosa.load(tmp_path, sr=22050, mono=True)

        # Compute chroma features (pitch class energy over time)
        chromagram = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_vals = np.mean(chromagram, axis=1)
        chroma_vals = chroma_vals / (np.max(chroma_vals) + 1e-8)

        best_corr = -2
        best_key_idx = 0
        best_mode = 'Major'

        for i in range(12):
            rotated = np.roll(chroma_vals, -i)
            maj_corr = np.corrcoef(rotated, MAJOR_PROFILE)[0, 1]
            min_corr = np.corrcoef(rotated, MINOR_PROFILE)[0, 1]

            if maj_corr > best_corr:
                best_corr = maj_corr
                best_key_idx = i
                best_mode = 'Major'
            if min_corr > best_corr:
                best_corr = min_corr
                best_key_idx = i
                best_mode = 'Minor'

        return NOTES[best_key_idx], best_mode, best_corr
    finally:
        os.unlink(tmp_path)


# ═══════════════════════════════════════════════════════════════
# Music Theory Helpers
# ═══════════════════════════════════════════════════════════════
def get_scale_notes(root, intervals):
    root_idx = NOTES.index(root)
    return [NOTES[(root_idx + iv) % 12] for iv in intervals]


def get_chord_family(root, mode):
    root_idx = NOTES.index(root)
    degrees = MAJOR_CHORD_DEGREES if mode == 'Major' else MINOR_CHORD_DEGREES
    numerals = MAJOR_NUMERALS if mode == 'Major' else MINOR_NUMERALS

    chords = []
    for (interval, quality), numeral in zip(degrees, numerals):
        note = NOTES[(root_idx + interval) % 12]
        if quality == 'min':
            chord_name = f"{note}m"
        elif quality == 'dim':
            chord_name = f"{note}dim"
        else:
            chord_name = note
        chords.append((chord_name, numeral))
    return chords


# ═══════════════════════════════════════════════════════════════
# Fretboard Visualization (matplotlib)
# ═══════════════════════════════════════════════════════════════
def draw_fretboard(root, scale_notes, max_fret=12):
    fig, ax = plt.subplots(1, 1, figsize=(14, 3.5), dpi=100)

    n_strings = 6
    bg = '#111122'
    board = '#1e1e3a'
    root_col = '#e63946'
    note_col = '#4895ef'

    fig.patch.set_facecolor(bg)
    ax.set_facecolor(board)

    # Draw frets
    for f in range(max_fret + 1):
        lw = 3.5 if f == 0 else 0.8
        color = '#dddddd' if f == 0 else '#555577'
        ax.axvline(x=f, color=color, linewidth=lw, zorder=1)

    # Draw strings (low E at bottom = y=0, high e at top = y=5)
    for s in range(n_strings):
        thickness = 2.0 - (s * 0.25)
        ax.axhline(y=s, color='#aaaaaa', linewidth=thickness, zorder=1, alpha=0.5)

    # Fret position markers (inlays)
    for m in [3, 5, 7, 9]:
        if m <= max_fret:
            ax.plot(m - 0.5, -0.7, 'o', color='#333355', markersize=7, zorder=0)
    if 12 <= max_fret:
        ax.plot(11.5, -0.5, 'o', color='#333355', markersize=6, zorder=0)
        ax.plot(11.5, -0.9, 'o', color='#333355', markersize=6, zorder=0)

    # Place scale notes
    for string_idx in range(n_strings):
        open_note = TUNING[string_idx]
        for fret in range(max_fret + 1):
            note_name = NOTES[(open_note + fret) % 12]
            if note_name in scale_notes:
                x = fret - 0.5 if fret > 0 else -0.05
                y = string_idx  # low E = 0 (bottom), high e = 5 (top)

                is_root = (note_name == root)
                color = root_col if is_root else note_col
                radius = 0.32 if is_root else 0.26

                circle = plt.Circle((x, y), radius, color=color, zorder=3, ec='white', lw=0.5)
                ax.add_patch(circle)
                ax.text(x, y, note_name, ha='center', va='center',
                        fontsize=8, fontweight='bold', color='white', zorder=4)

    # String labels (left side)
    for s in range(n_strings):
        ax.text(-0.7, s, STRING_NAMES[s], ha='right', va='center',
                fontsize=9, color='#9999bb', fontweight='bold')

    # Fret numbers (bottom)
    for f in range(1, max_fret + 1):
        ax.text(f - 0.5, -1.2, str(f), ha='center', va='center',
                fontsize=8, color='#9999bb')

    ax.set_xlim(-1.1, max_fret + 0.3)
    ax.set_ylim(-1.6, n_strings - 0.3)
    ax.set_aspect('equal')
    ax.axis('off')

    root_patch = mpatches.Patch(color=root_col, label=f'Root ({root})')
    note_patch = mpatches.Patch(color=note_col, label='Scale note')
    ax.legend(handles=[root_patch, note_patch], loc='upper right',
              fontsize=8, facecolor=bg, edgecolor='#444466', labelcolor='#cccccc')

    plt.tight_layout(pad=0.5)
    return fig


# ═══════════════════════════════════════════════════════════════
# Main App
# ═══════════════════════════════════════════════════════════════
def main():
    # Custom styling
    st.markdown("""
    <style>
        .big-key {
            font-size: 2.8rem;
            font-weight: 800;
            text-align: center;
            padding: 24px 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 16px;
            color: #e63946;
            margin: 16px 0 8px 0;
            letter-spacing: 2px;
        }
        .chord-pill {
            display: inline-block;
            background: #16213e;
            color: #ffffff;
            padding: 8px 14px;
            border-radius: 8px;
            margin: 3px;
            font-weight: 600;
            font-size: 0.95rem;
        }
        .chord-pill.easy { border: 2px solid #2ecc71; }
        .chord-pill.hard { border: 1px solid #555577; opacity: 0.8; }
    </style>
    """, unsafe_allow_html=True)

    # ── Birthday Splash (first visit EVER, not every session) ──
    # Uses browser localStorage so it persists across visits
    if 'show_splash' not in st.session_state:
        visited = streamlit_js_eval(
            js_expressions="localStorage.getItem('thoms_riffs_visited') === 'true' ? 'yes' : 'no'"
        )
        if visited is None:
            # JS still loading on first render — wait
            st.empty()
            return
        st.session_state.show_splash = (visited == 'no')

    if st.session_state.show_splash:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            border: 2px solid #e63946;
            border-radius: 20px;
            padding: 40px 30px;
            text-align: center;
            margin-bottom: 24px;
        ">
            <div style="font-size: 3rem; margin-bottom: 12px;">🎸🎂🎸</div>
            <div style="font-size: 2.2rem; font-weight: 800; color: #e63946; margin-bottom: 8px;">
                Happy Birthday, Thom!
            </div>
            <div style="font-size: 1.1rem; color: #ccccdd; line-height: 1.6;">
                This one's for you.<br>
                Upload a riff, find your key, and discover what to play next.<br>
                No theory homework required.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎸 Let's play", type="primary", use_container_width=True):
            streamlit_js_eval(js_expressions="localStorage.setItem('thoms_riffs_visited', 'true')")
            st.session_state.show_splash = False
            st.rerun()
        return  # Don't show the rest of the app until he clicks through

    # ── Header ──
    st.title("🎸 Thom's Riffs")
    st.caption("Upload a riff → get your key, scales, chords, and songs to jam with.")
    st.markdown("---")

    # ── Input ──
    detected_key = None
    detected_mode = None
    confidence = None

    tab_upload, tab_pick = st.tabs(["🎙️ Upload a Riff", "🎹 Just Pick a Key"])

    with tab_upload:
        st.markdown("Record yourself playing on your phone and upload the file here.  \n"
                     "Works best with **just guitar** — no TV or music in the background.")
        audio_file = st.file_uploader("Drop your audio here", type=['wav', 'mp3', 'm4a', 'ogg', 'flac'])

        if audio_file is not None:
            st.audio(audio_file)
            with st.spinner("Listening..."):
                try:
                    key, mode, conf = detect_key(audio_file.getvalue(), audio_file.name)
                    detected_key = key
                    detected_mode = mode
                    confidence = conf
                except Exception as e:
                    st.error(f"Couldn't read that file — try a .wav or .mp3 instead.\n\nDetails: {e}")

    with tab_pick:
        st.markdown("Don't have a recording? No problem — just tell me what key you're in.")
        col1, col2 = st.columns(2)
        with col1:
            manual_key = st.selectbox("Root note", NOTES, index=7)  # default G
        with col2:
            manual_mode = st.selectbox("Feel", ["Major", "Minor"],
                                        help="Major = happy/bright. Minor = moody/bluesy.")
        if st.button("Show me the goods →", type="primary", use_container_width=True):
            detected_key = manual_key
            detected_mode = manual_mode
            confidence = 1.0  # manual = full confidence

    # ── Results ──
    if detected_key is None or detected_mode is None:
        return

    st.markdown("---")

    # Key display
    st.markdown(f'<div class="big-key">{detected_key} {detected_mode}</div>', unsafe_allow_html=True)

    if confidence is not None and confidence < 1.0:
        if confidence > 0.65:
            st.caption("✅ Confident detection")
        elif confidence > 0.4:
            st.caption("⚠️ Decent guess — if it sounds off, try the 'Pick a Key' tab instead")
        else:
            st.caption("❌ Low confidence — noisy recording? Use 'Pick a Key' for a sure thing")

    # ── Chord Family ──
    st.markdown("### 🏠 Chord Family")
    st.markdown("These chords *belong together* in this key. Mix and match freely.")

    chords = get_chord_family(detected_key, detected_mode)
    chord_html = ""
    for chord_name, numeral in chords:
        is_easy = chord_name in EASY_OPEN_CHORDS
        css_class = "easy" if is_easy else "hard"
        badge = " ⭐" if is_easy else ""
        chord_html += f'<span class="chord-pill {css_class}">{numeral}: {chord_name}{badge}</span> '

    st.markdown(chord_html, unsafe_allow_html=True)
    st.caption("⭐ = easy open chord shape you probably already know")

    # ── Scales ──
    st.markdown("### 🎯 Scales to Play")

    if detected_mode == 'Minor':
        default_scale = 'Minor Pentatonic'
    else:
        default_scale = 'Major Pentatonic'

    scale_choice = st.radio(
        "Pick your flavor:",
        list(SCALES.keys()),
        index=list(SCALES.keys()).index(default_scale),
        horizontal=True
    )

    info = SCALES[scale_choice]
    scale_notes = get_scale_notes(detected_key, info['intervals'])

    st.markdown(f"**{info['emoji']} {info['description']}**")
    st.markdown(f"*{info['vibe']}*")

    # Show notes as big readable pills
    notes_html = " → ".join([f"**{n}**" for n in scale_notes])
    st.markdown(f"Notes: {notes_html}")

    # ── Fretboard ──
    st.markdown("### 🎸 Fretboard Map")
    st.markdown("**Red** = root note (home base) &nbsp;|&nbsp; **Blue** = scale notes (safe zone)  \n"
                "Stay on the dots — you literally can't hit a wrong note.")

    fret_range = st.radio("Show frets:", ["0–7 (beginner zone)", "0–12 (full neck)"],
                          horizontal=True, index=0)
    max_fret = 7 if "0–7" in fret_range else 12

    fig = draw_fretboard(detected_key, scale_notes, max_fret=max_fret)
    st.pyplot(fig)
    plt.close(fig)

    # ── Songs ──
    st.markdown("### 🎵 Songs to Jam With")
    st.markdown(f"These songs live in **{detected_key} {detected_mode}**. "
                f"Fire one up on YouTube and noodle along with the scale above.")

    song_key = (detected_key, detected_mode)
    songs = SONG_DB.get(song_key, DEFAULT_SONGS.get(detected_mode, []))

    for title, artist, tip in songs:
        if artist:
            st.markdown(f"**{title}** — {artist}")
            st.caption(f"_{tip}_")
            query = f"{title} {artist} guitar play along".replace(' ', '+')
            st.markdown(f"[▶ Find on YouTube](https://www.youtube.com/results?search_query={query})")
        else:
            st.markdown(f"**{title}**")
            st.caption(f"_{tip}_")
        st.markdown("")

    # ── Footer ──
    st.markdown("---")
    st.markdown("<div style='text-align:center; color:#666; font-size:0.85rem;'>"
                "Built with ❤️ for Thom, by Kieran</div>", unsafe_allow_html=True)


if __name__ == '__main__':
    main()
