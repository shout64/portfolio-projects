import requests
from bs4 import BeautifulSoup

def parse_tables(published_url):
    try:
        response = requests.get(published_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tables = soup.find_all("table")
        if not tables:
            raise Exception("No tables found.")
        
        for table in tables:
            current_table_data = []
            rows = table.find_all('tr')

            for row in rows:
                row_data = []
                cells = row.find_all(["th", "td"])

                for cell in cells:
                    cell_text = cell.get_text(separator=" ", strip=True)
                    row_data.append(cell_text)

                current_table_data.append(row_data)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {published_url}: {e}")
        return None

    max_x = 0
    max_y = 0

    for row in current_table_data[1:]:
        x = int(row[0])
        y = int(row[2])

        if x > max_x:
            max_x = x

        if y > max_y:
            max_y = y

    grid = [[" " for i in range(max_x + 1)] for j in range(max_y + 1) ]

    for row in current_table_data[1:]:
        x    = int(row[0])
        y    = max_y - int(row[2])
        char = row[1]

        grid[y][x] = char

    output_lines = ["".join(row) for row in grid]
    output_string = "\n".join(output_lines)

    print(output_string)

sample_doc = "https://docs.google.com/document/d/e/some_document_id/pub"

parse_tables(sample_doc)
