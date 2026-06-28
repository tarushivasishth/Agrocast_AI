symptoms(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    symptoms = []
    for tag in soup.find_all(["p", "b", "strong", "ul", "li"]):
        text = tag.get_text(" ", strip=True)
        if text.lower().startswith("symptoms"):
            if tag.name == "li":
                symptoms.append(text)
    return symptoms