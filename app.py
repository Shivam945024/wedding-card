import os
import io
import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(
    page_title="Shaadi Nimantran AI",
    page_icon="💍",
    layout="centered"
)

st.title("💍 Shaadi Nimantran AI")
st.subheader("AI Wedding Invitation Card Generator")
st.write("Create a personalized wedding invitation for your special day.")

with st.form("wedding_form"):
    st.subheader("Wedding Details")

    groom = st.text_input("Groom's Name")
    bride = st.text_input("Bride's Name")
    wedding_date = st.date_input("Wedding Date")
    wedding_time = st.text_input("Wedding Time (optional)")
    venue = st.text_input("Wedding Venue")
    family_message = st.text_input(
        "Family Invitation Message (optional)",
        placeholder="With the blessings of our families..."
    )

    religion = st.selectbox(
        "Select Religion / Tradition",
        [
            "Hindu",
            "Muslim",
            "Sikh",
            "Christian",
            "Buddhist",
            "Jain",
            "Interfaith",
            "Other"
        ]
    )

    language = st.selectbox(
        "Invitation Language",
        ["English", "Hindi"]
    )

    theme = st.selectbox(
        "Card Design",
        [
            "Royal Red and Gold",
            "Floral",
            "Traditional",
            "Elegant White",
            "Modern",
            "Luxury"
        ]
    )

    submitted = st.form_submit_button("Generate Wedding Card")

if submitted:
    if not groom.strip() or not bride.strip() or not venue.strip():
        st.warning("Please enter the bride's name, groom's name, and venue.")
    else:
        token = st.secrets.get(
            "HF_TOKEN",
            os.getenv("HF_TOKEN", "")
        )

        if not token:
            st.error(
                "Hugging Face token is missing. Add HF_TOKEN "
                "in Streamlit Cloud Settings > Secrets."
            )
        else:
            prompt = f"""
Create a beautiful, premium Indian wedding invitation card.

Bride's name: {bride}
Groom's name: {groom}
Wedding date: {wedding_date.strftime("%d %B %Y")}
Wedding time: {wedding_time if wedding_time.strip() else "Not specified"}
Venue: {venue}
Religion or tradition: {religion}
Language: {language}
Design theme: {theme}
Family message: {family_message if family_message.strip() else "With love and blessings, we invite you to celebrate our wedding."}

Design requirements:
- Create a vertical portrait wedding invitation.
- Use culturally respectful decorations appropriate to the selected
  religion or tradition.
- For Hindu weddings, use suitable floral patterns, traditional
  motifs and an appropriate festive palette.
- For Muslim weddings, use elegant geometric patterns and
  appropriate Islamic-inspired ornamentation.
- For Sikh weddings, use respectful Punjabi wedding-inspired
  decoration.
- For Christian weddings, use elegant floral designs and
  appropriate wedding motifs.
- For Interfaith weddings, combine traditions respectfully.
- For other traditions, use elegant neutral wedding decoration.
- Do not mix religious symbols from unrelated traditions.
- Keep the design balanced, readable and suitable for printing.
- Render the supplied names, date and venue as accurately as possible.
"""

            try:
                client = InferenceClient(
                    provider="auto",
                    api_key=token
                )

                with st.spinner("Creating your wedding invitation..."):
                    image = client.text_to_image(
                        prompt=prompt,
                        model="black-forest-labs/FLUX.1-dev"
                    )

                st.success("Your wedding invitation is ready!")
                st.image(
                    image,
                    caption="Shaadi Nimantran AI",
                    use_container_width=True
                )

                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                image_data = buffer.getvalue()

                st.download_button(
                    label="Download Wedding Card (PNG)",
                    data=image_data,
                    file_name="shaadi_nimantran.png",
                    mime="image/png"
                )

            except Exception as error:
                st.error("Unable to generate the wedding card.")
                st.code(str(error))
                st.info(
                    "Check your Hugging Face token, model availability, "
                    "inference permissions, and remaining credits."
                )
