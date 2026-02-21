from enum import Enum

class BlockType(Enum):
    PARAGRAPH     = "paragraph"
    HEADING       = "heading"
    CODE          = "code"
    QUOTE         = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST  = "ordered_list"

def block_to_block_type(block: str) -> BlockType:
    """
    Given a single stripped block of Markdown text, determine its type.
    Returns one of the BlockType enum values.
    """
    lines = block.splitlines()
    if not lines:
        return BlockType.PARAGRAPH  # empty block → treat as paragraph

    first_line = lines[0].strip()

    # 1. Heading: starts with 1–6 # followed by space
    if first_line.startswith("#"):
        count = 0
        for char in first_line:
            if char == "#":
                count += 1
            else:
                break
        if 1 <= count <= 6 and (len(first_line) > count and first_line[count] == " "):
            return BlockType.HEADING

    # 2. Code block: starts with ``` and ends with ```
    if block.startswith("```") and block.endswith("```"):
        # Make sure there's at least one newline after opening ```
        if "\n" in block:
            return BlockType.CODE

    # 3. Quote block: EVERY line starts with > (space after > is optional)
    if all(line.lstrip().startswith(">") for line in lines):
        return BlockType.QUOTE

    # 4. Unordered list: EVERY line starts with - followed by space
    if all(line.lstrip().startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    # 5. Ordered list: EVERY line starts with number. followed by space, starting from 1, incrementing by 1
    if lines and lines[0].lstrip().startswith("1. "):
        is_ordered = True
        expected_num = 1
        for line in lines:
            stripped = line.lstrip()
            if not stripped.startswith(f"{expected_num}. "):
                is_ordered = False
                break
            expected_num += 1
        if is_ordered:
            return BlockType.ORDERED_LIST

    # Default: normal paragraph
    return BlockType.PARAGRAPH

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