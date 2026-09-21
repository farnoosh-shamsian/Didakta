#!/usr/bin/env python3
"""Repoint the vocabulary links in the published Didakta files at Logeion.

The files downloaded from Zenodo (HTML, PDF, EPUB, DOCX and the split entries)
link every Greek word to the Perseus hopper word-study tool. That service is
legacy Perseus 4 infrastructure: it still answers the occasional click, but it
rate-limits and returns 503 under any real use, so for a reader working through
a chapter the links are effectively dead. This script rewrites them to Logeion
(University of Chicago), which parses the inflected form and returns LSJ,
Bailly, Pape, Middle Liddell and the rest alongside it.

    python didakta_relink.py            # rewrite every file, in place
    python didakta_relink.py --check    # report what would change, touch nothing

The hopper URLs carry the word in betacode (``l=tragw%7Cdoi%3Ds``), and a few of
those transliterations are wrong in the export itself. Rather than decode them,
the betacode is mapped back to the Unicode word using the HTML export, where
each link's anchor text is the word as printed. That table covers every link in
every file, so no link is rewritten on a guess: anything unresolvable is left
alone and reported. It is cached in didakta-betacode.json, because once the HTML
has been migrated the betacode is no longer anywhere in the repository.

Passage links still go to Perseus, which hosts the texts; they are upgraded from
http to https, which the hopper serves but does not redirect to.
"""

from __future__ import annotations

import argparse
import collections
import html as htmllib
import re
import json
import shutil
import sys
import unicodedata
import urllib.parse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LANGUAGES = ("english", "persian", "kurdish")
LOGEION = "https://logeion.uchicago.edu/"
TABLE_PATH = ROOT / "didakta-betacode.json"

GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")
MORPH_RE = re.compile(r"hopper/morph")
URI_SAFE = set(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
)


# ---------------------------------------------------------------------------
# betacode -> Unicode, learned from the HTML export
# ---------------------------------------------------------------------------


def unwrap_google(href: str) -> str:
    """The Google Docs export wraps every link in a www.google.com/url redirect."""
    href = htmllib.unescape(href)
    if "google.com/url" in href:
        target = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get("q")
        if target:
            return target[0]
    return href


def betacode_of(url: str) -> str | None:
    match = re.search(r"[?&]l=([^&]*)", url)
    return urllib.parse.unquote(match.group(1)) if match else None


def greek_letters(text: str) -> int:
    return sum(1 for c in text if GREEK_RE.match(c))


