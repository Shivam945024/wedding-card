```python
import os
import base64
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="AI Wedding Card Generator",
    page_icon="💍",
    layout="centered"
)

st.title("💍 AI Wedding Invitation Generator")
st.write("Create a beautiful wedding invitation using AI.")

with st.form("wedding_form"):
    groom = st.text_input("Groom's Name")
    bride = st.text_input("Bride's Name")
    date = st.text_input("Wedding Date")
    venue = st.text_input("Wedding Venue")

    theme = st.selectbox(
        "Choose Card Theme",
        ["Royal Indian", "Floral", "Traditional", "Modern"]
    )

    language = st.selectbox(
        "Invitation Language",
        ["English", "Hindi"]
    )

    submitted = st.form_submit_button("Generate Wedding Card")

if submitted:
    if not all([
        groom.strip(),
        bride.strip(),
        date.strip(),
        venue.strip()
    ]):
        st.warning("Please fill in all fields.")
    else:
    api_key = os.getenv("OPENAI_API_KEY")")

        if not api_key:
            st.error("Set your OPENAI_API_KEY environment variable.")
        else:
            try:
                client = OpenAI(api_key=api_key)

                prompt = f"""
                Design a beautiful printable Indian wedding invitation.
                Theme: {theme}
                Groom: {groom}
                Bride: {bride}
                Wedding date: {date}
                Venue: {venue}
                Language: {language}

                Create an elegant portrait wedding card with
                decorative borders, tasteful floral ornaments,
                premium typography, and balanced spacing.
                Include the supplied names, date, and venue.
                """

                with st.spinner("Generating your wedding card..."):
                    result = client.images.generate(
                        model="gpt-image-1",
                        prompt=prompt,
                        size="1024x1536"
                    )

                image_data = base64.b64decode(
                    result.data[0].b64_json
                )

                st.image(
                    image_data,
                    caption="Your Wedding Invitation",
                    use_container_width=True
                )

                st.download_button(
                    "Download Wedding Card",
                    data=image_data,
                    file_name="wedding_invitation.png",
                    mime="image/png"
                )

            except Exception as error:
                st.error("Image generation failed.")
                st.caption(str(error))
```
