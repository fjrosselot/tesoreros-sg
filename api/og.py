from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from io import BytesIO
import urllib.request
import json
import base64

FIREBASE_BASE = "https://bsg-7772d-default-rtdb.firebaseio.com"
W, H = 1200, 630
NAVY = (26, 35, 64)
NAVY_DARK = (22, 29, 52)
NAVY_BOTTOM = (22, 45, 74)
BLUE = (45, 91, 227)
WHITE = (255, 255, 255)
MUTED = (168, 196, 224)
MUTED2 = (123, 168, 204)
BOTTOM_BG = (22, 45, 74)
URL_COLOR = (90, 143, 194)

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
]
FONT_PATHS_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]


def _load_font(paths, size):
    from PIL import ImageFont
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _fetch_logo_b64(colegio_id):
    try:
        url = FIREBASE_BASE + "/plataforma/colegios/" + colegio_id + "/logoBase64.json"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data and isinstance(data, str):
                return data
    except Exception:
        pass
    return None


def _build_image(logo_b64):
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Subtle top gradient
    for y in range(160):
        t = y / 160
        r = int(NAVY[0] * (1 - t) + NAVY_DARK[0] * t)
        g = int(NAVY[1] * (1 - t) + NAVY_DARK[1] * t)
        b = int(NAVY[2] * (1 - t) + NAVY_DARK[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    font_title = _load_font(FONT_PATHS, 74)
    font_med = _load_font(FONT_PATHS_REG, 37)
    font_small = _load_font(FONT_PATHS_REG, 28)

    logo_x, logo_y, logo_size = 80, 55, 130

    # Logo or fallback circle
    if logo_b64:
        try:
            b64_data = logo_b64.split(",")[1] if "," in logo_b64 else logo_b64
            logo_bytes = base64.b64decode(b64_data)
            logo_img = Image.open(BytesIO(logo_bytes)).convert("RGBA")
            logo_img.thumbnail((logo_size, logo_size), Image.LANCZOS)
            lw, lh = logo_img.size
            bg = Image.new("RGBA", (logo_size, logo_size), (255, 255, 255, 255))
            offset_x = (logo_size - lw) // 2
            offset_y = (logo_size - lh) // 2
            bg.paste(logo_img, (offset_x, offset_y), logo_img)
            bg_round = bg.convert("RGB")
            # Rounded mask
            mask = Image.new("L", (logo_size, logo_size), 0)
            from PIL import ImageDraw as ID2
            m = ID2.Draw(mask)
            m.rounded_rectangle([0, 0, logo_size, logo_size], radius=18, fill=255)
            img.paste(bg_round, (logo_x, logo_y), mask)
        except Exception:
            logo_b64 = None

    if not logo_b64:
        draw.rounded_rectangle([logo_x, logo_y, logo_x + logo_size, logo_y + logo_size], radius=18, fill=BLUE)
        draw.text((logo_x + logo_size // 2, logo_y + logo_size // 2), "$", font=font_title, fill=WHITE, anchor="mm")

    text_x = logo_x + logo_size + 28
    draw.text((text_x, logo_y + logo_size // 2), "Tesoreros App", font=font_title, fill=WHITE, anchor="lm")

    draw.line([(80, 230), (W - 80, 230)], fill=BLUE, width=2)

    draw.text((80, 285), "Plataforma de gestión para delegados y tesoreros de colegios.", font=font_med, fill=MUTED, anchor="lm")
    draw.text((80, 345), "Cuotas  ·  Actividades  ·  Pagos  ·  Reportes", font=font_med, fill=MUTED2, anchor="lm")

    draw.rectangle([0, 570, W, H], fill=BOTTOM_BG)
    draw.text((80, 600), "tesoreros-app.vercel.app", font=font_small, fill=URL_COLOR, anchor="lm")

    return img


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        colegio_id = params.get("colegio", ["sg"])[0]

        logo_b64 = _fetch_logo_b64(colegio_id)
        img = _build_image(logo_b64)

        buf = BytesIO()
        img.save(buf, "PNG", optimize=True)
        png_data = buf.getvalue()

        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Cache-Control", "public, max-age=3600, stale-while-revalidate=86400")
        self.send_header("Content-Length", str(len(png_data)))
        self.end_headers()
        self.wfile.write(png_data)

    def log_message(self, *args):
        pass
