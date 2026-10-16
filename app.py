
import os
import streamlit as st
from openai import OpenAI

MODEL = "openai/gpt-oss-20b"

def generate_wording(prompt: str) -> str:
    api_key = os.getenv("NVIDIA_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets.get("NVIDIA_API_KEY", "")
        except Exception:
            api_key = ""

    if not api_key:
        st.error(
            "NVIDIA_API_KEY nahi mili. "
            "Environment variable ya Streamlit Secrets check karein."
        )
        return ""

    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key,
            timeout=45.0,
        )

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert Indian wedding invitation writer. "
                        "Write beautiful, respectful wedding invitations. "
                        "Follow the requested language and religion. "
                        "Return only invitation wording."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )

        result = response.choices[0].message.content
        if not result or not result.strip():
            st.error("AI ne empty response diya.")
            return ""

        return result.strip()

    except Exception as e:
        # Show the actual API error while debugging.
        st.error(f"NVIDIA API error: {type(e).__name__}: {e}")
        return ""
