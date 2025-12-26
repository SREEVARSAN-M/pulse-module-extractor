import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
import openai
import os
import streamlit as st

openai.api_key = os.getenv("OPENAI_API_KEY")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

MAX_PAGES = 20  # HARD LIMIT to stay safe



def fetch_html(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None


# content 

def extract_headings_and_content(html):
    soup = BeautifulSoup(html, "lxml")

    # Remove nav, footer, aside
    for tag in soup(["nav", "footer", "aside", "script", "style"]):
        tag.decompose()

    content = []
    current_heading = None

    for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
        text = tag.get_text(strip=True)
        if not text:
            continue

        if tag.name in ["h1", "h2", "h3"]:
            current_heading = text
            content.append({
                "type": tag.name,
                "title": text,
                "text": ""
            })
        else:
            if content:
                content[-1]["text"] += " " + text

    return content



def infer_modules(content_blocks):
    modules = []
    current_module = None

    for block in content_blocks:
        if block["type"] == "h1":
            if current_module:
                modules.append(current_module)

            current_module = {
                "module": block["title"],
                "description_text": block["text"],
                "submodules": []
            }

        elif block["type"] in ["h2", "h3"] and current_module:
            current_module["submodules"].append({
                "title": block["title"],
                "text": block["text"]
            })

        elif current_module:
            current_module["description_text"] += " " + block["text"]

    if current_module:
        modules.append(current_module)

    return modules


# LLM generator

def generate_description(title, text):
    if not text.strip():
        return f"Documentation section covering {title}."

    prompt = f"""
    You are summarizing product documentation.
    Title: {title}
    Content: {text}

    Generate a concise but detailed description based ONLY on the content.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Description for {title} based on documentation content."


# pipeline 

def extract_modules_from_url(url):
    html = fetch_html(url)
    if not html:
        return []

    content_blocks = extract_headings_and_content(html)
    raw_modules = infer_modules(content_blocks)

    structured_output = []

    for module in raw_modules:
        module_desc = generate_description(
            module["module"],
            module["description_text"]
        )

        submodules = {}
        for sub in module["submodules"]:
            submodules[sub["title"]] = generate_description(
                sub["title"],
                sub["text"]
            )

        structured_output.append({
            "module": module["module"],
            "Description": module_desc,
            "Submodules": submodules
        })

    return structured_output



# UI
import streamlit as st
import json

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Pulse Module Extractor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------
# Grok-style Black & White Vintage Theme
# -------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0b0b;
        color: #eaeaea;
        font-family: "Courier New", monospace;
    }

    h1, h2, h3 {
        color: #ffffff;
        letter-spacing: 0.6px;
    }

    input {
        background-color: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
        border-radius: 0px !important;
    }

    .stButton button {
        background-color: #ffffff;
        color: #000000;
        border-radius: 0px;
        border: 1px solid #ffffff;
        font-weight: 600;
        padding: 0.45rem 1.2rem;
    }

    .stButton button:hover {
        background-color: #dddddd;
        color: #000000;
    }

    pre {
        background-color: #0f0f0f !important;
        color: #e6e6e6 !important;
        border: 1px solid #333;
        border-radius: 0px;
    }

    .stAlert {
        background-color: #0f0f0f;
        color: #ffffff;
        border: 1px solid #333;
    }

    .stDownloadButton button {
        background-color: transparent;
        color: #ffffff;
        border: 1px solid #ffffff;
        border-radius: 0px;
    }

    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# UI Content
# -------------------------------------------------
st.title("Pulse – Module Extraction AI Agent")

st.write(
    "A lightweight documentation intelligence tool that extracts product modules "
    "and submodules directly from help-site content and generates structured, "
    "content-grounded descriptions."
)

url = st.text_input(
    "Documentation URL",
    placeholder="https://wordpress.org/documentation/"
)

if st.button("Extract Modules"):
    if not url.strip():
        st.error("Please enter a valid documentation URL.")
    else:
        with st.spinner("Processing documentation..."):
            result = extract_modules_from_url(url)

        if result:
            st.success("Extraction completed successfully.")

            st.subheader("Structured Output")
            st.json(result)

            json_data = json.dumps(result, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="module_extraction_output.json",
                mime="application/json"
            )
        else:
            st.warning("No modules could be extracted from the provided URL.")

