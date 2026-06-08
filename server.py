import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import sys

PORT = 8000

# Seed random generator for deterministic, realistic dataset generation
random.seed(42)

# --- REALISTIC DATASET GENERATION ---
INDUSTRIES = [
    "Robotics & Automation", "Advanced Manufacturing", "FinTech Infrastructure",
    "Biotechnology", "Clean Energy & Grid", "AI & Machine Learning",
    "Enterprise SaaS", "Cybersecurity Systems", "Aerospace & Defense",
    "IoT Solutions", "Logistics & Supply Chain", "Automotive & EV",
    "Quantum Computing", "MedTech Devices", "Semicondictor Materials"
]

LOCATIONS = [
    "San Francisco, CA", "Boston, MA", "Austin, TX", "Seattle, WA", 
    "New York, NY", "Chicago, IL", "Denver, CO", "Los Angeles, CA",
    "London, UK", "Berlin, Germany", "Tokyo, Japan", "Toronto, Canada",
    "Singapore", "Munich, Germany", "Paris, France"
]

PREFIXES = [
    "Apex", "Aether", "Veloce", "Nova", "Stellar", "Quantum", "Bio", "Eco",
    "Neo", "Core", "Optima", "Zenith", "Helix", "Sentry", "Vortex", "Horizon",
    "Krypton", "Omni", "Prism", "Vector", "Summit", "Nexus", "Solaria", "Pulse"
]

SUFFIXES = [
    "Robotics", "Systems", "Technologies", "Laboratories", "Electric",
    "Solutions", "Dynamics", "Manufacturing", "Energy", "Analytics",
    "Networks", "Labs", "Industries", "Cyber", "Biotech", "Instruments",
    "Automotive", "Logistics", "Devices", "Aero", "Computing", "Silicon"
]

TAGLINES = {
    "Robotics & Automation": "Developing autonomous mobile manipulators for warehouse logistics and heavy manufacturing.",
    "Advanced Manufacturing": "Developing precision metal 3D printing systems for aerospace and medical applications.",
    "FinTech Infrastructure": "Next-generation transactional clearing infrastructure and payment rails for global commerce.",
    "Biotechnology": "Pioneering programmable mRNA therapeutic platforms for rare autoimmune and infectious diseases.",
    "Clean Energy & Grid": "Developing high-density solid-state grid storage solutions for utility-scale green energy transition.",
    "AI & Machine Learning": "Providing edge-native multi-modal foundation models optimized for low-latency robotics inference.",
    "Enterprise SaaS": "AI-orchestrated team workflows and document intelligence platforms for global enterprises.",
    "Cybersecurity Systems": "Zero-trust network authorization engines and automated real-time threat intelligence detection.",
    "Aerospace & Defense": "Designing next-generation autonomous cargo drone platforms for remote and defense logistics.",
    "IoT Solutions": "Developing ultra-low power wireless sensor networks for harsh industrial environments.",
    "Logistics & Supply Chain": "Dynamic algorithmic dispatch and real-time shipping route optimization solutions.",
    "Automotive & EV": "High-density solid-state batteries and drive-train systems for next-generation electric vehicles.",
    "Quantum Computing": "Error-corrected superconducting quantum processors and compilation software suites.",
    "MedTech Devices": "Pioneering non-invasive continuous glucose and vital sign biometric monitoring arrays.",
    "Semicondictor Materials": "Synthesizing high-purity gallium nitride wafers for next-generation power electronics."
}

def generate_companies(count=150):
    companies = []
    generated_names = set()
    
    # Pre-populate some highly tailored entries to show custom care
    custom_companies = [
        {
            "name": "Apex Robotics",
            "industry": "Robotics & Automation",
            "location": "Boston, MA",
            "website": "https://apexrobotics.io",
            "description": "Developing autonomous mobile manipulators for warehouse logistics and heavy manufacturing."
        },
        {
            "name": "NextGen EV",
            "industry": "Automotive & EV",
            "location": "Munich, Germany",
            "website": "https://nextgenev.com",
            "description": "High-density solid-state batteries and drive-train systems for next-generation electric vehicles."
        },
        {
            "name": "Stellar Bio",
            "industry": "Biotechnology",
            "location": "San Francisco, CA",
            "website": "https://stellarbio.io",
            "description": "Pioneering programmable mRNA therapeutic platforms for rare autoimmune and infectious diseases."
        }
    ]
    
    for c in custom_companies:
        companies.append(c)
        generated_names.add(c["name"])
        
    while len(companies) < count:
        prefix = random.choice(PREFIXES)
        suffix = random.choice(SUFFIXES)
        name = f"{prefix} {suffix}"
        
        if name in generated_names:
            continue
            
        generated_names.add(name)
        industry = random.choice(INDUSTRIES)
        location = random.choice(LOCATIONS)
        
        # Clean name for slug
        slug = name.lower().replace(" ", "")
        tld = "io" if random.random() > 0.5 else "com"
        website = f"https://{slug}.{tld}"
        
        description = TAGLINES.get(industry, "Developing innovative technology solutions to solve complex global challenges.")
        
        companies.append({
            "name": name,
            "industry": industry,
            "location": location,
            "website": website,
            "description": description
        })
        
    return companies

