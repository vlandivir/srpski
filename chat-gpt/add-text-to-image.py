from PIL import Image, ImageDraw, ImageFont

def add_text_to_image(image_path, output_path, text, font_path, font_size=48):
    """
    Adds text to an image and saves the result.

    Parameters:
    - image_path: path to the input image.
    - output_path: path where the output image will be saved.
    - text: the text to add to the image.
    - font_path: path to the .ttf or .otf font file.
    - font_size: size of the font to use.
    """
    # Load the image
    image = Image.open(image_path)

    # Initialize the drawing context
    draw = ImageDraw.Draw(image)

    # Load the font
    font = ImageFont.truetype(font_path, font_size)
    print(font.getsize(text))


    # Calculate text position (bottom center)
    # text_width, text_height = draw.textsize(text, font=font)
    # text_x = (image.width - text_width) / 2
    # text_y = image.height - text_height - 10  # Adjust as needed

    text_x = 0
    text_y = 0

    # Specify text color (change as needed)
    text_color = "white"

    # Add the text to the image
    draw.text((text_x, text_y), text, fill=text_color, font=font)

    # Save the image
    image.save(output_path)

# Example usage
image_path = 'Pričao_sam_sa_satovima_na_zidu_o_vremenu.webp'  # Update this path
output_path = 'Pričao_sam_sa_satovima_na_zidu_o_vremenu_output.webp'  # Update this path
text = "Pričao sam sa satovima na zidu o vremenu"

# font_path = 'path_to_your_font.ttf'  # Update this path with a font that supports Serbian characters
font_path = '/System/Library/Fonts/Geneva.ttf'

# Call the function
add_text_to_image(image_path, output_path, text, font_path)
