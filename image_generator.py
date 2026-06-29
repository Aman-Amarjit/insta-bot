import os
import time
from PIL import Image, ImageDraw, ImageFont
import config

class ImageGenerator:
    def __init__(self):
        self.fonts_dir = "fonts"
        self.bold_font_path = os.path.join(self.fonts_dir, "Inter-Bold.ttf")
        self.regular_font_path = os.path.join(self.fonts_dir, "Inter-Regular.ttf")

    def _ensure_fonts(self):
        """
        Verifies that fonts exist locally. If missing, raises an error.
        """
        if not os.path.exists(self.bold_font_path) or not os.path.exists(self.regular_font_path):
            raise FileNotFoundError(
                f"❌ Fonts not found in '{self.fonts_dir}/'. "
                f"Please ensure Inter-Bold.ttf and Inter-Regular.ttf are committed to the repo."
            )

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list:
        """
        Wraps text into multiple lines so that no line exceeds max_width in pixels.
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            # Calculate pixel width of the test line
            width = draw.textlength(test_line, font=font)
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    # Single word is wider than max_width, force it
                    lines.append(word)
                    current_line = []

        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def render(self, fact_data: dict) -> str:
        """
        Renders a 1080x1080 square image containing the fact text.
        Applies dynamic font scaling, layout centering, and a custom watermark.
        """
        self._ensure_fonts()

        fact_text = fact_data.get("fact", "")
        category = fact_data.get("category", "DID YOU KNOW?").upper()
        # Add spacing to the category title for aesthetics (e.g. S C I E N C E)
        spaced_category = "   ".join(list(category))

        # 1. Initialize canvas (1080x1080) in RGBA mode for transparent watermark drawing
        canvas = Image.new("RGBA", (1080, 1080), (15, 15, 20, 255)) # Dark navy/black solid: #0F0F14
        draw = ImageDraw.Draw(canvas)

        # 2. Draw background gradient (Top to Bottom)
        # From #0F0F14 at top to #0B0B0F at bottom
        for y in range(1080):
            r = int(15 - (4 * y / 1080))
            g = int(15 - (4 * y / 1080))
            b = int(20 - (5 * y / 1080))
            draw.line([(0, y), (1080, y)], fill=(r, g, b, 255))

        # 3. Draw Category Title Header
        # Header is placed at y = 180
        header_font_size = 28
        header_font = ImageFont.truetype(self.bold_font_path, header_font_size)
        
        # Center the header
        header_w = draw.textlength(spaced_category, font=header_font)
        header_x = int((1080 - header_w) / 2)
        header_y = 180
        
        # Draw category title in a soft gray/white
        draw.text((header_x, header_y), spaced_category, font=header_font, fill=(240, 240, 255, 255))

        # Draw a beautiful gradient accent line under the category header
        accent_y = header_y + 60
        accent_w = 120
        accent_x_start = int((1080 - accent_w) / 2)
        # Draw a thin line with color #E1306C (Instagram Pink/Red)
        draw.line(
            [(accent_x_start, accent_y), (accent_x_start + accent_w, accent_y)],
            fill=(225, 48, 108, 255),
            width=3
        )

        # 4. Text Wrapping & Dynamic Font Scaling
        # Safe bounds: padding of 110px on each side -> max width of 860px
        max_text_width = 860
        max_text_height = 500  # Target height to prevent overflowing to watermark
        center_y = 570  # Visual center of the fact text area

        font_sizes = [48, 40, 32, 24]
        selected_font = None
        selected_lines = []
        selected_line_height = 0
        selected_line_spacing = 0

        for size in font_sizes:
            font = ImageFont.truetype(self.bold_font_path, size)
            lines = self._wrap_text(fact_text, font, max_text_width, draw)
            
            # Estimate line metrics
            bbox = font.getbbox("A")
            line_height = bbox[3] - bbox[1]
            line_spacing = int(line_height * 0.4) # 40% spacing between lines
            total_height = len(lines) * line_height + (len(lines) - 1) * line_spacing

            if total_height <= max_text_height or size == font_sizes[-1]:
                selected_font = font
                selected_lines = lines
                selected_line_height = line_height
                selected_line_spacing = line_spacing
                
                # If we are at the minimum font size and it still overflows, truncate
                if size == font_sizes[-1] and total_height > max_text_height:
                    print("⚠️ ImageGenerator warning: Fact text is exceptionally long. Truncating.")
                    # Keep only lines that fit within max_text_height
                    max_allowed_lines = int((max_text_height + selected_line_spacing) / (selected_line_height + selected_line_spacing))
                    if max_allowed_lines > 0:
                        selected_lines = selected_lines[:max_allowed_lines]
                        selected_lines[-1] = selected_lines[-1][:-3] + "..."
                break

        # 5. Draw Wrapped Fact Text centered
        total_text_height = len(selected_lines) * selected_line_height + (len(selected_lines) - 1) * selected_line_spacing
        start_y = int(center_y - total_text_height / 2)

        for i, line in enumerate(selected_lines):
            line_w = draw.textlength(line, font=selected_font)
            line_x = int((1080 - line_w) / 2)
            line_y = start_y + i * (selected_line_height + selected_line_spacing)
            
            # Draw line text in pure white
            draw.text((line_x, line_y), line, font=selected_font, fill=(255, 255, 255, 255))

        # 6. Draw Watermark with specified config opacity
        watermark_text = config.WATERMARK_TEXT
        watermark_opacity = config.WATERMARK_OPACITY
        watermark_font = ImageFont.truetype(self.regular_font_path, 22)
        
        watermark_w = draw.textlength(watermark_text, font=watermark_font)
        watermark_x = int((1080 - watermark_w) / 2)
        watermark_y = 920

        # Draw semi-transparent watermark text
        alpha_color = (255, 255, 255, int(255 * watermark_opacity))
        draw.text((watermark_x, watermark_y), watermark_text, font=watermark_font, fill=alpha_color)

        # 7. Convert RGBA to RGB and save
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)
        filename = f"post_{int(time.time())}.jpg"
        save_path = os.path.join(config.UPLOAD_DIR, filename)
        
        rgb_canvas = canvas.convert("RGB")
        rgb_canvas.save(save_path, "JPEG", quality=95)
        
        return save_path
