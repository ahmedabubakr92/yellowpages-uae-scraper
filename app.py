import streamlit as st
import os
from scraper import run_scraper  # ✅ Local scraper

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="YellowPages UAE Scraper",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- FORCE LIGHT MODE + CUSTOM CSS ---
st.markdown("""
    <style>
    html, body {
        background-color: #f9fafb !important;
        color: #1e2f71 !important;
        font-family: 'Segoe UI', 'Helvetica Neue', sans-serif !important;
    }
    .title {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1e2f71 !important;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #555 !important;
        margin-bottom: 25px;
    }
    .stButton>button {
        background-color: #1e2f71 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
        height: 3em !important;
        font-weight: 600 !important;
        padding: 0 1.5em !important;
    }
    .stButton>button:hover {
        background-color: #16235a !important;
    }
    .stDownloadButton>button {
        background-color: #28a745 !important;
        color: #ffffff !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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

st.markdown("### 💡 Pick a popular category (optional):")

if "selected_category" not in st.session_state:
    st.session_state["selected_category"] = ""

selected_category = st.selectbox(
    "Choose from popular categories:",
    [""] + categories,
    index=categories.index(st.session_state["selected_category"]) + 1 if st.session_state["selected_category"] else 0
)

if selected_category:
    st.session_state["selected_category"] = selected_category

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

# --- SCRAPE BUTTON ---
if st.button("🚀 Start Scraping"):
    if not keyword.strip():
        st.warning("⚠️ Please enter or select a keyword.")
    else:
        with st.spinner("🔎 Scraping in progress... Please wait!"):
            try:
                file_path = run_scraper(
                    keyword.strip(),
                    city if city else "",
                    max_pages
                )

                if file_path and os.path.exists(file_path):
                    st.success("✅ Done! Your data is ready.")
                    st.write(f"📄 Saved file: `{file_path}`")
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Excel",
                            data=f,
                            file_name=os.path.basename(file_path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.error("⚠️ Could not find the generated file.")

            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")