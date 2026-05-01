from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from io import BytesIO
import urllib.request
import json
import base64

FIREBASE_BASE = "https://bsg-7772d-default-rtdb.firebaseio.com"
W, H = 1200, 630

BG        = (248, 250, 252)   # slate-50
SURFACE   = (255, 255, 255)   # white card
NAVY      = (26,  40,  68)    # text principal
BLUE      = (45,  91,  227)   # acento
BLUE_SOFT = (238, 242, 255)   # fondo badge
MUTED     = (100, 116, 139)   # slate-500
BORDER    = (226, 232, 240)   # slate-200
URL_COLOR = (45,  91,  227)


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

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    font_title  = _load_font(FONT_PATHS,     68)
    font_sub    = _load_font(FONT_PATHS_REG, 34)
    font_tag    = _load_font(FONT_PATHS,     22)
    font_small  = _load_font(FONT_PATHS_REG, 26)

    # White card (center area)
    card_x, card_y = 64, 60
    card_w, card_h = W - 128, 430
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=24, fill=SURFACE, outline=BORDER, width=2
    )

    # Logo or fallback square
    logo_size = 110
    logo_x, logo_y = card_x + 52, card_y + (card_h - logo_size) // 2
    if logo_b64:
        try:
            b64_data = logo_b64.split(",")[1] if "," in logo_b64 else logo_b64
            logo_bytes = base64.b64decode(b64_data)
            logo_img = Image.open(BytesIO(logo_bytes)).convert("RGBA")
            logo_img.thumbnail((logo_size, logo_size), Image.LANCZOS)
            lw, lh = logo_img.size
            bg = Image.new("RGBA", (logo_size, logo_size), (255, 255, 255, 255))
            bg.paste(logo_img, ((logo_size - lw) // 2, (logo_size - lh) // 2), logo_img)
            mask = Image.new("L", (logo_size, logo_size), 0)
            from PIL import ImageDraw as ID2
            m = ID2.Draw(mask)
            m.rounded_rectangle([0, 0, logo_size, logo_size], radius=16, fill=255)
            img.paste(bg.convert("RGB"), (logo_x, logo_y), mask)
        except Exception:
            logo_b64 = None

    if not logo_b64:
        draw.rounded_rectangle(
            [logo_x, logo_y, logo_x + logo_size, logo_y + logo_size],
            radius=16, fill=BLUE_SOFT
        )
        draw.text(
            (logo_x + logo_size // 2, logo_y + logo_size // 2),
            "$", font=font_title, fill=BLUE, anchor="mm"
        )

    # Text block
    text_x = logo_x + logo_size + 48
    text_mid_y = card_y + card_h // 2

    draw.text((text_x, text_mid_y - 68), "Tesoreros App",
              font=font_title, fill=NAVY, anchor="lm")
    draw.text((text_x, text_mid_y + 8), "Plataforma de gestión para delegados y",
              font=font_sub, fill=MUTED, anchor="lm")
    draw.text((text_x, text_mid_y + 52), "tesoreros de colegios.",
              font=font_sub, fill=MUTED, anchor="lm")

    # Feature tags row
    tags = ["Cuotas", "Actividades", "Pagos", "Reportes"]
    tag_x = card_x + 52
    tag_y = card_y + card_h - 58
    pad_x, pad_y, r = 18, 8, 12
    for tag in tags:
        bbox = font_tag.getbbox(tag)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        bw = tw + pad_x * 2
        bh = th + pad_y * 2
        draw.rounded_rectangle(
            [tag_x, tag_y, tag_x + bw, tag_y + bh],
            radius=r, fill=BLUE_SOFT
        )
        draw.text((tag_x + pad_x, tag_y + pad_y - bbox[1]), tag,
                  font=font_tag, fill=BLUE)
        tag_x += bw + 12

    # Bottom URL bar
    bar_y = H - 80
    draw.rectangle([0, bar_y, W, H], fill=NAVY)
    draw.text((80, bar_y + 40), "tesoreros-app.vercel.app",
              font=font_small, fill=(148, 163, 184), anchor="lm")

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
