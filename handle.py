import psycopg2
import requests

# Replace with your real connection string
DB_CONNECTION = "postgresql://neondb_owner:npg_YqBVZNepQ18x@ep-orange-bread-a9efjwmt-pooler.gwc.azure.neon.tech/neondb?sslmode=require"

def update_photo_links():
    """
    1. Fetches the list of files (images) under the GitHub folder: 
       https://github.com/Hakari-Bibani/photo/tree/main/pictures
    2. For each image, derives the 'common_name' from the file name (strips extension).
    3. Upserts (INSERT ... ON CONFLICT) into table 'photo' so that:
         - "Common_name " = derived common name
         - " Common_name _url" = raw GitHub link
    """
    # 1. Connect to the PostgreSQL database
    conn = psycopg2.connect(DB_CONNECTION)
    cur = conn.cursor()

    # 2. Make a request to the GitHub API to list contents in /pictures
    github_api_url = "https://api.github.com/repos/Hakari-Bibani/photo/contents/pictures"
    response = requests.get(github_api_url)
    if response.status_code != 200:
        raise Exception(f"GitHub API request failed with status {response.status_code}")
    
    files_data = response.json()  # This should be a list of items if the repo is public and path is correct

    for file_info in files_data:
        # Each item in files_data might be a directory or file
        if file_info['type'] == 'file':
            file_name = file_info['name']         # e.g. "Cypress.jpg"
            
            # Derive common_name by removing the extension
            # e.g. "Cypress.jpg" -> "Cypress"
            if '.' in file_name:
                common_name_value = file_name.rsplit('.', 1)[0]
            else:
                common_name_value = file_name

            # You can use the download_url field from the GitHub API JSON
            # Alternatively, you could build a raw link like:
            #   f"https://raw.githubusercontent.com/Hakari-Bibani/photo/main/pictures/{file_name}"
            # But the API's download_url is typically fine.
            photo_url = file_info['download_url']  

            # 3. Upsert the record into the "photo" table
            #    NOTE: Pay special attention to the double quotes and spacing:
            upsert_query = """
                INSERT INTO "photo"("Common_name ", " Common_name _url")
                VALUES (%s, %s)
                ON CONFLICT ("Common_name ")
                DO UPDATE SET " Common_name _url" = EXCLUDED." Common_name _url";
            """
            cur.execute(upsert_query, (common_name_value, photo_url))
    
    # Commit once after all inserts/updates
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    # Simply call the function to perform the update
    update_photo_links()
    print("Photo links updated successfully!")
