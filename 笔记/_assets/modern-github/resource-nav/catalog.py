import csv
import sys
from pathlib import Path
from urllib.parse import urlsplit


def load_resources(path):
    resources = []
    seen_urls = set()
    with Path(path).open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        if reader.fieldnames != ["title", "url", "category"]:
            raise ValueError("Header must be title,url,category")
        for raw in reader:
            if None in raw or any(value is None for value in raw.values()):
                raise ValueError(f"Line {reader.line_num}: expected exactly three fields")
            row = {key: value.strip() for key, value in raw.items()}
            if any(not value for value in row.values()):
                raise ValueError(f"Line {reader.line_num}: fields must not be blank")
            address = urlsplit(row["url"])
            if address.scheme not in {"http", "https"} or not address.hostname:
                raise ValueError(f"Line {reader.line_num}: expected an absolute HTTP(S) URL")
            if row["url"] in seen_urls:
                raise ValueError(f"Line {reader.line_num}: duplicate URL")
            seen_urls.add(row["url"])
            resources.append(row)
    if not resources:
        raise ValueError("Catalog must contain at least one resource")
    return resources


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "resources.csv"
    try:
        resources = load_resources(path)
    except (OSError, ValueError, csv.Error) as error:
        print(f"Catalog error: {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(resources)} resources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
