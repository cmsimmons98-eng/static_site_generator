def markdown_to_blocks(markdown: str) -> list[str]:
    """
    Splits a full Markdown document into block strings.
    Blocks are separated by blank lines (two consecutive newlines).
    
    Returns a list of stripped block strings with no empty entries.
    """
    # Split on double newlines (the main block separator in Markdown)
    raw_blocks = markdown.split("\n\n")
    
    # Clean each block and remove empties
    blocks = []
    for block in raw_blocks:
        cleaned = block.strip()           # remove leading/trailing whitespace
        if cleaned:                       # skip if it's now empty
            blocks.append(cleaned)
    
    return blocks