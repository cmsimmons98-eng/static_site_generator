
import os 
import shutil

from textnode import TextNode, TextType, extract_markdown_images, extract_markdown_links
from block_parsing import markdown_to_html_node, extract_title

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

def generate_page(from_path: str, template_path: str, dest_path: str) -> None:
    """
    Generate one HTML page from a Markdown file using a template.
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    # Read Markdown file
    with open(from_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    # Read template file
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Convert Markdown to HTML string
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()

    # Get page title
    title = extract_title(markdown_content)

    # Replace placeholders
    full_html = template.replace("{{ Title }}", title)
    full_html = full_html.replace("{{ Content }}", html_content)

    # Create directories if needed and write the file
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"Page generated: {dest_path}")

def generate_pages_recursive(dir_path_content: str, template_path: str, dest_dir_path: str) -> None:
    """
    Recursively find all .md files in dir_path_content and generate HTML pages in dest_dir_path.
    Preserves the folder structure.
    """
    # List everything in the current content directory
    entries = os.listdir(dir_path_content)

    for entry in entries:
        content_path = os.path.join(dir_path_content, entry)
        dest_path = os.path.join(dest_dir_path, entry)

        if os.path.isfile(content_path):
            # It's a file
            if entry.endswith(".md"):
                # Markdown file → generate HTML
                # Replace .md with .html in destination
                html_dest = dest_path[:-3] + ".html"  # remove .md, add .html
                print(f"Generating page: {content_path} → {html_dest}")
                generate_page(content_path, template_path, html_dest)
            else:
                print(f"Skipping non-markdown file: {content_path}")

        elif os.path.isdir(content_path):
            # It's a directory → create matching dir in public and recurse
            print(f"Entering directory: {content_path}")
            os.makedirs(dest_path, exist_ok=True)
            generate_pages_recursive(content_path, template_path, dest_path)
        
def main():
    print("Starting SSG build...")

    # Copy static assets
    copy_directory("static", "public")

    # Generate ALL pages recursively from content/
    generate_pages_recursive(
        dir_path_content="content",
        template_path="template.html",
        dest_dir_path="public"
    )

    print("Build complete! Run the server next.")

if __name__ == "__main__":
    main()