import requests
from bs4 import BeautifulSoup


def decode_secret_message(url):
    # 1. Download the published Google Doc
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    # 2. Read the document's HTML
    soup = BeautifulSoup(response.text, "html.parser")

    coordinates = []

    # 3. Extract the data from the table
    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"])

        if len(cells) < 3:
            continue

        values = [cell.get_text(strip=True) for cell in cells]

        try:
            x = int(values[0])
            character = values[1]
            y = int(values[2])
        except ValueError:
            # Skip the table header
            continue

        coordinates.append((x, character, y))

    if not coordinates:
        raise ValueError("No valid character data found.")

    # 4. Calculate the grid dimensions
    max_x = max(x for x, _, _ in coordinates)
    max_y = max(y for _, _, y in coordinates)

    # Create a grid filled with spaces
    grid = [
        [" "] * (max_x + 1)
        for _ in range(max_y + 1)
    ]

    # 5. Place each character at its coordinates
    for x, character, y in coordinates:
        grid[max_y - y][x] = character

    # 6. Print the completed grid
    for row in grid:
        print("".join(row).rstrip())


# Replace this with the published Google Doc URL
decode_secret_message("https://docs.google.com/document/d/e/2PACX-1vSvM5gDlNvt7npYHhp_XfsJvuntUhq184By5xO_pA4b_gCWeXb6dM6ZxwN8rE6S4ghUsCj2VKR21oEP/pub")

