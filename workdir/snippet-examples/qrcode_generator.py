import qrcode
from PIL import Image, ImageDraw, ImageFont
from qrcode.main import QRCode

# Data to encode in the QR code
oscillator_module_passport_urn = (
    "urn:manufacturer:TNO:03556607-ef11-4c8d-b28f-4b4e65f011fb"
)
power_group_passport_urn = (
    "urn:manufacturer:Elenco:3ee8ba6d-9af0-457f-9552-adb368be098f"
)

# Create a basic QR code
qr = QRCode(
    version=1,
    error_correction=qrcode.ERROR_CORRECT_H,
    box_size=15,  # Increased box size for higher resolution
    border=4,
)
qr.add_data(power_group_passport_urn)
qr.make(fit=True)

# Create an image from the QR code instance
qr_img = qr.make_image(fill_color="black", back_color="white")

# Convert QR code image to a PIL image
qr_img = qr_img.convert("RGBA")

# # Add larger text inside the QR code
# draw = ImageDraw.Draw(qr_img)
# text = "Your Text"

# # Use the default font
# font = ImageFont.load_default()

# # Scale up the text by drawing it multiple times
# scale_factor = 3  # Change this factor to increase or decrease the text size

# # Calculate text size and position
# text_bbox = draw.textbbox((0, 0), text, font=font)
# text_width = (text_bbox[2] - text_bbox[0]) * scale_factor
# text_height = (text_bbox[3] - text_bbox[1]) * scale_factor

# # Position the text in the center
# img_width, img_height = qr_img.size
# text_position = ((img_width - text_width) // 2, (img_height - text_height) // 2)

# # Draw a rectangle for the text background
# rect_x0 = text_position[0] - 5
# rect_y0 = text_position[1] - 5
# rect_x1 = text_position[0] + text_width + 5
# rect_y1 = text_position[1] + text_height + 5
# draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill="white")

# # Add the text on top of the rectangle multiple times to simulate a larger font
# for x in range(scale_factor):
#     for y in range(scale_factor):
#         draw.text(
#             (text_position[0] + x, text_position[1] + y),
#             text,
#             fill="black",
#             font=font,
#         )

# # Optionally, draw a line inside the QR code
# # Line coordinates
# line_x0, line_y0 = 0, img_height // 2
# line_x1, line_y1 = img_width, img_height // 2
# draw.line([line_x0, line_y0, line_x1, line_y1], fill="black", width=3)

# Save the final image
qr_img.save("PowerGroupPassport.png")
