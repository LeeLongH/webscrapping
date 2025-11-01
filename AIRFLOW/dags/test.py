from bs4 import BeautifulSoup

with open("out.html", "rb") as f:
    html_file = f.read()

soup = BeautifulSoup(html_file, "html.parser")

section = soup.find("section", class_="content")
text = section.get_text(strip=True) if section else None

print(text)