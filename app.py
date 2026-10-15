
import io
import os
import textwrap
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(
    page_title="Shaadi Nimantran Generator",
    page_icon="💍",
    layout="centered"
)

st.title("💍 Shaadi Nimantran Generator")
st.write("Create a beautiful wedding invitation — completely free!")

religion = st.selectbox(
    "Select Religion",
    ["Hindu", "Muslim", "Christian", "Sikh",
     "Jain", "Buddhist", "Other"]
)

language = st.selectbox(
    "Select Language", ["English", "Hindi"]
)

style = st.selectbox(
    "Card Style",
    ["Royal Red & Gold", "Elegant Green",
     "Classic White", "Royal Purple"]
)

bride = st.text_input("Bride's Name")
groom = st.text_input("Groom's Name")
family = st.text_input("Family Names")
wedding_date = st.date_input("Wedding Date")
wedding_time = st.text_input("Wedding Time", "7:00 PM")
venue = st.text_input("Wedding Venue")
message = st.text_area("Additional Message (Optional)")


def create_invitation():
    templates = {
        "Hindu": {
            "English": (
                "Shri Ganeshaya Namah\n"
                "WEDDING INVITATION\n"
                f"{groom} & {bride}\n"
                "Request the pleasure of your presence."
            ),
            "Hindi": (
                "॥ श्री गणेशाय नमः ॥\n"
                "शुभ विवाह\n"
                f"{groom} एवं {bride}\n"
                "आप सपरिवार सादर आमंत्रित हैं।"
            )
        },
        "Muslim": {
            "English": (
                "NIKAH INVITATION\n"
                f"{groom} & {bride}\n"
                "Join us to celebrate our Nikah."
            ),
            "Hindi": (
                "निकाह का निमंत्रण\n"
                f"{groom} एवं {bride}\n"
                "आपकी उपस्थिति सादर प्रार्थनीय है।"
            )
        },
        "Christian": {
            "English": (
                "WEDDING INVITATION\n"
                f"{groom} & {bride}\n"
                "Joyfully invite you to their wedding."
            ),
            "Hindi": (
                "विवाह समारोह का निमंत्रण\n"
                f"{groom} एवं {bride}\n"
                "सप्रेम आमंत्रित हैं।"
            )
        },
        "Sikh": {
            "English": (
                "ANAND KARAJ INVITATION\n"
                f"{groom} & {bride}\n"
                "With our families, we invite you."
            ),
            "Hindi": (
                "आनंद कारज का निमंत्रण\n"
                f"{groom} एवं {bride}\n"
                "आप सादर आमंत्रित हैं।"
            )
        },
        "Jain": {
            "English": (
                "WEDDING INVITATION\n"
                f"{groom} & {bride}\n"
                "Please join us for our wedding."
            ),
            "Hindi": (
                "शुभ विवाह का निमंत्रण\n"
                f"{groom} एवं {bride}\n"
                "आप सपरिवार आमंत्रित हैं।"
            )
        },
        "Buddhist": {
            "English": (
                "WEDDING INVITATION\n"
                f"{groom} & {bride}\n"
                "Celebrate our special day with us."
            ),
            "Hindi": (
                "विवाह समारोह का निमंत्रण\n"
                f"{groom} एवं {bride}\n"
                "आप सादर आमंत्रित हैं।"
            )
        },
        "Other": {
            "English": (
                "WEDDING INVITATION\n"
                f"{groom} & {bride}\n"
                "You are warmly invited to celebrate."
            ),
            "Hindi": (
                "विवाह समारोह का निमंत्रण\n"
                f"{groom} एवं {bride}\n"
                "आप सादर आमंत्रित हैं।"
            )
        }
    }

    invitation = templates[religion][language]

    if family.strip():
        invitation += f"\nWith love from {family}"

    invitation += (
        f"\nDate: {wedding_date.strftime('%d-%m-%Y')}"
        f"\nTime: {wedding_time}"
        f"\nVenue: {venue}"
    )

    if message.strip():
        invitation += f"\n{message.strip()}"

    return invitation


def get_font(size, language):
    candidates = (
        [
            "fonts/NotoSansDevanagari-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
            "C:/Windows/Fonts/Nirmala.ttf"
        ]
        if language == "Hindi"
        else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/arial.ttf"
        ]
    )

    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                pass

    return ImageFont.load_default()


def make_card(invitation):
    colors = {
        "Royal Red & Gold": ("#720D24", "#E8C878"),
        "Elegant Green": ("#064E3B", "#D9C17A"),
        "Classic White": ("#FFFCF4", "#A98746"),
        "Royal Purple": ("#39224F", "#E3C779")
    }

    bg, gold = colors[style]
    img = Image.new("RGB", (900, 1200), bg)
    draw = ImageDraw.Draw(img)

    draw.rectangle((25, 25, 875, 1175), outline=gold, width=5)
    draw.rectangle((43, 43, 857, 1157), outline=gold, width=2)

    title_font = get_font(42, language)
    body_font = get_font(28, language)
    small_font = get_font(23, language)

    def centered(text, y, font, fill=None):
        fill = fill or gold
        box = draw.textbbox((0, 0), text, font=font)
        width = box[2] - box[0]
        draw.text(((900 - width) / 2, y), text,
                  font=font, fill=fill)

    heading = (
        "शुभ विवाह" if language == "Hindi"
        else "WEDDING INVITATION"
    )
    centered("✦", 65, title_font)
    centered(heading, 115, title_font)

    y = 220
    max_width = 31 if language == "Hindi" else 36

    for line in invitation.splitlines():
        wrapped_lines = textwrap.wrap(line, width=max_width) or [""]
        for wrapped in wrapped_lines:
            if y > 850:
                break
            centered(wrapped, y, body_font)
            y += 48

    centered("With love and blessings", 930, small_font)

    output = io.BytesIO()
    img.save(output, format="PNG")
    return img


if st.button("✨ Generate Invitation", type="primary"):
    if not bride.strip() or not groom.strip() or not venue.strip():
        st.error("Please enter the bride's name, groom's name and venue.")
    else:
        with st.spinner("Creating your invitation..."):
            wording = create_invitation()
            card = make_card(wording)

        st.subheader("Invitation Preview")
        st.image(card, use_container_width=True)

        st.subheader("Invitation Text")
        st.text(wording)

        output = io.BytesIO()
        card.save(output, format="PNG")

        st.download_button(
            "⬇️ Download Invitation Card (PNG)",
            data=output.getvalue(),
            file_name="shaadi_nimantran.png",
            mime="image/png"
        )
