def build_svg_style(svg_class, text_classes):
    css = ""

    if svg_class:
        css += f"""
.{svg_class} {{
  position: absolute;
  top: 8;
  left: 4;
  transform-origin: top left;
  pointer-events: none;
}}
"""

    for c in text_classes:
        css += f"""
.{c} {{
  user-select: text;
  -webkit-user-select: text;
  pointer-events: auto;
  fill: rgba(0,0,0,0.01);
}}
"""

    return css


def wrap_page(content, svg_style):
    return f"""
<html>
<body>
<style>
{svg_style}
</style>
{content}
</body>
</html>
"""

# ordina pagine
def page_id(p):
    import re
    m = re.search(r"pageContainer(\d+)", p.get("id",""))
    return int(m.group(1)) if m else 0

pages = sorted(pages, key=page_id)

def extract_single_svg_class(page):
    svg = page.find("svg")
    if not svg:
        return None

    cls = svg.get("class")

    if not cls:
        return None

    if isinstance(cls, list):
        return cls[0]

    return cls

def extract_svg_text_classes(page):
    svg = page.find("svg")
    if not svg:
        return set()

    text_elements = svg.find_all("text")
    classes = set()

    for t in text_elements:
        cls = t.get("class")
        if not cls:
            continue

        if isinstance(cls, list):
            classes.update(cls)
        else:
            classes.add(cls)

    return classes
