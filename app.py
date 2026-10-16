
import os
import io
import textwrap
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI

# ---------------- APP CONFIG ----------------
st.set_page_config(
    page_title="AI Shaadi Nimantran",
    page_icon="💌",
    layout="wide",
)

MODEL = "openai/gpt-oss-20b"
BASE_URL = "https://integrate.api.nvidia.com/v1"

THEMES = {
    "Royal Red & Gold": {
        "background": "#720D24",
        "gold": "#E8C878",
        "paper": "#FFF8E8",
    },
    "Elegant Green": {
        "background": "#064E3B",
        "gold": "#D9C17A",
        "paper": "#F5F5E8",
    },
    "Classic White": {
        "background": "#FFFCF4",
        "gold": "#A98746",
        "paper": "#FFF8E8",
    },
    "Royal Purple": {
        "background": "#39224F",
        "gold": "#E3C779",
        "paper": "#FFF8F0",
    },
}

TEMPLATES = {
    "Hindu": {
        "English": (
            "With the blessings of Lord Ganesha, our families "
            "cordially invite you to celebrate the wedding of "
            "{bride} and {groom}. Date: {date}. Time: {time}. "
            "Venue: {venue}. Your presence will make our "
            "celebration truly special."
        ),
        "Hindi": (
            "श्री गणेश जी की कृपा से, हमारे परिवार आपको "
            "{bride} एवं {groom} के शुभ विवाह में सादर आमंत्रित "
            "करते हैं। दिनांक: {date}। समय: {time}। "
            "स्थान: {venue}। आपकी उपस्थिति हमारे लिए "
            "सौभाग्य की बात होगी।"
        ),
    },
    "Muslim": {
        "English": (
            "Bismillah-ir-Rahman-ir-Rahim. With the blessings "
            "of Allah, we invite you to the Nikah ceremony of "
            "{bride} and {groom}. Date: {date}. Time: {time}. "
            "Venue: {venue}. Please join us with your duas."
        ),
        "Hindi": (
            "बिस्मिल्लाहिर्रहमानिर्रहीम। अल्लाह की रहमत से "
            "आपको {bride} एवं {groom} के निकाह में सादर "
            "आमंत्रित करते हैं। दिनांक: {date}। समय: {time}। "
            "स्थान: {venue}। अपनी दुआओं से नवाज़ें।"
        ),
    },
    "Christian": {
        "English": (
            "With God's blessings and joyful hearts, we invite "
            "you to celebrate the wedding of {bride} and "
            "{groom}. Date: {date}. Time: {time}. "
            "Venue: {venue}. Your presence and prayers "
            "will make this day more meaningful."
        ),
        "Hindi": (
            "परमेश्वर के आशीर्वाद और हर्षित हृदय से हम आपको "
            "{bride} एवं {groom} के विवाह समारोह में आमंत्रित "
            "करते हैं। दिनांक: {date}। समय: {time}। "
            "स्थान: {venue}। आपकी उपस्थिति हमारे लिए "
            "आशीर्वाद होगी।"
        ),
    },
    "Sikh": {
        "English": (
            "With the blessings of Waheguru, our families "
            "warmly invite you to the wedding of {bride} and "
            "{groom}. Date: {date}. Time: {time}. "
            "Venue: {venue}. Please join us in this joyful "
            "celebration."
        ),
        "Hindi": (
            "वाहेगुरु जी की कृपा से, हमारे परिवार आपको "
            "{bride} एवं {groom} के शुभ विवाह में सादर "
            "आमंत्रित करते हैं। दिनांक: {date}। समय: {time}। "
            "स्थान: {venue}। कृपया पधारकर हमें अनुगृहीत करें।"
        ),
    },
    "Jain": {
        "English": (
            "With the blessings of the Almighty and our elders, "
            "we invite you to the wedding of {bride} and "
            "{groom}. Date: {date}. Time: {time}. "
            "Venue: {venue}. Kindly join our families "
            "in this auspicious celebration."
        ),
        "Hindi": (
            "परमात्मा एवं बड़ों के आशीर्वाद से, हम आपको "
            "{bride} एवं {groom} के शुभ विवाह में सादर "
            "आमंत्रित करते हैं। दिनांक: {date}। समय: {time}। "
            "स्थान: {venue}। कृपया पधारकर शुभ अवसर की "
            "शोभा बढ़ाएँ।"
        ),
    },
    "Buddhist": {
        "English": (
            "With peace, loving-kindness, and the blessings "
            "of our elders, we invite you to celebrate the "
            "wedding of {bride} and {groom}. Date: {date}. "
            "Time: {time}. Venue: {venue}. "
            "Your presence will bring us happiness."
        ),
        "Hindi": (
            "शांति, मैत्री और बड़ों के आशीर्वाद के साथ हम आपको "
            "{bride} एवं {groom} के विवाह समारोह में आमंत्रित "
            "करते हैं। दिनांक: {date}। समय: {time}। "
            "स्थान: {venue}। आपकी उपस्थिति हमारे लिए "
            "हर्ष का विषय होगी।"
        ),
    },
    "Other": {
        "English": (
            "With love and happiness, our families invite you "
            "to celebrate the wedding of {bride} and {groom}. "
            "Date: {date}. Time: {time}. Venue: {venue}. "
            "We look forward to celebrating with you."
        ),
        "Hindi": (
            "हर्ष एवं उल्लास के साथ, हम आपको {bride} एवं "
            "{groom} के शुभ विवाह में सादर आमंत्रित करते हैं। "
            "दिनांक: {date}। समय: {time}। स्थान: {venue}। "
            "कृपया पधारकर हमें अनुगृहीत करें।"
        ),
    },
}


