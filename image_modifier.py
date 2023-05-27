def generate_composite_image_background_position(
    background_image, overlay_image, position
):
    if position < 1 or position > 6:
        raise ValueError("Invalid position. Position must be between 1 and 6.")

    composite_width = background_image.width
    composite_height = background_image.height
    composite_image = background_image.copy()

    overlay_width = composite_width // 2
    overlay_height = composite_height // 3
    resized_overlay = overlay_image.resize((overlay_width, overlay_height))

    row = (position - 1) // 2
    col = (position - 1) % 2

    paste_x = col * overlay_width
    paste_y = row * overlay_height

    composite_image.paste(resized_overlay, (paste_x, paste_y))

    return composite_image
