from PIL import Image, ImageDraw, ImageFont

#https://levelup.gitconnected.com/how-to-properly-calculate-text-size-in-pil-images-17a2cc6f51fd
def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

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

    # Calculate text position (bottom center)
    text_width, text_height = get_text_dimensions(text, font)
    text_x = (image.width - text_width) / 2
    text_y = image.height - text_height - 24  # Adjust as needed

    # Create a separate image for the semi-transparent rectangle
    rect_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
    rect_draw = ImageDraw.Draw(rect_image)

    # Draw a semi-transparent rectangle (80% opacity)
    opacity = int(255 * 0.8)  # 80% opacity
    rect_draw.rectangle([text_x - 8, text_y - 8, text_x + text_width + 8, text_y + text_height + 8], fill=(0, 0, 0, opacity))

    # Blend this rectangle with the base image
    image.paste(rect_image, (0, 0), rect_image)

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

font_path = '/System/Library/Fonts/Helvetica.ttc'

# Call the function
add_text_to_image(image_path, output_path, text, font_path)
