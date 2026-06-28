import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

BASE_URL = "https://agritech.tnau.ac.in/crop_protection/"

def get_disease_name(url):
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    # Usually the disease name is in the first <strong> inside the main content
    strong_tag = soup.find("strong")
    if strong_tag:
        return strong_tag.get_text(" ", strip=True)
    else:
        # fallback to URL filename
        return url.rsplit("/", 1)[-1].replace(".html", "")


# Function to get disease links from a crop page
def get_disease_links(crop_page_url):
    resp = requests.get(crop_page_url, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    seen_urls = set()

    for a in soup.find_all("a", href=True):
        href = a['href']
        # keep disease pages only
        if href.endswith(".html") and "disease" in href.lower():
            full_url = urljoin(BASE_URL, href)
            if full_url not in seen_urls:
                disease_name = get_disease_name(full_url)
                links.append((disease_name, full_url))
                seen_urls.add(full_url)

    return links


# Function to get symptoms
def get_symptoms(url):
    resp = requests.get(url, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")

    symptoms = []
    current_section = False

    for tag in soup.find_all(["p", "b", "strong", "ul", "li"]):
        text = tag.get_text(" ", strip=True)
        text_lower = text.lower()

        # Detect symptom heading (symptom / symptoms / etc.)
        if text_lower.startswith("symptom"):
            current_section = True
            continue

        # If we’re inside the Symptom section
        if current_section:
            # Stop when a new section starts (like Pathogen, Management, etc.)
            if any(text_lower.startswith(x) for x in [
                "pathogen", "management", "control", "favourable", 
                "favorable", "survival", "source", "acknowledgement"
            ]):
                current_section = False
                continue

            # Collect both bullet points and meaningful paragraphs
            if tag.name == "li":
                symptoms.append(text)
            elif tag.name == "p" and len(text) > 5:
                symptoms.append(text)

    return symptoms



def get_management(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except:
        return {}

    soup = BeautifulSoup(resp.text, "html.parser")

    sections = {
        "pathogen": [],
        "survival_mode": [],
        "favourable_conditions": [],
        "management_practices": [],
        "sources": [],
        "acknowledgements": []
    }

    current_section = None

    for tag in soup.find_all(["p", "b", "strong", "ul", "li"]):
        text = tag.get_text(" ", strip=True)
        text_lower = text.lower()

        # Detect main section headings
        if text_lower.startswith("pathogen"):
            current_section = "pathogen"
            continue
        elif text_lower.startswith("survival and mode of spread"):
            current_section = "survival_mode"
            continue
        elif text_lower.startswith("favourable conditions"):
            current_section = "favourable_conditions"
            continue
        elif text_lower.startswith("management"):
            current_section = "management_practices"
            continue
        elif text_lower.startswith("source of information"):
            current_section = "sources"
            continue
        elif text_lower.startswith("acknowledgements"):
            current_section = "acknowledgements"
            continue

        # Collect points only if inside a section
        if current_section:
            if tag.name == "li":
                sections[current_section].append(text)
            # also collect <p> that are not headings (skip if starts with colon-style heading)
            elif tag.name == "p" and not text.endswith(":") and len(text) > 10:
                sections[current_section].append(text)

    # Remove empty sections
    sections = {k: v for k, v in sections.items() if v}

    return sections



# Main scrape function
def scrape_cereals(crop_name, crop_url):
    diseases = []
    disease_links = get_disease_links(crop_url)
    
    for disease_name, disease_url in disease_links:
        # Split URL into base + filename for management fallback
        parts = disease_url.rsplit("/", 1)
        base_url = parts[0]
        filename = parts[1]
        management_filename = "another%20methods_" + filename
        management_url = urljoin(base_url + "/", management_filename)

        # Get symptoms
        symptoms = get_symptoms(disease_url)

        # Try to get management from disease page first
        management = get_management(disease_url)

        # If all sections are empty, fallback to management page
        if all(len(v) == 0 for v in management.values()):
            try:
                management = get_management(management_url)
            except:
                management = {}  # if management page is missing

        diseases.append({
            "name": disease_name,
            "url": disease_url,
            "symptoms": symptoms,
            "management": management
        })
    
    return {"crop": crop_name, "diseases": diseases}


all_data = []
# crop_name = "Rice"
# crop_url = "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop%20diseases_cereals_rice_main.html"
# crop_name = "Maize"
# crop_url = "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop%20diseases_cereals_maize.html"
# crop_name = "Wheat"
# crop_url = "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop%20diseases_cereals_wheat_main.html"
# crop_name = "Sugarcane"
# crop_url = "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop%20diseases_cash%20crops_sugarcane.html"
# crop_name = "Cotton"
# crop_url = "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop%20diseases_cash%20crops_cotton.html"
# crop_name = "Potato"
# crop_url = "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop%20diseases_veg_potato.html"
# crop_name = "Tea"
# crop_url = "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop%20diseases_plantation_tea.html"
# crop_name = "Coffee"
# crop_url = "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop%20diseases_plantation_coffee.html"
crop_name = "Rubber"
crop_url = "https://agritech.tnau.ac.in/crop_protection/crop_prot_crop%20diseases_plantation_rubber.html"

print(f"Scraping {crop_name}...")
crop_data = scrape_cereals(crop_name, crop_url)
all_data.append(crop_data)

print(len(crop_data["diseases"]))


# Save to JSON
with open(f"KB/{crop_name}_diseases.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print(f"Scraping complete. Data saved in {crop_name}_diseases.json")