# ---------------- NVIDIA API ----------------
def get_api_key():
    key = os.getenv("NVIDIA_API_KEY", "").strip()

    if not key:
        try:
            key = st.secrets.get("NVIDIA_API_KEY", "").strip()
        except Exception:
            key = ""

    return key


def generate_invitation(prompt):
    key = get_api_key()

    if not key:
        return None, "NVIDIA_API_KEY is missing."

    try:
        client = OpenAI(
            base_url=BASE_URL,
            api_key=key,
            timeout=60.0,
        )

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You write beautiful, respectful Indian "
                        "wedding invitation cards. Follow the "
                        "requested religion and language. Include "
                        "the supplied names, date, time and venue "
                        "exactly. Use elegant wording and short "
                        "paragraphs. Return only the invitation "
                        "text, without markdown or explanations."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        result = response.choices[0].message.content

        if not result or not result.strip():
            return None, "The AI returned an empty response."

        return result.strip(), None

    except Exception as exc:
        # Display the real error to help debug the API.
        return None, f"{type(exc).__name__}: {exc}"


# ---------------- FALLBACK TEMPLATE ----------------
def make_fallback(religion, language, bride, groom, date, time, venue):
    template = TEMPLATES[religion][language]

    return template.format(
        bride=bride,
        groom=groom,
        date=date,
        time=time,
        venue=venue,
    )


# ---------------- FONT HELPERS ----------------
def get_font(size, bold=False, language="English"):
    root = Path(__file__).parent

    candidates = []

    if language == "Hindi":
        candidates += [
            root / "fonts" / "NotoSansDevanagari-Bold.ttf"
            if bold else root / "fonts" / "NotoSansDevanagari-Regular.ttf",
            Path("C:/Windows/Fonts/NirmalaB.ttf")
            if bold else Path("C:/Windows/Fonts/Nirmala.ttf"),
        ]

    candidates += [
        Path("C:/Windows/Fonts/georgiab.ttf")
        if bold else Path("C:/Windows/Fonts/georgia.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf")
        if bold else Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
    ]

    for path in candidates:
        try:
            if path.exists():
                return ImageFont.truetype(str(path), size)
        except OSError:
            pass

    return ImageFont.load_default()


