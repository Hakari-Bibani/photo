import os
import psycopg2

# Base URL for your GitHub repository images.
GITHUB_BASE_URL = "https://github.com/Hakari-Bibani/photo/blob/main/pictures"
# Directory path for your images.
# This script expects the pictures to be available locally.
# If you are syncing your repository on an online server, adjust this path accordingly.
PICTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photo", "pictures")

# Neon PostgreSQL online connection string
CONNECTION_STRING = (
    "postgresql://neondb_owner:npg_YqBVZNepQ18x@"
    "ep-orange-bread-a9efjwmt-pooler.gwc.azure.neon.tech/neondb?sslmode=require"
)

def update_common_name_url(conn, common_name, url):
    """
    Update the Common_name_url column for the given common_name (case-insensitive).
    """
    try:
        with conn.cursor() as cursor:
            # Use lower() on both sides to ensure case-insensitive matching.
            sql = """
            UPDATE "public"."photo"
            SET "Common_name_url" = %s
            WHERE lower("Common_name") = lower(%s)
            """
            cursor.execute(sql, (url, common_name))
        conn.commit()
        print(f"Updated {common_name} with URL: {url}")
    except Exception as e:
        print(f"Error updating {common_name}: {e}")
        conn.rollback()

def process_images():
    # Connect to the Neon online database.
    try:
        conn = psycopg2.connect(CONNECTION_STRING)
        print("Connected to Neon database successfully.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return

    try:
        # Process each file in the pictures directory.
        for filename in os.listdir(PICTURES_DIR):
            # Check for common image file extensions.
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff")):
                # Extract the common name (filename without extension).
                common_name, _ = os.path.splitext(filename)
                # Construct the image URL.
                image_url = f"{GITHUB_BASE_URL}/{filename}"
                # Update the record in the online Neon database.
                update_common_name_url(conn, common_name, image_url)
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    process_images()
