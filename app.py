import os
import io
import streamlit as st
from google import genai
from PIL import Image

st.set_page_config(
    page_title="Shaadi Nimantran AI",
    page_icon="💍",
    layout="centered"
)

st.title("💍 Shaadi Nimantran AI")
st.write("Create a personalized Indian wedding invitation card.")

with st.form("wedding_form"):
    groom = st.text_input("Groom's Name")
    bride = st.text_input("Bride's Name")
    wedding_date = st.text_input("Wedding Date")
    venue = st.text_input("Wedding Venue")

    theme = st.selectbox(
        "Choose Card Design",
        ["Royal Red and Gold", "Floral", "Traditional Indian", "Modern"]
    )

    language = st.selectbox(
        "Invitation Language",
        ["Hindi", "English"]
    )

    submitted = st.form_submit_button("Generate Wedding Card")

if submitted:
    if not all([
        groom.strip(),
        bride.strip(),
        wedding_date.strip(),
        venue.strip()
    ]):
        st.warning("Please fill in all fields.")
    else:
        api_key = st.secrets.get(
            "AQ.Ab8RN6IyugJceYwO-sa7E3aZi5UC6vf5kF5_hVVGcOgbgkxBvw",
            os.getenv("GEMINI_API_KEY", "")
        )

        if not api_key:
            st.error(
                "Gemini API key missing. Add GEMINI_API_KEY "
                "in Streamlit Cloud Settings > Secrets."
            )
        else:
            prompt = f"""
            Generate a beautiful, high-quality Indian wedding
            invitation card as an image.

            Groom: {groom}
            Bride: {bride}
            Wedding date: {wedding_date}
            Venue: {venue}
            Design: {theme}
            Language: {language}

            Create a vertical portrait card with elegant Indian
            motifs, decorative borders, floral patterns, rich
            colors and premium typography.

            Include the couple's names, date and venue clearly.
            Make the design balanced and suitable for printing.
            """

            try:
                client = genai.Client(api_key=api_key)

                with st.spinner("Gemini is designing your card..."):
                    response = client.models.generate_content(
                        model="gemini-3.1-flash-image",
                        contents=prompt
                    )

                generated_image = None

                for part in response.parts:
                    if part.inline_data is not None:
                        generated_image = part.as_image()
                        break

                if generated_image is None:
                    st.error(
                        "No image returned. The model may have "
                        "returned text only or image generation "
                        "may not be available for your API account."
                    )
                else:
                    st.success("Wedding invitation generated!")
                    st.image(
                        generated_image,
                        caption="Your Wedding Invitation",
                        use_container_width=True
                    )

                    buffer = io.BytesIO()
                    generated_image.save(buffer, format="PNG")

                    st.download_button(
                        "Download Wedding Card",
                        data=buffer.getvalue(),
                        file_name="shaadi_nimantran.png",
                        mime="image/png"
                    )

            except Exception as e:
                st.error("Gemini image generation failed.")
                st.code(str(e))