def build_table() -> dict[str, str]:
    """Map each betacode form to the Greek word the HTML export prints for it.

    A handful of words are split across two anchors sharing one href, so the
    same betacode can be seen against a fragment ('e)pei\\' against both 'epei'
    and 'pei'). The candidate with the most Greek letters is the whole word;
    frequency breaks the remaining ties.
    """
    seen: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for language in LANGUAGES:
        path = ROOT / f"didakta-{language}.html"
        if not path.exists():
            continue
        source = path.read_text(encoding="utf-8")
        for href, text in re.findall(
            r'<a[^>]*href="([^"]*hopper/morph[^"]*)"[^>]*>(.*?)</a>', source, re.S
        ):
            code = betacode_of(unwrap_google(href))
            word = unicodedata.normalize(
                "NFC", htmllib.unescape(re.sub(r"<[^>]+>", "", text)).strip()
            )
            if code and word and greek_letters(word):
                seen[code][word] += 1
    table = {
        code: max(words.items(), key=lambda kv: (greek_letters(kv[0]), kv[1]))[0]
        for code, words in seen.items()
    }
    if table:
        # Once the HTML is migrated its betacode is gone, so keep the mapping
        # beside the files: it is the record of what each old URL referred to,
        # and lets the script run again over a freshly downloaded Zenodo file.
        stored = load_table()
        stored.update(table)
        TABLE_PATH.write_text(
            json.dumps(stored, ensure_ascii=False, indent=0, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return stored
    return load_table()


def load_table() -> dict[str, str]:
    if TABLE_PATH.exists():
        return json.loads(TABLE_PATH.read_text(encoding="utf-8"))
    return {}


def logeion_url(form: str) -> str:
    form = unicodedata.normalize("NFC", form).strip()
    return LOGEION + "".join(
        c if c in URI_SAFE else "".join(f"%{b:02X}" for b in c.encode("utf-8"))
        for c in form
    )


class Relinker:
    """Turns one hopper URL into one Logeion URL, counting what it could not do."""

    def __init__(self, table: dict[str, str]) -> None:
        self.table = table
        self.words = 0
        self.passages = 0
        self.unresolved: collections.Counter = collections.Counter()
        self._mark = (0, 0)

    def take(self) -> tuple[int, int]:
        """Counts since the last call, so each file can report its own total."""
        words, passages = self.words - self._mark[0], self.passages - self._mark[1]
        self._mark = (self.words, self.passages)
        return words, passages

    def rewrite(self, href: str, anchor: str | None = None) -> str | None:
        """Return the replacement for `href`, or None to leave it as it is.

        `anchor` is the link's own text where the format has it to hand; it is
        the word as printed, so it is preferred over the betacode table.
        """
        plain = unwrap_google(href)
        if "hopper/text" in plain:
            upgraded = plain.replace("http://", "https://", 1)
            # Compare unescaped: `href` may carry &amp; where `upgraded` has &,
            # which is the same URL and must not count as a rewrite.
            if upgraded == htmllib.unescape(href):
                return None
            self.passages += 1
            return upgraded
        if not MORPH_RE.search(plain):
            return None
        word = None
        if anchor:
            candidate = unicodedata.normalize("NFC", anchor.strip())
            if greek_letters(candidate):
                word = candidate
        if word is None:
            code = betacode_of(plain)
            word = self.table.get(code) if code else None
        if word is None:
            self.unresolved[betacode_of(plain) or plain] += 1
            return None
        self.words += 1
        return logeion_url(word)


# ---------------------------------------------------------------------------
# per-format rewriting
# ---------------------------------------------------------------------------


def rewrite_html_text(text: str, rel: Relinker) -> str:
    """HTML and EPUB XHTML: anchor text sits right next to the href."""

    def repl(match: re.Match) -> str:
        head, href, mid, body, tail = match.groups()
        new = rel.rewrite(href, anchor=htmllib.unescape(re.sub(r"<[^>]+>", "", body)))
        if new is None:
            return match.group(0)
        return f"{head}{htmllib.escape(new, quote=True)}{mid}{body}{tail}"

    return re.sub(
        r'(<a[^>]*?href=")([^"]*)("[^>]*>)(.*?)(</a>)', repl, text, flags=re.S
    )


def rewrite_markdown(text: str, rel: Relinker) -> str:
    """Split entries: [word](url), so the anchor text is again to hand."""

    def repl(match: re.Match) -> str:
        label, href = match.groups()
        new = rel.rewrite(href, anchor=label)
        return match.group(0) if new is None else f"[{label}]({new})"

    return re.sub(r"\[([^\]\n]*)\]\((https?://[^)\s]*)\)", repl, text)


def rewrite_rels(text: str, rel: Relinker) -> str:
    """DOCX: hyperlinks live in the .rels parts, away from their anchor text."""

    def repl(match: re.Match) -> str:
        head, href, tail = match.groups()
        new = rel.rewrite(href)
        if new is None:
            return match.group(0)
        return f"{head}{htmllib.escape(new, quote=True)}{tail}"

    return re.sub(r'(Target=")([^"]*)(")', repl, text)


def rewrite_zip(path: Path, rel: Relinker, members: str, check: bool) -> int:
    """Rewrite the text parts of a zip container (EPUB or DOCX) in place."""
    source = zipfile.ZipFile(path)
    changed = 0
    staged: dict[str, bytes] = {}
    for name in source.namelist():
        if not re.search(members, name):
            continue
        raw = source.read(name)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if "hopper/" not in text:
            continue
        new = (
            rewrite_rels(text, rel)
            if name.endswith(".rels")
            else rewrite_html_text(text, rel)
        )
        if new != text:
            staged[name] = new.encode("utf-8")
            changed += 1
    if check or not staged:
        source.close()
        return changed
    temp = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as out:
        for item in source.infolist():
            data = staged.get(item.filename, source.read(item.filename))
            # keep mimetype stored first and uncompressed, as EPUB requires
            info = zipfile.ZipInfo(item.filename, date_time=item.date_time)
            info.compress_type = (
                zipfile.ZIP_STORED
                if item.filename == "mimetype"
                else zipfile.ZIP_DEFLATED
            )
            info.external_attr = item.external_attr
            out.writestr(info, data)
    source.close()
    temp.replace(path)
    return changed


def rewrite_pdf(path: Path, rel: Relinker, check: bool) -> int:
    """PDF: the URLs are /URI actions on link annotations, no anchor text."""
    import logging

    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import TextStringObject

    # the Google Docs PDFs repeat a few named destinations; pypdf reports each
    logging.getLogger("pypdf").setLevel(logging.ERROR)

    reader = PdfReader(str(path))
    writer = PdfWriter(clone_from=reader)
    changed = 0
    for page in writer.pages:
        for annot in page.get("/Annots") or []:
            obj = annot.get_object()
            action = obj.get("/A")
            if not action or "/URI" not in action:
                continue
            new = rel.rewrite(str(action["/URI"]))
            if new is None:
                continue
            changed += 1
            if not check:
                action[TextStringObject("/URI")] = TextStringObject(new)
    if changed and not check:
        temp = path.with_suffix(".pdf.tmp")
        with open(temp, "wb") as fh:
            writer.write(fh)
        temp.replace(path)
    return changed


# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="report changes without writing"
    )
    parser.add_argument(
        "--no-backup", action="store_true", help="do not keep .perseus.bak copies"
    )
    args = parser.parse_args(argv)

    table = build_table()
    print(f"betacode table: {len(table)} forms learned from the HTML exports\n")
    if not table:
        print("error: no HTML exports found, cannot map betacode to Greek")
        return 1

    grand = Relinker(table)
    for language in LANGUAGES:
        rel = Relinker(table)
        print(f"{language}:")

        for suffix, kind in ((".html", "html"), (".md", "markdown")):
            path = ROOT / f"didakta-{language}{suffix}"
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            if "hopper/" not in text:
                continue
            new = (
                rewrite_html_text(text, rel)
                if kind == "html"
                else rewrite_markdown(text, rel)
            )
            if new != text and not args.check:
                if not args.no_backup:
                    shutil.copy2(path, path.with_suffix(suffix + ".perseus.bak"))
                path.write_text(new, encoding="utf-8")
            w, c = rel.take()
            print(f"  {path.name}: {w} words, {c} citations")

        entries = ROOT / f"didakta-{language}-split-entries"
        if entries.is_dir():
            touched = 0
            for md in sorted(entries.glob("*.md")):
                text = md.read_text(encoding="utf-8")
                if "hopper/" not in text:
                    continue
                new = rewrite_markdown(text, rel)
                if new != text:
                    touched += 1
                    if not args.check:
                        md.write_text(new, encoding="utf-8")
            w, c = rel.take()
            print(f"  {entries.name}: {w} words, {c} citations "
                  f"across {touched} entry files")

        for suffix, members in ((".epub", r"\.(xhtml|html|opf|ncx)$"),
                                (".docx", r"\.rels$")):
            path = ROOT / f"didakta-{language}{suffix}"
            if not path.exists():
                continue
            if not args.check and not args.no_backup:
                shutil.copy2(path, path.with_suffix(suffix + ".perseus.bak"))
            n = rewrite_zip(path, rel, members, args.check)
            w, c = rel.take()
            print(f"  {path.name}: {w} words, {c} citations in {n} parts")

        pdf = ROOT / f"didakta-{language}.pdf"
        if pdf.exists():
            if not args.check and not args.no_backup:
                shutil.copy2(pdf, pdf.with_suffix(".pdf.perseus.bak"))
            n = rewrite_pdf(pdf, rel, args.check)
            w, c = rel.take()
            print(f"  {pdf.name}: {w} words, {c} citations in {n} annotations")

        print(f"  -> {rel.words} vocabulary + {rel.passages} passage "
              f"rewrites, summed over the formats above")
        if rel.unresolved:
            print(f"  -> UNRESOLVED {sum(rel.unresolved.values())}: "
                  f"{list(rel.unresolved)[:5]}")
        grand.words += rel.words
        grand.passages += rel.passages
        grand.unresolved.update(rel.unresolved)
        print()

    if not grand.words and not grand.passages and not grand.unresolved:
        print("total: nothing to do, every link already points at Logeion")
        return 0
    print(f"total: {grand.words} vocabulary links to Logeion, "
          f"{grand.passages} passage links upgraded to https")
    if grand.unresolved:
        print(f"unresolved: {sum(grand.unresolved.values())} links left as they were")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
