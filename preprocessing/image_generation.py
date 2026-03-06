from PIL import Image, ImageDraw, ImageFont # Image - Creates and manages image files , Draws text/shapes on a image , loads and manages fonts
import textwrap # for wrapping long text into shorter lines 


def text_to_images(text, font_path=None, font_size=20, margin=50, dpi=72):
    """
    Converts text into A4 images (210mm x 297mm) and spreads long text across multiple images.

    Args:
        text (str): The input text to convert.
        font_path (str, optional): Path to a TTF font file. Defaults to PIL default font.
        font_size (int, optional): Font size in points. Defaults to 20.
        margin (int, optional): Margin around the text in pixels. Defaults to 50.

    Returns:
        list: A list of generated PIL Image objects.
    """
    # Define A4 size in pixels
    a4_width_px = int(8.27 * dpi)
    a4_height_px = int(11.69 * dpi)

    # Load font
    try:
        font = ImageFont.truetype(font_path or "arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Compute max width for text
    max_height = a4_height_px - 2 * margin

    # Wrap text
    wrapped_text = []
    for paragraph in text.split("\n"):
        lines = textwrap.wrap(paragraph, width=80)
        wrapped_text.extend(lines + [""])  # Add empty line after paragraph

    # Calculate line height
    line_height = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]  # + 5  # Add spacing
    max_lines_per_page = max_height // line_height

    # Create images
    images = []
    for i in range(0, len(wrapped_text), max_lines_per_page): # Loops through wrapped lines in chunks of max_lines_per_page Each iteration = one page/image
        img = Image.new("RGB", (a4_width_px, a4_height_px), "white") # Blank White A4 image
        draw = ImageDraw.Draw(img)
        y = margin

        for line in wrapped_text[i : i + max_lines_per_page]:
            draw.text((margin, y), line, font=font, fill="black")
            y += line_height

        images.append(img)

    return images