# ---------------- CREATE INVITATION PNG ----------------
def create_card(
    bride,
    groom,
    date,
    time,
    venue,
    religion,
    language,
    theme_name,
    invitation_text,
):
    theme = THEMES[theme_name]
    width, height = 1000, 1400

    image = Image.new(
        "RGB",
        (width, height),
        theme["background"],
    )
    draw = ImageDraw.Draw(image)

    margin = 45
    draw.rounded_rectangle(
        (margin, margin, width - margin, height - margin),
        radius=35,
        fill=theme["paper"],
        outline=theme["gold"],
        width=8,
    )

    draw.rounded_rectangle(
        (margin + 18, margin + 18, width - margin - 18, height - margin - 18),
        radius=25,
        outline=theme["gold"],
        width=2,
    )

    def centered(text, y, font, fill):
        box = draw.textbbox((0, 0), text, font=font)
        text_width = box[2] - box[0]
        draw.text(
            ((width - text_width) // 2, y),
            text,
            font=font,
            fill=fill,
        )

    centered(
        "WEDDING INVITATION" if language == "English" else "शुभ विवाह",
        105,
        get_font(44, True, language),
        theme["gold"],
    )

    centered(
        "Together with our families" if language == "English"
        else "सपरिवार सादर आमंत्रण",
        185,
        get_font(27, False, language),
        theme["background"],
    )

    centered(
        bride,
        290,
        get_font(48, True, language),
        theme["background"],
    )

    centered(
        "&",
        365,
        get_font(40, False, language),
        theme["gold"],
    )

    centered(
        groom,
        435,
        get_font(48, True, language),
        theme["background"],
    )

    draw.line(
        (200, 520, 800, 520),
        fill=theme["gold"],
        width=3,
    )

    centered(
        date,
        555,
        get_font(31, True, language),
        theme["background"],
    )

    centered(
        time,
        610,
        get_font(27, False, language),
        theme["background"],
    )

    centered(
        venue,
        665,
        get_font(25, False, language),
        theme["background"],
    )

    # Draw invitation wording with approximate character wrapping.
    y = 755
    font = get_font(25, False, language)
    max_chars = 43 if language == "Hindi" else 49

    paragraphs = invitation_text.splitlines()

    for paragraph in paragraphs:
        if not paragraph.strip():
            y += 15
            continue

        lines = textwrap.wrap(
            paragraph,
            width=max_chars,
            break_long_words=True,
        ) or [""]

        for line in lines:
            if y > 1190:
                break

            box = draw.textbbox((0, 0), line, font=font)
            line_width = box[2] - box[0]

            draw.text(
                ((width - line_width) // 2, y),
                line,
                font=font,
                fill=theme["background"],
            )
            y += 39

        y += 12

    footer = (
        "Your presence is our blessing"
        if language == "English"
        else "आपकी उपस्थिति हमारा सौभाग्य है"
    )

    centered(
        footer,
        1240,
        get_font(25, True, language),
        theme["gold"],
    )

    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)

    return output.getvalue()


# ---------------- STREAMLIT UI ----------------
st.title("💌 AI Shaadi Nimantran Generator")
st.write(
    "Create a personalized wedding invitation in Hindi or English "
    "and download it as a PNG image."
)

with st.sidebar:
    st.header("Invitation Settings")

    religion = st.selectbox(
        "Religion / Tradition",
        ["Hindu", "Muslim", "Christian", "Sikh", "Jain", "Buddhist", "Other"],
    )

    language = st.selectbox(
        "Language",
        ["Hindi", "English"],
    )

    theme_name = st.selectbox(
        "Card Design",
        list(THEMES.keys()),
    )

    st.caption("AI text generation uses the NVIDIA API.")
    st.caption("Do not put your API key directly in app.py.")

with st.form("invitation_form"):
    col1, col2 = st.columns(2)

    with col1:
        bride = st.text_input("Bride's Name")
        date = st.text_input("Wedding Date", placeholder="25 November 2026")

    with col2:
        groom = st.text_input("Groom's Name")
        time = st.text_input("Wedding Time", placeholder="7:00 PM onwards")

    venue = st.text_input(
        "Venue / Address",
        placeholder="Wedding Palace, Lucknow",
    )

    extra = st.text_area(
        "Additional Message (optional)",
        placeholder="Family names, reception details, RSVP, etc.",
    )

    submitted = st.form_submit_button(
        "✨ Generate Invitation",
        use_container_width=True,
    )

if submitted:
    if not all([bride.strip(), groom.strip(), date.strip(),
                time.strip(), venue.strip()]):
        st.error("Please fill in the bride, groom, date, time and venue.")
        st.stop()

    prompt = f"""
Create an elegant wedding invitation.

Religion/tradition: {religion}
Language: {language}
Bride: {bride}
Groom: {groom}
Date: {date}
Time: {time}
Venue: {venue}
Additional message: {extra or "None"}

Write a polished invitation suitable for a wedding card.
Use only the requested language, preserve names and event details,
and keep the wording concise enough to fit on a card.
"""

    with st.spinner("Generating your wedding invitation..."):
        ai_text, error = generate_invitation(prompt)

    if ai_text:
        invitation_text = ai_text
        st.success("AI invitation generated successfully!")
    else:
        invitation_text = make_fallback(
            religion,
            language,
            bride,
            groom,
            date,
            time,
            venue,
        )

        st.warning(
            "AI generation failed. A built-in invitation template "
            "is being used instead."
        )

        with st.expander("Show API error details"):
            st.code(error or "Unknown error")
            st.markdown(
                "Check your API key, model access and usage limits. "
                "If the error is 401, verify the key; if 403, check "
                "account permissions; if 429, check rate limits."
            )

    if extra.strip():
        invitation_text += "\n\n" + extra.strip()

    st.subheader("Invitation Wording")
    st.text_area(
        "Edit your invitation text",
        value=invitation_text,
        height=220,
        key="editable_invitation",
    )

    card_text = st.session_state.editable_invitation

    try:
        png_bytes = create_card(
            bride=bride.strip(),
            groom=groom.strip(),
            date=date.strip(),
            time=time.strip(),
            venue=venue.strip(),
            religion=religion,
            language=language,
            theme_name=theme_name,
            invitation_text=card_text,
        )

        st.subheader("Card Preview")
        st.image(png_bytes, caption="Your wedding invitation")

        st.download_button(
            "⬇️ Download Invitation PNG",
            data=png_bytes,
            file_name="shaadi_nimantran.png",
            mime="image/png",
            use_container_width=True,
        )

    except Exception as exc:
        st.error(f"Could not create the card image: {exc}")

st.divider()
st.caption(
    "AI wording requires NVIDIA API access. Built-in templates "
    "remain available when the API is unavailable."
)
