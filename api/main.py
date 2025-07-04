# api/main.py

from fastapi import FastAPI, HTTPException, Request, Header
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional  # For Python 3.9+
import os

# ✅ Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

# ✅ Make sure we can import sibling folder
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from streamlit_app.scraper import run_scraper  # ✅ Now it works!

# ✅ Initialize FastAPI app
app = FastAPI(
    title="YellowPages UAE Scraper API",
    description="A secure API to run your B2B scraper remotely",
    version="1.0.0"
)

# ✅ Pydantic model for incoming JSON request
class ScrapeRequest(BaseModel):
    keyword: str
    city: str = ""
    max_pages: Optional[int] = None  # Python 3.9 syntax for Optional

# ✅ Root check
@app.get("/")
def root():
    return {"message": "✅ YellowPages UAE Scraper API is running!"}

# ✅ Main scrape endpoint with simple API key check
@app.post("/scrape")
async def scrape_data(
    body: ScrapeRequest,
    x_api_key: str = Header(None)  # Read custom header: X-API-Key
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="❌ Unauthorized: Invalid API key.")

    try:
        # 🔗 Run your local scraper logic
        file_path = run_scraper(
            body.keyword.strip(),
            body.city.strip() if body.city else "",
            body.max_pages
        )
        return {
            "message": "✅ Scraping completed successfully!",
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraper error: {str(e)}")