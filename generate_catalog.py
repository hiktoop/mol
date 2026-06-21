#!/usr/bin/env python3
"""
generate_catalog.py
扫描 books/*.json，生成 OPDS 1.2 格式的 catalog.xml
用法：python generate_catalog.py
输出：catalog.xml（放到 gh-pages 根目录）
"""

import json
import os
import glob
from datetime import datetime, timezone
from xml.dom import minidom
import xml.etree.ElementTree as ET

# ── 配置 ──────────────────────────────────────────────────────────────
SITE_URL = "https://hiktoop.github.io/mol"  # GitHub Pages 地址
LIBRARY_TITLE = "mol - 我的书库"
LIBRARY_AUTHOR = "hiktoop"
LIBRARY_ID = "urn:uuid:mol-opds-library-hiktoop"
# ─────────────────────────────────────────────────────────────────────


def load_books():
    """读取所有 books/*.json"""
    books = []
    for path in sorted(glob.glob("books/*.json")):
        with open(path, encoding="utf-8") as f:
            book = json.load(f)
            books.append(book)
    return books


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_feed(books):
    # 命名空间
    NS = {
        "": "http://www.w3.org/2005/Atom",
        "opds": "http://opds-spec.org/2010/catalog",
        "dcterms": "http://purl.org/dc/terms/",
    }
    for prefix, uri in NS.items():
        ET.register_namespace(prefix, uri)
    ET.register_namespace("opds", "http://opds-spec.org/2010/catalog")
    ET.register_namespace("dcterms", "http://purl.org/dc/terms/")

    feed = ET.Element(
        "feed",
        xmlns="http://www.w3.org/2005/Atom",
    )
    feed.set("xmlns:opds", "http://opds-spec.org/2010/catalog")
    feed.set("xmlns:dcterms", "http://purl.org/dc/terms/")

    # Feed 元数据
    ET.SubElement(feed, "id").text = LIBRARY_ID
    ET.SubElement(feed, "title").text = LIBRARY_TITLE
    ET.SubElement(feed, "updated").text = now_iso()

    author_el = ET.SubElement(feed, "author")
    ET.SubElement(author_el, "name").text = LIBRARY_AUTHOR

    # self link
    ET.SubElement(
        feed,
        "link",
        rel="self",
        href=f"{SITE_URL}/catalog.xml",
        type="application/atom+xml;profile=opds-catalog;kind=acquisition",
    )

    # 每本书 → entry
    for book in books:
        entry = ET.SubElement(feed, "entry")
        ET.SubElement(entry, "title").text = book.get("title", "Untitled")
        ET.SubElement(entry, "id").text = f"urn:uuid:{book.get('id', 'unknown')}"
        ET.SubElement(entry, "updated").text = f"{book.get('added', '2026-01-01')}T00:00:00Z"

        author_el = ET.SubElement(entry, "author")
        ET.SubElement(author_el, "name").text = book.get("author", "Unknown")

        summary = book.get("summary", "")
        if summary:
            ET.SubElement(entry, "summary").text = summary

        # dcterms:language
        lang = book.get("language", "zh")
        lang_el = ET.SubElement(entry, "dcterms:language")
        lang_el.text = lang

        # 封面图
        cover = book.get("cover", "")
        if cover:
            ET.SubElement(
                entry,
                "link",
                rel="http://opds-spec.org/image",
                href=f"{SITE_URL}/{cover}",
                type="image/jpeg",
            )
            ET.SubElement(
                entry,
                "link",
                rel="http://opds-spec.org/image/thumbnail",
                href=f"{SITE_URL}/{cover}",
                type="image/jpeg",
            )

        # 下载链接（acquisition link）
        download_url = book.get("download_url", "")
        file_type = book.get("file_type", "application/epub+zip")
        if download_url:
            link_el = ET.SubElement(
                entry,
                "link",
                rel="http://opds-spec.org/acquisition",
                href=download_url,
                type=file_type,
            )
            file_size = book.get("file_size", 0)
            if file_size:
                link_el.set("length", str(file_size))

    return feed


def prettify(elem):
    """返回格式化的 XML 字符串"""
    rough_string = ET.tostring(elem, encoding="unicode", xml_declaration=False)
    reparsed = minidom.parseString(f'<?xml version="1.0" encoding="UTF-8"?>{rough_string}')
    return reparsed.toprettyxml(indent="  ", encoding=None)


def main():
    books = load_books()
    print(f"找到 {len(books)} 本书")

    feed = build_feed(books)
    output = prettify(feed)

    # minidom 会额外加一行 <?xml ...?>, 去掉重复的
    lines = output.split("\n")
    # 过滤掉 minidom 自动加的那行（toprettyxml 已经用 xml_declaration）
    # 直接写出
    with open("catalog.xml", "w", encoding="utf-8") as f:
        f.write(output)

    print(f"已生成 catalog.xml，包含 {len(books)} 条目")
    print(f"OPDS URL: https://hiktoop.github.io/mol/catalog.xml")


if __name__ == "__main__":
    main()
