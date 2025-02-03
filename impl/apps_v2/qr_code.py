import qrcode
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime

class QrCode:
    def __init__(self):
        self.font = ImageFont.truetype("fonts/tiny.otf", 5)

        self.canvas_width = 64
        self.canvas_height = 64
        self.text_color = (255, 255, 255)
        self.grid_color = (100, 100, 100)

    def generate(self):
        # Get the current time as a string
        current_time = datetime.now().strftime("%H:%M:%S")

        # Generate a QR code for the current time
        qr = qrcode.QRCode(
            version=1,  # Adjust size as needed
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,  # Small box size to fit 64x64 canvas
            border=0    # No border to ensure it fits the canvas
        )
        qr.add_data(current_time)
        qr.make(fit=True)

        # Create an image for the QR code
        qr_image = qr.make_image(fill_color=self.grid_color, back_color="black")

        # Resize the QR code to fit the 64x64 canvas
        qr_image = qr_image.resize((self.canvas_width, self.canvas_height), Image.NEAREST)

        # Create the frame and paste the QR code onto it
        frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
        frame.paste(qr_image, (0, 0))

        return frame

# Example usage
if __name__ == "__main__":
    qr_code = QrCode()
    qr_image = qr_code.generate()
    qr_image.show()
