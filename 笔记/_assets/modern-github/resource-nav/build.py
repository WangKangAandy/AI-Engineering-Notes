import csv
import sys
from html import escape
from pathlib import Path

from catalog import load_resources


def render_page(resources):
    items = []
    for resource in resources:
        title = escape(resource["title"])
        url = escape(resource["url"], quote=True)
        category = escape(resource["category"])
        items.append(f'<li><a href="{url}">{title}</a> <span>({category})</span></li>')
    return (
        '<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Learning Resource Navigator</title></head><body>\n'
        '<h1>学习资源导航</h1>\n<ul>\n'
        + "\n".join(items)
        + "\n</ul>\n</body></html>\n"
    )


def main():
    try:
        resources = load_resources("resources.csv")
        page = render_page(resources)
        output = Path("site")
        output.mkdir(exist_ok=True)
        (output / "index.html").write_text(page, encoding="utf-8")
    except (OSError, ValueError, csv.Error) as error:
        print(f"Build error: {error}", file=sys.stderr)
        return 1
    print(f"Built site/index.html with {len(resources)} resources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
