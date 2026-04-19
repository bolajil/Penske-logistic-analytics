import requests
from bs4 import BeautifulSoup
import re

def decode_message(url):
    # Fetch the document content
    response = requests.get(url)
    html = response.text
    
    # Parse HTML to extract table data
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all table cells
    rows = soup.find_all('tr')
    
    coordinates = []
    max_x, max_y = 0, 0
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 3:
            # Google Docs format: x-coordinate, Character, y-coordinate
            x_text = cells[0].get_text(strip=True)
            char = cells[1].get_text(strip=True)
            y_text = cells[2].get_text(strip=True)
            
            # Skip header row or invalid data
            if not x_text.isdigit() or not y_text.isdigit():
                continue
            
            if not char:
                char = ' '
                
            x, y = int(x_text), int(y_text)
            coordinates.append((char, x, y))
            max_x = max(max_x, x)
            max_y = max(max_y, y)
    
    if not coordinates:
        print("No coordinates found")
        return
    
    # Create the grid filled with spaces
    grid = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]
    
    # Fill the grid with characters
    for char, x, y in coordinates:
        grid[y][x] = char
    
    # Print the grid
    for row in grid:
        print(''.join(row))

if __name__ == "__main__":
    url = "https://docs.google.com/document/d/e/2PACX-1vSvM5gDlNvt7npYHhp_XfsJvuntUhq184By5xO_pA4b_gCWeXb6dM6ZxwN8rE6S4ghUsCj2VKR21oEP/pub"
    decode_message(url)
