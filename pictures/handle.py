import os
import psycopg2

# Database connection string (you might want to store this in an environment variable)
DB_URL = "postgresql://neondb_owner:npg_YqBVZNepQ18x@ep-orange-bread-a9efjwmt-pooler.gwc.azure.neon.tech/neondb?sslmode=require"

# Directory containing the pictures in your repo
PICTURES_DIR = "photo/pictures"

# Base URL for the raw images in your GitHub repository (adjust branch if needed)
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Hakari-Bibani/photo/main/photo/pictures/"

def update_photo_url(cursor, file_name):
    """
    Extract the common name from the file name (ignoring case and extension)
    and update the corresponding row in the database with the image URL.
    """
    # Remove extension and whitespace, then convert to lowercase
    common_name = os.path.splitext(file_name)[0].strip().lower()
    image_url = GITHUB_RAW_BASE + file_name

    # Use a case-insensitive match on the "Common_name " column in the table.
    # Note: The column names have extra spaces. Make sure to include them exactly.
    update_query = """
    UPDATE "public"."photo"
    SET " Common_name _url" = %s
    WHERE LOWER(TRIM("Common_name ")) = %s
    """
    cursor.execute(update_query, (image_url, common_name))

def main():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Process all images in the designated directory
        for file in os.listdir(PICTURES_DIR):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                update_photo_url(cursor, file)
                print(f"Updated {file} -> {GITHUB_RAW_BASE + file}")
        
        # Commit all updates
        conn.commit()
    except Exception as e:
        print("Error:", e)
    finally:
        # Clean up and close the connection
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()

