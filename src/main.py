from textnode import TextNode, TextType, extract_markdown_images, extract_markdown_links

import os 
import shutil

def copy_directory(src: str, dest: str) -> None:
    """
    Recursively copy everything from src directory to dest directory.
    - Deletes all existing content in dest first
    - Creates dest if it doesn't exist
    - Prints each file/folder it copies
    """
    # Step 1: Delete everything in dest (if it exists)
    if os.path.exists(dest):
        print(f"Deleting existing contents of {dest}...")
        shutil.rmtree(dest)
    
    # Step 2: Create the destination directory
    os.makedirs(dest, exist_ok=True)
    print(f"Created destination directory: {dest}")

    # Step 3: Walk through source recursively
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dest_path = os.path.join(dest, item)

        if os.path.isdir(src_path):
            # It's a directory → recurse!
            print(f"Copying directory: {src_path} → {dest_path}")
            copy_directory(src_path, dest_path)
        
        elif os.path.isfile(src_path):
            # It's a file → copy it
            print(f"Copying file: {src_path} → {dest_path}")
            shutil.copy2(src_path, dest_path)
        
        else:
            print(f"Skipping unusual item: {src_path}")

    print(f"Finished copying {src} to {dest}")



def main():
   # Make sure public/ exists (or will be created)
    public_dir = "public"
    static_dir = "static"

    print("Starting SSG build...")

    # Copy static assets to public/
    copy_directory(static_dir, public_dir)

    print("Build complete! Check the 'public' folder.")

if __name__ == "__main__":
    main()