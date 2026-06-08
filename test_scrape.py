import requests
from bs4 import BeautifulSoup

url = "https://www.yellowpages.com/search?search_terms=manufacturer&geo_location_terms=San+Francisco%2C+CA"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print("Status Code:", response.status_code)
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    soup = BeautifulSoup(response.content, "html.parser")
    print("Title:", soup.title.string)
    
    # Try to find organic search results
    results = soup.find_all("div", class_="result")
    print(f"Found {len(results)} 'result' divs")
    
    # Let's print the name of the first results
    for i, res in enumerate(results[:5]):
        name_div = res.find("a", class_="business-name")
        name = name_div.text.strip() if name_div else "N/A"
        print(f"  - {name}")


    
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    soup = BeautifulSoup(response.content, "html.parser")
    
    print("\n--- Examining Pagination ---")
    # Let's search for pagination links
    # Often they are inside a pagination div or nav, or have class pagination
    pagination_divs = soup.find_all(class_=lambda x: x and "pagination" in x)
    print(f"Found {len(pagination_divs)} divs with 'pagination' in class name")
    
    # Let's print all links containing page numbers or next/prev text
    links = soup.find_all("a", href=True)
    page_links = []
    for l in links:
        href = l['href']
        text = l.text.strip()
        if "page" in href or (text.isdigit()) or "Next" in text or "Prev" in text:
            page_links.append((href, text))
            
    print(f"Potential pagination links found: {len(page_links)}")
    for href, text in page_links[:10]:
        print(f"  Href: {href} | Text: {text}")

except Exception as e:
    import traceback
    traceback.print_exc()