ALL_COMPANIES = generate_companies()

# --- STATE TRACKING FOR SIMULATED ERROR ENDPOINTS ---
# We keep track of how many times error endpoints have been hit to simulate
# transient network issues that eventually resolve on retry attempts.
error_states = {
    "429_hits": 0,
    "500_hits": 0
}

# --- TEMPLATE CSS & HTML DESIGN ---
# Curated harmonious color palette: Sleek Dark Mode (Glassmorphism & harmonized HSL accents)
CSS_STYLE = """
:root {
    --bg-color: #0d1117;
    --card-bg: #161b22;
    --text-color: #c9d1d9;
    --text-muted: #8b949e;
    --primary-color: #58a6ff;
    --primary-hover: #1f6feb;
    --border-color: #30363d;
    --badge-bg: #21262d;
    --success-color: #2ea44f;
    --danger-color: #da3637;
    --warning-color: #d29922;
    --font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}

body {
    background-color: var(--bg-color);
    color: var(--text-color);
    font-family: var(--font-family);
    margin: 0;
    padding: 0;
    line-height: 1.6;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 20px;
}

header {
    margin-bottom: 40px;
    text-align: center;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 30px;
}

header h1 {
    font-size: 2.5em;
    color: #ffffff;
    margin: 0 0 10px 0;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, #58a6ff 0%, #bc8cff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

header p {
    color: var(--text-muted);
    font-size: 1.1em;
    margin: 0;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 30px;
}

.stat-card {
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 15px;
    text-align: center;
}

.stat-card .value {
    font-size: 1.8em;
    font-weight: 700;
    color: var(--primary-color);
}

.stat-card .label {
    font-size: 0.9em;
    color: var(--text-muted);
}

.company-card {
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 20px;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.company-card:hover {
    transform: translateY(-2px);
    border-color: var(--primary-color);
    box-shadow: 0 6px 12px rgba(88, 166, 255, 0.1);
}

.company-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
    flex-wrap: wrap;
    gap: 10px;
}

.company-name {
    font-size: 1.4em;
    color: #ffffff;
    margin: 0;
}

.company-badges {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.badge {
    font-size: 0.75em;
    padding: 4px 8px;
    border-radius: 6px;
    font-weight: 600;
    border: 1px solid var(--border-color);
}

.company-industry {
    background-color: rgba(88, 166, 255, 0.1);
    color: var(--primary-color);
    border-color: rgba(88, 166, 255, 0.2);
}

.company-location {
    background-color: var(--badge-bg);
    color: var(--text-color);
}

.company-description {
    color: var(--text-muted);
    font-size: 0.95em;
    margin: 10px 0 15px 0;
}

.company-website {
    display: inline-flex;
    align-items: center;
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9em;
    transition: color 0.2s ease;
}

.company-website:hover {
    color: var(--primary-hover);
    text-decoration: underline;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    margin-top: 40px;
}

.pagination a, .pagination span {
    padding: 8px 16px;
    border-radius: 6px;
    border: 1px solid var(--border-color);
    text-decoration: none;
    color: var(--text-color);
    font-weight: 600;
    font-size: 0.9em;
    transition: background-color 0.2s ease, border-color 0.2s ease;
}

.pagination a:hover {
    background-color: var(--badge-bg);
    border-color: var(--text-muted);
}

.pagination .active {
    background-color: var(--primary-color);
    color: #ffffff;
    border-color: var(--primary-color);
}

.pagination .disabled {
    color: var(--text-muted);
    pointer-events: none;
    opacity: 0.5;
}

/* Simulated testing UI */
.simulation-panel {
    background-color: rgba(210, 153, 34, 0.05);
    border: 1px dashed var(--warning-color);
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 30px;
    font-size: 0.9em;
}

.simulation-panel h3 {
    margin: 0 0 10px 0;
    color: var(--warning-color);
}

.simulation-links {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}

.simulation-link {
    color: var(--warning-color);
    text-decoration: none;
    font-weight: 600;
}

.simulation-link:hover {
    text-decoration: underline;
}

.error-container {
    text-align: center;
    padding: 80px 20px;
}

.error-code {
    font-size: 6em;
    font-weight: 900;
    color: var(--danger-color);
    margin: 0;
    line-height: 1;
}

.error-title {
    font-size: 1.8em;
    color: #ffffff;
    margin: 15px 0;
}

.error-desc {
    color: var(--text-muted);
    max-width: 500px;
    margin: 0 auto 30px auto;
}

.btn-home {
    display: inline-block;
    padding: 10px 20px;
    background-color: var(--primary-color);
    color: #ffffff;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
    transition: background-color 0.2s ease;
}

.btn-home:hover {
    background-color: var(--primary-hover);
}
"""

class DirectoryRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Format logs neatly to standard output
        sys.stdout.write(f"[Server Log] {format % args}\n")

    def send_html(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        # --- 1. SIMULATE STATUS CODES FOR RETRY ENGINE TESTING ---
        
        if path == "/simulate-429":
            error_states["429_hits"] += 1
            # We fail the first 3 times (Too Many Requests), and succeed on the 4th!
            if error_states["429_hits"] <= 3:
                html = f"""<!DOCTYPE html>
                <html>
                <head>
                    <title>429 Too Many Requests</title>
                    <style>{CSS_STYLE}</style>
                </head>
                <body>
                    <div class="error-container">
                        <p class="error-code">429</p>
                        <h2 class="error-title">Rate Limit Exceeded (Simulated)</h2>
                        <p class="error-desc">Simulating aggressive API rate limiting. This endpoint will succeed on request attempt #4. Current hits: {error_states["429_hits"]}/4.</p>
                        <a href="/" class="btn-home">Return Directory Home</a>
                    </div>
                </body>
                </html>"""
                self.send_html(html, 429)
            else:
                # Reset hits counter after a success to allow future demo runs
                error_states["429_hits"] = 0
                html = f"""<!DOCTYPE html>
                <html>
                <head>
                    <title>200 OK</title>
                    <style>{CSS_STYLE}</style>
                </head>
                <body>
                    <div class="container" style="text-align: center; padding-top: 100px;">
                        <h2 style="color: var(--success-color)">✓ Connection Resolved Successfully!</h2>
                        <p style="color: var(--text-muted)">The Scraper Retry logic successfully endured the rate limiting and resolved on Attempt #4.</p>
                        <a href="/" class="btn-home">Go Back</a>
                    </div>
                </body>
                </html>"""
                self.send_html(html, 200)
            return

        if path == "/simulate-500":
            error_states["500_hits"] += 1
            # We fail the first 2 times (Internal Server Error), and succeed on the 3rd!
            if error_states["500_hits"] <= 2:
                html = f"""<!DOCTYPE html>
                <html>
                <head>
                    <title>500 Internal Server Error</title>
                    <style>{CSS_STYLE}</style>
                </head>
                <body>
                    <div class="error-container">
                        <p class="error-code">500</p>
                        <h2 class="error-title">Simulated Server Downtime</h2>
                        <p class="error-desc">Simulating server issues. This page will resolve on request attempt #3. Current hits: {error_states["500_hits"]}/3.</p>
                        <a href="/" class="btn-home">Return Directory Home</a>
                    </div>
                </body>
                </html>"""
                self.send_html(html, 500)
            else:
                error_states["500_hits"] = 0
                html = f"""<!DOCTYPE html>
                <html>
                <head>
                    <title>200 OK</title>
                    <style>{CSS_STYLE}</style>
                </head>
                <body>
                    <div class="container" style="text-align: center; padding-top: 100px;">
                        <h2 style="color: var(--success-color)">✓ Server Recovered Successfully!</h2>
                        <p style="color: var(--text-muted)">The Scraper successfully bypassed the server outage and retrieved the payload on Attempt #3.</p>
                        <a href="/" class="btn-home">Go Back</a>
                    </div>
                </body>
                </html>"""
                self.send_html(html, 200)
            return

        # --- 2. STANDARD DIRECTORY PAGINATION (10 PAGES) ---
        
        # Check if the page is requested in the format `/page/X`
        page_num = 1
        is_directory_route = False
        
        if path == "/":
            is_directory_route = True
            page_num = 1
        elif path.startswith("/page/"):
            is_directory_route = True
            try:
                page_num = int(path.split("/")[-1])
            except ValueError:
                page_num = 1

        if is_directory_route:
            # Enforce 10-page ceiling
            if page_num < 1 or page_num > 10:
                html = f"""<!DOCTYPE html>
                <html>
                <head>
                    <title>404 Not Found</title>
                    <style>{CSS_STYLE}</style>
                </head>
                <body>
                    <div class="error-container">
                        <p class="error-code">404</p>
                        <h2 class="error-title">Page Out of Bounds</h2>
                        <p class="error-desc">The directory pagination is limited to exactly 10 pages containing 15 records each (Total 150).</p>
                        <a href="/" class="btn-home">Directory Home</a>
                    </div>
                </body>
                </html>"""
                self.send_html(html, 404)
                return

            items_per_page = 15
            start_index = (page_num - 1) * items_per_page
            end_index = start_index + items_per_page
            page_companies = ALL_COMPANIES[start_index:end_index]

            # Build listing cards
            cards_html = ""
            for comp in page_companies:
                cards_html += f"""
                <div class="company-card">
                    <div class="company-header">
                        <h3 class="company-name">{comp["name"]}</h3>
                        <div class="company-badges">
                            <span class="company-industry badge">{comp["industry"]}</span>
                            <span class="company-location badge">{comp["location"]}</span>
                        </div>
                    </div>
                    <p class="company-description">{comp["description"]}</p>
                    <a class="company-website" href="{comp["website"]}" target="_blank">
                        Visit Website 
                        <svg style="margin-left: 4px;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" width="12" height="12">
                            <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6m4-3h6v6m-11 5L21 3" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </a>
                </div>
                """

            # Build Pagination
            prev_class = "" if page_num > 1 else "disabled"
            next_class = "" if page_num < 10 else "disabled"
            prev_href = f"/page/{page_num - 1}" if page_num > 1 else "#"
            next_href = f"/page/{page_num + 1}" if page_num < 10 else "#"

            pagination_html = f'<div class="pagination">'
            pagination_html += f'<a class="prev-page {prev_class}" href="{prev_href}">« Previous</a>'
            for p in range(1, 11):
                active_class = "active" if p == page_num else ""
                pagination_html += f'<a class="{active_class}" href="/page/{p}">{p}</a>'
            pagination_html += f'<a class="next-page {next_class}" href="{next_href}">Next »</a>'
            pagination_html += "</div>"

            # Main Page Template
            html_content = f"""<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Global Startup & Manufacturer Directory</title>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
                <style>{CSS_STYLE}</style>
            </head>
            <body>
                <div class="container">
                    <header>
                        <h1>Global Startup & Manufacturer Directory</h1>
                        <p>Enterprise Sandbox for Scraping and Lead Extraction Practice</p>
                    </header>

                    <div class="simulation-panel">
                        <h3>Scraper Resilience Testing Lab</h3>
                        <p>Simulate production exceptions to test your scraper retry engine. Standard GET requests will receive errors but resolve transparently under proper backoff retry handling.</p>
                        <div class="simulation-links">
                            <a class="simulation-link" href="/simulate-429" target="_blank">Simulate Rate Limit (HTTP 429 - Resolves on 4th hit)</a>
                            <a class="simulation-link" href="/simulate-500" target="_blank">Simulate Server Outage (HTTP 500 - Resolves on 3rd hit)</a>
                        </div>
                    </div>

                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="value">150</div>
                            <div class="label">Total Businesses</div>
                        </div>
                        <div class="stat-card">
                            <div class="value">10</div>
                            <div class="label">Total Pages</div>
                        </div>
                        <div class="stat-card">
                            <div class="value">15</div>
                            <div class="label">Records Per Page</div>
                        </div>
                    </div>

                    <main class="company-list">
                        {cards_html}
                    </main>

                    {pagination_html}
                </div>
            </body>
            </html>"""
            
            self.send_html(html_content, 200)
            return

        # Fallback 404 for arbitrary routes
        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <title>404 Not Found</title>
            <style>{CSS_STYLE}</style>
        </head>
        <body>
            <div class="error-container">
                <p class="error-code">404</p>
                <h2 class="error-title">Route Not Found</h2>
                <p class="error-desc">The requested endpoint is not available in the directory web server.</p>
                <a href="/" class="btn-home">Directory Home</a>
            </div>
        </body>
        </html>"""
        self.send_html(html, 404)

def run(port=PORT):
    server_address = ("", port)
    httpd = HTTPServer(server_address, DirectoryRequestHandler)
    print(f"============================================================")
    print(f" MOCK DIRECTORY WEB SERVER STARTED SUCCESSFULLY             ")
    print(f" Listening on: http://localhost:{port}                      ")
    print(f" Press Ctrl+C to stop the server                            ")
    print(f"============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Mock Directory Web Server... Done.")
        sys.exit(0)

if __name__ == "__main__":
    run()
