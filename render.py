#!/usr/bin/env python3
"""Build the worldtoday-v2 front page and render it to entry.png.

Two stages, both deterministic (no network, no clock, no randomness):

1. Pillow prepares the photo panels in assets/proc/:
   - leaders.jpg: the top banner strip (which carries a wrong "2024"
     caption) is cropped off, keeping the three leaders and their flags.
   - globe.jpg: the engraved globe is cut out as a circle on
     transparency, so it sits on the newsprint like a masthead logo.
   - grid.jpg: the 2x2 contact sheet is split into its four panels,
     inset a few pixels so the white gutters disappear.
   - world.jpg: squished into the wide, short band the reference
     broadsheet uses for its "world at a glance" map.
   - every panel is downscaled to the size it is printed at.

2. Headless Chromium (Playwright's bundled build) opens page.html at
   exactly 1024x1024 and screenshots it to entry.png. If the PNG is
   over the 1 MiB gate, it is re-encoded as JPEG (the rules allow a
   JPEG in entry.png) at the highest quality that fits.

Usage: python3 render.py  (writes entry.png next to this file)
"""

import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
PROC = os.path.join(ASSETS, "proc")
PAGE = os.path.join(HERE, "page.html")
OUT = os.path.join(HERE, "entry.png")
LIMIT = 1048576  # 1 MiB, the competition gate


def load(name):
    return Image.open(os.path.join(ASSETS, name)).convert("RGB")


def save(im, name, quality=90):
    path = os.path.join(PROC, name)
    im.save(path, "JPEG", quality=quality)
    return path


def edge_pad(im, left, top, right, bottom):
    """Pad an image by replicating its edge pixels outward.

    Used to give a photo breathing room inside its print box without
    inventing picture content: the pad is just the edge column/row
    stretched a few pixels, which reads as the scene continuing.
    """
    w, h = im.size
    out = Image.new("RGB", (w + left + right, h + top + bottom))
    out.paste(im, (left, top))
    out.paste(im.crop((0, 0, 1, h)).resize((left, h)), (0, top))
    out.paste(im.crop((w - 1, 0, w, h)).resize((right, h)),
              (left + w, top))
    top_row = out.crop((0, top, out.width, top + 1))
    out.paste(top_row.resize((out.width, top)), (0, 0))
    bot_row = out.crop((0, top + h - 1, out.width, top + h))
    out.paste(bot_row.resize((out.width, bottom)), (0, top + h))
    return out


