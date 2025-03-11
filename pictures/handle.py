import os
import psycopg2
import logging

# Configure logging to output to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Retrieve database URL from environment variable or fallback (for testing only)
DB_URL = os.getenv("DB_URL", "postgresql://neondb_owner:npg_YqBVZNepQ18x@ep-orange-bread-a9efjwmt-pooler.gwc.azure.neon.tech/neondb?sslmode=require")

# Directory containing the pictures in your repo
PICTURES_DIR = os.path.join("photo", "pictures")

# Base URL for the raw images in your GitHub repository
# Adjust branch if needed (e.g., 'main' or 'master')
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Hakari-Bibani/photo/main/photo/pictures/"

def update_photo_url(cursor, file_name):
    """
    Extract the common name from the file name (ignoring case and extension)
    and update the corresponding row in the database with the image URL.
    """
    # Remove extension and whitespace, then convert to lowercase
    common_name = os.path.splitext(file_name)[0].strip().lower()
    image_url = GITHUB_RAW_BASE + file_name
    logging.info(f"Processing file: {file_name} (common name: '{common_name}') with URL: {image_url}")

    update_query = """
    UPDATE "public"."photo"
    SET " Common_name _url" = %s
    WHERE LOWER(TRIM("Common_name ")) = %s
    """
    cursor.execute(update_query, (image_url, common_name))
    logging.info(f"Rows affected for '{common_name}': {cursor.rowcount}")

def main():
    try:
        # Connect to the PostgreSQL database
        logging.info("Connecting to the database...")
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        logging.info("Connected to the database.")

        # Process all image files in the designated directory
        if not os.path.exists(PICTURES_DIR):
            logging.error(f"Directory {PICTURES_DIR} does not exist.")
            return

        files_found = False
        for file in os.listdir(PICTURES_DIR):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                files_found = True
                update_photo_url(cursor, file)
        if not files_found:
            logging.warning("No image files found in the pictures directory.")
        else:
            conn.commit()
            logging.info("Database updates committed.")
    except Exception as e:
        logging.error("An error occurred:", exc_info=True)
    finally:
        try:
            cursor.close()
            conn.close()
            logging.info("Database connection closed.")
        except Exception as close_err:
            logging.error("Error closing database connection:", exc_info=True)

if __name__ == '__main__':
    main()
