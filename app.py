import os
import base64
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Shaadi Nimantran AI",
    page_icon="💍",
    layout="centered"
)

st.title("💍 Shaadi Nimantran AI")
st.write("Create your personalized wedding invitation card.")

with st.form("wedding_form"):
    groom = st.text_input("Groom Name")
    bride = st.text_input("Bride Name")
    wedding_date = st.text_input("Wedding Date")
    venue = st.text_input("Wedding Venue")

    theme = st.selectbox(
        "Select Theme",
        ["Royal Gold", "Red Floral", "Elegant White", "Modern"]
    )

    language = st.selectbox(
        "Select Language",
        ["English", "Hindi"]
    )

    submitted = st.form_submit_button("Generate Card")

if submitted:
    if not all([
        groom.strip(),
        bride.strip(),
        wedding_date.strip(),
        venue.strip()
    ]):
        st.warning("Please fill in every field.")
    else:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            st.error("API key missing. Configure Streamlit Secrets.")
        else:
            prompt = f"""
            Design an elegant Indian wedding invitation card.
            Groom: {groom}
            Bride: {bride}
            Date: {wedding_date}
            Venue: {venue}
            Theme: {theme}
            Language: {language}

            Portrait invitation, beautiful Indian ornaments,
            premium typography, decorative borders and flowers.
            Use a tasteful wedding color palette.
            """

            try:
                client = OpenAI(api_key=api_key)

                with st.spinner("Generating your card..."):
                    response = client.images.generate(
                        model="gpt-image-1",
                        prompt=prompt,
                        size="1024x1536"
                    )

                image_bytes = base64.b64decode(
                    response.data[0].b64_json
                )

                st.image(
                    image_bytes,
                    caption="Your Wedding Invitation",
                    use_container_width=True
                )

                st.download_button(
                    "Download Wedding Card",
                    data=image_bytes,
                    file_name="wedding_card.png",
                    mime="image/png"
                )

            except Exception as e:
                st.error("Image generation failed.")
                st.write(str(e))