def prep():
    """Prepare the photo panels. Returns nothing; writes assets/proc/."""
    os.makedirs(PROC, exist_ok=True)

    # --- leaders: tight group portrait (1280x1920). The old crop
    # (0, 550, 1280, 1600) resized to 300x246 did not match the
    # 210x196 print box, so object-fit: cover shaved ~15px off each
    # side and cut ~1/6 of Putin's head (his head starts ~17px from
    # the source's left edge). New crop is exactly the print-box
    # aspect (210:196), full width so nothing is shaved, and the
    # panel is inset on a 420x392 canvas with edge-replicated
    # margins so all three heads sit inside the frame with room.
    leaders = load("leaders.jpg")
    leaders = leaders.crop((0, 500, 1280, 1695))  # 1280x1195
    leaders = leaders.resize((400, 373), Image.LANCZOS)
    leaders = edge_pad(leaders, 10, 9, 10, 10)  # -> 420x392
    save(leaders, "leaders.jpg")

    # --- lead missile photo and Odesa photo. The lead is resized to
    # the exact print-box aspect (384:298) so cover crops nothing:
    # the Kuwait flag drops from ~40% of the frame to ~36% and the
    # flagpole (finial included) is fully visible. (A 1920x1280
    # frame cannot fit a 384x298 box undistorted; this is a ~14%
    # horizontal squeeze, invisible at print size. Any width crop
    # would cut the pole or the Kuwait Towers.)
    lead = load("lead.jpg")
    lead = lead.resize((768, 596), Image.LANCZOS)
    save(lead, "lead.jpg")
    odesa = load("odesa.jpg")
    odesa = odesa.resize((420, 840), Image.LANCZOS)
    save(odesa, "odesa.jpg")

    # --- Meta glass building, full-bleed. The old whole-frame panel
    # (600x400) was shown with object-fit: contain, which letterboxed
    # it with light-blue bars. New crop (100, 0, 1700, 1280) holds
    # the full blue loop plus "Met" (the final "a" runs off the right
    # edge, as in the reference) and is resized to the exact print
    # aspect (200:196), so cover shows it full-bleed with no bars.
    # (1600x1280 -> 400x392 is an ~18% horizontal squeeze; the loop
    # plus the whole word cannot fit a near-square box undistorted.)
    meta = load("meta.jpg")
    meta = meta.crop((100, 0, 1700, 1280))
    meta = meta.resize((400, 392), Image.LANCZOS)
    save(meta, "meta.jpg")
    germany = load("germany.jpg")
    germany = germany.resize((200, 400), Image.LANCZOS)
    save(germany, "germany.jpg")

    # --- globe: cut the engraved circle out of its square sheet.
    globe = load("globe.jpg")
    # The engraved circle spans roughly x 105..1495, y 120..1455.
    globe = globe.crop((105, 120, 1495, 1455))
    globe = globe.resize((420, 404), Image.LANCZOS)
    mask = Image.new("L", globe.size, 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([2, 2, globe.width - 2, globe.height - 2], fill=255)
    circ = Image.new("RGBA", globe.size, (0, 0, 0, 0))
    circ.paste(globe, (0, 0), mask)
    circ.save(os.path.join(PROC, "globe.png"), "PNG")

    # --- bottom grid: split the 2x2 sheet into four panels, inset so
    # the white gutters between the panels are gone. The COP31 panel
    # is cropped to the full stage: the "COP31 BRASIL" lettering
    # spans x 1426..1912 of the sheet (screen x 1306..2032), so the
    # window (1399, 8, 1939, 547) holds the whole line with ~27px
    # margins, plus ceiling above and audience below, and is resized
    # to the exact print-box aspect (92:124) so cover crops nothing.
    # (A 540x539 window into a 92x124 box is a ~26% horizontal
    # squeeze: the 486px-wide line cannot fit a 0.74-aspect box
    # undistorted, the panel is only 539px tall. The old crop
    # (1123, 60, 1560, 547) held only "COP" and cover shaved more,
    # leaving just "CO".)
    grid = load("grid.jpg")
    w, h = grid.size  # 2240 x 1120
    panels = {
        "voyager.jpg": ((8, 8, 1107, 547), (440, 216)),
        "cop31.jpg": ((1399, 8, 1939, 547), (184, 248)),
        "iceberg.jpg": ((8, 563, 1107, 1112), (440, 216)),
        "fuji.jpg": ((1123, 563, 2232, 1112), (440, 216)),
    }
    for name, (box, size) in panels.items():
        panel = grid.crop(box)
        panel = panel.resize(size, Image.LANCZOS)
        save(panel, name)

    # --- world map: squash the equirectangular satellite view into
    # the wide short band of the reference (560 x 100).
    world = load("world.jpg")
    world = world.resize((560, 100), Image.LANCZOS)
    save(world, "world-band.jpg", quality=88)


def render():
    """Screenshot page.html at 1024x1024 with headless Chromium."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1024, "height": 1024},
                                device_scale_factor=1)
        page.goto("file://" + PAGE)
        page.wait_for_load_state("load")
        page.wait_for_timeout(400)
        page.screenshot(path=OUT, full_page=False)
        browser.close()
    return OUT


def fit_size(path):
    """If the screenshot is over the 1 MiB gate, re-encode as JPEG
    (allowed: the file is told apart by its first bytes) at the
    highest quality that fits, stepping down deterministically."""
    size = os.path.getsize(path)
    if size <= LIMIT:
        return size, "PNG"
    im = Image.open(path).convert("RGB")
    for quality in (92, 88, 84, 80, 76, 72):
        im.save(path, "JPEG", quality=quality)
        size = os.path.getsize(path)
        if size <= LIMIT:
            return size, "JPEG q%d" % quality
    return size, "JPEG q72 (STILL OVER LIMIT)"


def main():
    prep()
    render()
    im = Image.open(OUT)
    size, kind = fit_size(OUT)
    print("wrote %s %s %dx%d %d bytes" % (OUT, kind, im.width, im.height,
                                          size))
    if im.size != (1024, 1024):
        print("ERROR: entry.png is not 1024x1024", file=sys.stderr)
        sys.exit(1)
    if size > LIMIT:
        print("ERROR: entry.png is over 1 MiB", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
