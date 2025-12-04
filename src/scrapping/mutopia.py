import os
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, NavigableString
from src.utils import util
from src.schemas.models import MusicalPiece
from src.DI.container import get_piece_dao

piece_dao = get_piece_dao()

BASE_URL = "https://www.mutopiaproject.org/"
PIECE_LIST_URL = urljoin(BASE_URL, "piece-list.html")
OUTPUT_DIR = "mutopia_a4_pdfs"

session = requests.Session()
session.headers["User-Agent"] = "MutopiaA4Scraper/1.0 (personal use)"

def get_piece_pages():
    """
    Récupère toutes les URLs de pages de pièces
    depuis piece-list.html
    """
    resp = session.get(PIECE_LIST_URL, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    urls = []
    # Dans piece-list.html, chaque pièce est un lien numéroté vers cgibin/piece-info.cgi?id=XXX
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "piece-info.cgi" in href:
            full_url = urljoin(BASE_URL, href)
            urls.append(full_url)

    # supprimer les doublons en conservant l’ordre
    seen = set()
    unique_urls = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)
    return unique_urls

def fetch_piece_page(piece_url):
    resp = session.get(piece_url, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def find_pdf_link(piece_url, soup=None):
    """
    Finds PDF link on the piece page.
    """
    soup = soup or fetch_piece_page(piece_url)

    a_tag = soup.find("a", string=util.is_pdf_text)
    if not a_tag:
        return None

    pdf_href = a_tag.get("href")
    pdf_url = urljoin(piece_url, pdf_href)
    return pdf_url

def extract_piece_metadata(piece_url, soup=None, allowed_keys=None) -> MusicalPiece:
    """
    Extract metadata from a piece page and return as MusicalPiece model.
    """
    soup = soup or fetch_piece_page(piece_url)
    payload = {}

    # Grab title and composer from the page header (h2/h4).
    title_tag = soup.find("h2")
    if title_tag:
        payload["title"] = title_tag.get_text(strip=True)

    composer_tag = soup.find("h4")
    if composer_tag:
        composer_text = composer_tag.get_text(" ", strip=True)
        if composer_text.lower().startswith("by "):
            composer_text = composer_text[3:].strip()
        # Fix common mojibake for en dash ranges (e.g., 1784–1849)
        composer_text = composer_text.replace("â\x80\x93", "-")
        payload["composer"] = composer_text or None

    table = soup.find("table", class_=lambda c: c and "result-table" in c.split())
    if not table:
        raise ValueError("No metadata table found on piece page")

    table_label_to_key = {
        "Instrument(s)": "instruments",
        "Style": "style",
        "Opus": "opus",
        "Date of composition": "date_of_composition",
        "Source": "source",
        "Copyright": "copyright",
        "Last updated": "last_updated",
        "Music ID Number": "music_id_number"
    }

    #allowed_keys = set(allowed_keys) if allowed_keys else None
    for td in table.find_all("td"):
        label_tag = td.find("b")
        if not label_tag:
            continue
        label = label_tag.get_text(strip=True).rstrip(":")
        key = table_label_to_key.get(label)
        # Skip unknown labels to avoid inserting None keys into metadata
        if not key:
            continue
        #if not key or (allowed_keys is not None and key not in allowed_keys):
            #continue
        # Prefer the text right after the label, fallback to the rest of the cell
        value_node = label_tag.next_sibling
        if isinstance(value_node, NavigableString):
            value = str(value_node)
        else:
            value = td.get_text(" ", strip=True)
            value = value.replace(label_tag.get_text(" ", strip=True), "", 1)
        payload[key] = value.strip(' \n\t"') or None

    pdf_url = find_pdf_link(piece_url, soup=soup)
    if pdf_url:
        payload["pdf_url"] = pdf_url
        payload["format"] = "PDF"
        
    return MusicalPiece.model_validate(payload)
   
    

def start_scrapping(max_pieces=None, delay=1.0):
    
    piece_pages = get_piece_pages()
    if max_pieces is not None:
        piece_pages = piece_pages[:max_pieces]

    print(f"Found {len(piece_pages)} piece pages")

    for i, url in enumerate(piece_pages, start=1):
        print(f"[{i}/{len(piece_pages)}] {url}")
        try:
            soup = fetch_piece_page(url)
            metadata = extract_piece_metadata(url, soup=soup)
            print (f"  Metadata extracted. {len(metadata.model_dump())} fields found.")
            if metadata:
                print(f"  Metadata: {metadata}")
                piece_dao.insert_object_to_db(metadata)
                
        except Exception as e:
            print("  Error:", e)
        time.sleep(delay)  
