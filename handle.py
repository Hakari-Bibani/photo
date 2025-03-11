import os
import psycopg2

# Retrieve connection string from environment variable for security.
conn_str = os.environ.get("CONNECTION_STRING")
if not conn_str:
    raise ValueError("Please set the CONNECTION_STRING environment variable.")

# Directory where the pictures are stored
pictures_dir = "photo/pictures"

# Base URL for images in your GitHub repo
url_base = "https://github.com/Hakari-Bibani/photo/blob/main/pictures/"

def update_db(common_name, file_name):
    """Update the database row for a given common name with the image URL."""
    try:
        # Construct full URL
        url = url_base + file_name
        
        # Connect to your Neon PostgreSQL database
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()
        
        # SQL: update the row matching common name (case-insensitive)
        query = """
        UPDATE public.photo
        SET Common_name_url = %s
        WHERE LOWER(Common_name) = LOWER(%s)
        """
        cursor.execute(query, (url, common_name))
        conn.commit()
        
        print(f"Updated '{common_name}' with URL: {url}")
    except Exception as e:
        print(f"Error updating '{common_name}': {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    # List all image files in the pictures directory
    for file_name in os.listdir(pictures_dir):
        if file_name.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
            # Remove the file extension to get the common name
            common_name = os.path.splitext(file_name)[0]
            update_db(common_name, file_name)

if __name__ == "__main__":
    main()
