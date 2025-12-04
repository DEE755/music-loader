import asyncio
import os
from pymongo import MongoClient
import logging

from requests import session


async def wait_for_mongo(client: MongoClient, retries: int = 3, delay: float = 1.0) -> None:
    for attempt in range(1, retries + 1):
        try:
            print("entered try")
            await asyncio.to_thread(client.admin.command, "ping")
            return
        except Exception as exc:
            print("entered except")
            if attempt == retries:
                raise
            logging.info("Mongo not ready (attempt %s/%s): %s", attempt, retries, exc)
            await asyncio.sleep(delay)
            
            
            

def is_pdf_text(text):
        if not text:
            return False
        t = text.strip().lower()
        return "a4" in t and "pdf" in t
    
    
def download_pdf(pdf_url, dest_dir):
    """
    Télécharge un PDF vers dest_dir en gardant le nom de fichier.
    """
    os.makedirs(dest_dir, exist_ok=True)
    filename = pdf_url.rstrip("/").split("/")[-1]
    dest_path = os.path.join(dest_dir, filename)

    # évite de re-télécharger si déjà présent
    if os.path.exists(dest_path):
        print(f"  Already exists, skipping: {dest_path}")
        return

    print(f"  Downloading {pdf_url}")
    r = session.get(pdf_url, timeout=60)
    r.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(r.content)
    print(f"  Saved to {dest_path}")