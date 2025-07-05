import streamlit as st
import os
import requests

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="YellowPages UAE Scraper",
    page_icon="📄",
    layout="centered"
)

# --- HIDE Streamlit default elements ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    body {
        background-color: #f5f7fa;
    }
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e2f71;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 1rem;
        color: #555;
        margin-bottom: 25px;
    }
    .stButton>button {
        background-color: #1e2f71;
        color: white;
        border-radius: 5px;
        height: 3em;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- TITLE ---
st.markdown('<div class="title">YellowPages UAE Scraper</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Find & download verified business contacts easily.</div>', unsafe_allow_html=True)

# --- POPULAR CATEGORIES ---
categories = [
    "Advertising", "Air Conditioning", "Aluminium", "Building Materials",
    "Cable and Wire", "Car Hire and Leasing", "Chemicals", "Clinics", "Digital Printing",
    "Concrete Products", "Electrical", "Exhibition Stands", "Generators",
    "Hardware and Tools", "H Frame Scaffolding", "Hospitals", "Event Management",
    "Interior Decorators", "Kitchen Equipment", "Oilfield Equipment", "Pipes",
    "Plastics", "Packaging Materials", "Prefabricated Buildings", "Safety And Security",
    "Shelving and Storage", "Steel Merchants", "Steel Fabricators", "Valves"
]

st.markdown("### 💡 Click a popular category:")

# --- Store selected category in session state ---
if "selected_category" not in st.session_state:
    st.session_state["selected_category"] = ""

cols = st.columns(3)
for idx, category in enumerate(categories):
    if cols[idx % 3].button(category):
        st.session_state["selected_category"] = category

# --- SEARCH INPUT ---
st.markdown("### 🔍 What are you searching for?")
keyword = st.text_input(
    "Type any business category or keyword",
    value=st.session_state["selected_category"],
    placeholder="e.g., Steel Fabricators"
)

# --- CITY SELECT ---
emirates = ["", "Abu Dhabi", "Dubai", "Sharjah", "Ajman",
            "Umm Al Quwain", "Ras Al Khaimah", "Fujairah"]
city = st.selectbox("🏙️ Select an Emirate (optional)", emirates)

# --- MAX PAGES SELECT ---
st.markdown("### 📄 How many pages to scrape?")
page_options = ["All Pages"] + [str(i) for i in range(1, 11)]
selected_page = st.selectbox("Select pages to scrape", page_options)
max_pages = None if selected_page == "All Pages" else int(selected_page)

# ✅ --- API Endpoint ---
API_URL = "https://YOUR-RENDER-API-URL/scrape"

# --- SCRAPE BUTTON ---
if st.button("🚀 Start Scraping"):
    if not keyword.strip():
        st.warning("⚠️ Please enter or select a keyword.")
    else:
        st.info("🔎 Scraping in progress... Please wait...")

        try:
            # ✅ Payload for the API
            payload = {
                "keyword": keyword.strip(),
                "city": city if city else "",
                "max_pages": max_pages
            }

            headers = {
                "X-API-Key": st.secrets["API_KEY"]
            }

            # ✅ Call your Render API!
            response = requests.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            file_path = data.get("file_path")

            if file_path:
                st.success("✅ Done! Your data is ready.")
                st.write("📄 File saved at:", file_path)
                # 👉 If you later host files on S3 / Render static: add download link here
            else:
                st.error("⚠️ No file path returned.")

        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")