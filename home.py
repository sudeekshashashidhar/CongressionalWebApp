from __future__ import annotations

import html
from pathlib import Path


DIST_DIR = Path("dist")
OUTPUT_FILE = Path("home.html")


def discover_city_pages(dist_dir: Path = DIST_DIR) -> list[tuple[str, str]]:
    """Return [(label, relative_path)] for each city HTML page under dist."""
    if not dist_dir.exists():
        return []

    discovered: dict[str, Path] = {}

    for path in sorted(dist_dir.rglob("*.html")):
        # Skip the statewide index page
        if path == dist_dir / "index.html":
            continue

        # Skip loose HTML files at the root (we prefer the city folders)
        if path.parent == dist_dir and path.name != "index.html":
            continue

        if path.name == "index.html":
            slug = path.parent.name
        else:
            slug = path.stem

        label = slug_to_label(slug)
        # Prefer nested city directories over single files if duplicates appear
        if label not in discovered or path.name == "index.html":
            discovered[label] = path

    return [(label, rel_path(dist_dir.parent, p)) for label, p in sorted(discovered.items())]


def slug_to_label(slug: str) -> str:
    """Convert a slug like 'chapel-hill-nc' into 'Chapel Hill, NC'."""
    parts = slug.split("-")
    if parts and parts[-1].lower() == "nc":
        city = " ".join(parts[:-1]) or "NC"
        return f"{city.title()}, NC"
    return slug.replace("-", " ").title()


def rel_path(base: Path, target: Path) -> str:
    """Return POSIX-style relative path from base directory to target."""
    return target.relative_to(base).as_posix()


def build_home_html(city_pages: list[tuple[str, str]]) -> str:
    """Produce the home page HTML string."""
    options_html = "\n".join(
        f'          <option value="{html.escape(path)}">{html.escape(label)}</option>'
        for label, path in city_pages
    )

    if not options_html:
        options_html = '          <option value="" disabled>No city pages found</option>'

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>North Carolina Careers Hub</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: \"Segoe UI\", system-ui, -apple-system, sans-serif;
      line-height: 1.6;
      --bg: #f5f7fb;
      --text: #1f2933;
      --muted: #637183;
      --accent: #2463eb;
      --accent-dark: #1a44a6;
      --card: #ffffff;
      --shadow: 0 18px 45px rgba(15, 31, 62, 0.12);
      --radius: 18px;
    }}

    *, *::before, *::after {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      display: flex;
      flex-direction: column;
    }}

    header {{
      background: linear-gradient(145deg, #102b5d, #15407c, #2463eb);
      color: #fff;
      padding: 3.5rem 1.5rem 3rem;
      text-align: center;
    }}

    header h1 {{
      margin: 0;
      font-size: clamp(2.2rem, 3vw + 1.2rem, 3.2rem);
      letter-spacing: -0.015em;
    }}

    header p {{
      margin: 1rem auto 0;
      max-width: 60ch;
      color: #dce7ff;
    }}

    main {{
      flex: 1 1 auto;
      width: min(900px, 92%);
      margin: -2.5rem auto 0;
    }}

    .search-card {{
      background: var(--card);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 2.2rem 2.4rem;
      display: grid;
      gap: 1.4rem;
    }}

    .search-card h2 {{
      margin: 0;
      font-size: clamp(1.5rem, 1.4vw + 1rem, 2rem);
    }}

    .search-form {{
      display: grid;
      gap: 1rem;
    }}

    .search-fields {{
      display: grid;
      gap: 0.75rem;
    }}

    @media (min-width: 640px) {{
      .search-fields {{
        grid-template-columns: 1fr 1fr;
        gap: 0.85rem;
        align-items: center;
      }}
    }}

    @media (min-width: 960px) {{
      .search-fields {{
        grid-template-columns: 1.1fr 1fr 1fr;
      }}
    }}

    .search-fields input {{
      border: 1px solid rgba(31, 41, 51, 0.1);
      border-radius: 999px;
      padding: 0.85rem 1.1rem;
      font-size: 1rem;
      width: 100%;
    }}

    .search-fields select {{
      border: 1px solid rgba(31, 41, 51, 0.12);
      border-radius: 999px;
      padding: 0.85rem 1.1rem;
      font-size: 1rem;
      width: 100%;
      background: #fff;
    }}

    .search-form button {{
      justify-self: flex-start;
      border: none;
      border-radius: 999px;
      padding: 0.85rem 1.8rem;
      background: var(--accent);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
      transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
    }}

    .search-form button:hover {{
      background: var(--accent-dark);
      transform: translateY(-2px);
      box-shadow: var(--shadow);
    }}

    footer {{
      padding: 2rem 0 2.5rem;
      text-align: center;
      color: var(--muted);
      font-size: 0.95rem;
    }}
  </style>
</head>
<body>
  <header>
    <h1>North Carolina Careers Hub</h1>
    <p>Explore in-demand roles across the Tar Heel State. Choose a city to see curated opportunities filtered from the latest Adzuna feed.</p>
  </header>
  <main>
    <section class=\"search-card\">
      <h2>Search openings by city</h2>
      <form class=\"search-form\" id=\"city-form\">
        <div class=\"search-fields\">
          <label class=\"visually-hidden\" for=\"city-search\">Filter cities</label>
          <input id=\"city-search\" type=\"search\" placeholder=\"Start typing a city...\" autocomplete=\"off\" />
          <label class=\"visually-hidden\" for=\"keyword-search\">Keyword or skill (optional)</label>
          <input id=\"keyword-search\" type=\"search\" placeholder=\"Keyword or skill (optional)\" autocomplete=\"off\" />
          <label class=\"visually-hidden\" for=\"city-select\">Choose a city</label>
          <select id=\"city-select\" required>
            <option value=\"\" disabled selected>Select a city</option>
{options_html}
          </select>
        </div>
        <button type=\"submit\">View city insights</button>
      </form>
    </section>
  </main>
  <footer>
    &copy; 2024 North Carolina Careers Hub. Connecting talent with opportunity statewide.
  </footer>

  <style>
    .visually-hidden {{
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }}
  </style>
  <script>
    const searchInput = document.getElementById('city-search');
    const keywordInput = document.getElementById('keyword-search');
    const citySelect = document.getElementById('city-select');
    const form = document.getElementById('city-form');

    if (searchInput && citySelect) {{
      searchInput.addEventListener('input', () => {{
        const term = searchInput.value.trim().toLowerCase();
        let firstVisible = null;
        Array.from(citySelect.options).forEach(option => {{
          if (!option.value) return;
          const match = option.text.toLowerCase().includes(term);
          option.hidden = !match;
          if (match && !firstVisible) {{
            firstVisible = option;
          }}
        }});
        if (firstVisible) {{
          citySelect.value = firstVisible.value;
        }} else {{
          citySelect.value = '';
        }}
      }});
    }}

    if (form && citySelect) {{
      form.addEventListener('submit', event => {{
        event.preventDefault();
        let destination = citySelect.value;
        if (!destination) return;

        const keyword = keywordInput ? keywordInput.value.trim() : '';
        if (keyword) {{
          const joiner = destination.includes('?') ? '&' : '?';
          destination += joiner + 'q=' + encodeURIComponent(keyword);
        }}
        window.location.href = destination;
      }});
    }}
  </script>
</body>
</html>
"""


def main() -> None:
    city_pages = discover_city_pages()
    html_doc = build_home_html(city_pages)
    OUTPUT_FILE.write_text(html_doc, encoding="utf-8")
    print(f"✅ Wrote home page to '{OUTPUT_FILE}'.")


if __name__ == "__main__":
    main()
