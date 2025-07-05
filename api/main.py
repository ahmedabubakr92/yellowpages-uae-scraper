# api/main.py

from fastapi import FastAPI, HTTPException, Request, Header
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional  # ✅ For Python 3.9+
import os
import sys

# ✅ Load environment variables from .env if running locally
load_dotenv()

# ✅ Get API_KEY securely (Render or local .env)
API_KEY = os.getenv("API_KEY")

# ✅ Ensure Python path can find the sibling scraper module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from streamlit_app.scraper import run_scraper  # ✅ Import your scraper cleanly

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

# ✅ Health check route
@app.get("/")
def root():
    return {"message": "✅ YellowPages UAE Scraper API is running!"}

# ✅ POST endpoint with API key header check
@app.post("/scrape")
async def scrape_data(
    body: ScrapeRequest,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="❌ Unauthorized: Invalid API key.")

    try:
        # ✅ Run scraper
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