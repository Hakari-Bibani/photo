import psycopg2
import requests

def update_photo_urls():
    # GitHub API endpoint for listing files in the pictures folder
    api_url = "https://api.github.com/repos/Hakari-Bibani/photo/contents/pictures"
    response = requests.get(api_url)
    
    if response.status_code != 200:
        print("Failed to retrieve images from GitHub.")
        return

    files = response.json()
    
    # Create a dictionary mapping lower-case common names to filenames
    file_mapping = {}
    for f in files:
        filename = f.get("name")
        # Get the name without extension and convert to lowercase
        common_name_from_file = filename.rsplit(".", 1)[0].lower()
        file_mapping[common_name_from_file] = filename

    # Connect to your PostgreSQL database
    conn = psycopg2.connect(
        "postgresql://neondb_owner:npg_YqBVZNepQ18x@ep-orange-bread-a9efjwmt-pooler.gwc.azure.neon.tech/neondb?sslmode=require"
    )
    cur = conn.cursor()

    # Retrieve all rows from the photo table
    cur.execute('SELECT "Common_name " FROM "photo";')
    rows = cur.fetchall()

    for row in rows:
        # Get the common name from the DB row and remove any extra spaces
        common_name_db = row[0].strip()
        common_name_lower = common_name_db.lower()

        # If a file matching the common name exists (case-insensitive), update its URL
        if common_name_lower in file_mapping:
            filename = file_mapping[common_name_lower]
            # Construct the raw URL for the image on GitHub
            raw_url = f"https://raw.githubusercontent.com/Hakari-Bibani/photo/main/pictures/{filename}"
            
            update_query = 'UPDATE "photo" SET " Common_name _url" = %s WHERE lower("Common_name ") = %s;'
            cur.execute(update_query, (raw_url, common_name_lower))
            print(f"Updated '{common_name_db}' with URL: {raw_url}")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    update_photo_urls()
