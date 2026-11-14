import json
import os
import re
import urllib.request

CREDLY_USER = "ematevar"
API_URL = f"https://www.credly.com/users/{CREDLY_USER}/badges.json"
README_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")


def fetch_badges():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))
        return payload.get("data", [])


def build_badges_html(badges):
    if not badges:
        return "<p align=\"center\"><i>No public Credly badges found.</i></p>\n"

    cards = []
    for b in badges:
        template = b.get("badge_template", {})
        name = template.get("name", "Certification")
        issuer = template.get("issuer", {}).get("summary", "")
        badge_id = b.get("id", "")
        badge_url = f"https://www.credly.com/badges/{badge_id}"
        img_url = b.get("image_url", "")

        card = f"""    <td align="center" width="16%">
      <a href="{badge_url}" target="_blank">
        <img src="{img_url}" width="95" height="95" alt="{name}" /><br />
        <sub><b>{name}</b></sub><br />
        <sub><font color="#888">{issuer}</font></sub>
      </a>
    </td>"""
        cards.append(card)

    # Organizar en filas de max 3 por fila para que se lea perfecto en móvil y desktop
    rows = []
    chunk_size = 3
    for i in range(0, len(cards), chunk_size):
        chunk = cards[i : i + chunk_size]
        row_content = "\n".join(chunk)
        rows.append(f"  <tr>\n{row_content}\n  </tr>")

    table_body = "\n".join(rows)

    html = f"""<div align="center">
  <p>
    <a href="https://www.credly.com/users/{CREDLY_USER}" target="_blank">
      <img src="https://img.shields.io/badge/Credly-Ver_Perfil_Oficial-F47E20?style=for-the-badge&logo=credly&logoColor=white" alt="Credly Profile" />
    </a>
    <img src="https://img.shields.io/badge/Badges_Verificados-{len(badges)}-0A84FF?style=for-the-badge" alt="Badge Count" />
  </p>

  <table border="0" align="center">
{table_body}
  </table>
</div>"""
    return html


def update_readme():
    print(f"Fetching badges from Credly for user: {CREDLY_USER}...")
    badges = fetch_badges()
    print(f"Retrieved {len(badges)} badges.")

    badges_html = build_badges_html(badges)

    if not os.path.exists(README_PATH):
        raise FileNotFoundError(f"README not found at {README_PATH}")

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "<!-- CREDLY_BADGES_START -->"
    end_marker = "<!-- CREDLY_BADGES_END -->"

    pattern = re.compile(
        f"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
        re.DOTALL,
    )

    replacement = f"{start_marker}\n{badges_html}\n{end_marker}"

    if not pattern.search(content):
        print("Warning: Marker tags not found in README. Appending section.")
        new_content = content + f"\n\n### 🏆 Certificaciones Oficiales (Credly)\n\n{replacement}\n"
    else:
        new_content = pattern.sub(replacement, content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("README.md updated successfully with Credly badges!")


if __name__ == "__main__":
    update_readme()
