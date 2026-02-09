#!/usr/bin/env python3
import argparse
import csv
import io
import mimetypes
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

try:
    from mutagen import File as MutagenFile
except Exception:
    MutagenFile = None


def eprint(*args):
    print(*args, file=sys.stderr)


class PlexClient:
    def __init__(self, base_url: str, token: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _url(self, path: str, params=None):
        p = dict(params or {})
        p["X-Plex-Token"] = self.token
        return f"{self.base_url}{path}?{urllib.parse.urlencode(p)}"

    def get_xml(self, path: str, params=None):
        with urllib.request.urlopen(self._url(path, params), timeout=self.timeout) as r:
            return ET.fromstring(r.read())

    def get_bytes(self, path: str, params=None):
        with urllib.request.urlopen(self._url(path, params), timeout=self.timeout) as r:
            return r.read()

    def get(self, path: str, params=None):
        req = urllib.request.Request(self._url(path, params), method="GET")
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read()

    def put(self, path: str, params=None):
        req = urllib.request.Request(self._url(path, params), method="PUT")
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read()

    def delete(self, path: str, params=None):
        req = urllib.request.Request(self._url(path, params), method="DELETE")
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read()

    def post_url_poster(self, artist_id: str, source_url: str):
        params = {"url": source_url}
        req = urllib.request.Request(self._url(f"/library/metadata/{artist_id}/posters", params), method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read()

    def post_raw_poster(self, artist_id: str, image_path: str):
        ctype = mimetypes.guess_type(image_path)[0] or "application/octet-stream"
        data = Path(image_path).read_bytes()
        req = urllib.request.Request(
            self._url(f"/library/metadata/{artist_id}/posters"),
            data=data,
            method="POST",
            headers={"Content-Type": ctype},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read()


def parse_map(items):
    out = []
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid --path-map: {item}")
        src, dst = item.split("=", 1)
        out.append((src.rstrip("/"), dst.rstrip("/")))
    return out


def apply_maps(path: str, maps):
    for src, dst in maps:
        if path.startswith(src):
            return dst + path[len(src) :]
    return path


def extract_track_number_from_filename(path: str):
    base = os.path.basename(path)
    stem, _ext = os.path.splitext(base)
    patterns = [
        r"^\s*0*(\d{1,3})\s*[-._)]",
        r"^\s*track\s*0*(\d{1,3})\b",
        r"^\s*0*(\d{1,3})\s+",
        r"^\s*0*(\d{1,3})$",
    ]
    for pat in patterns:
        m = re.match(pat, stem, flags=re.IGNORECASE)
        if m:
            n = int(m.group(1))
            if 0 < n <= 999:
                return n
    return None


def load_all_artists(client: PlexClient, section_id: str):
    root = client.get_xml(f"/library/sections/{section_id}/all", {"type": "8"})
    return root


def find_artists_by_name(client: PlexClient, section_id: str, names):
    root = load_all_artists(client, section_id)
    wanted = {n.strip().lower() for n in names}
    out = []
    for d in root.findall("Directory"):
        title = d.attrib.get("title", "")
        if title.lower() in wanted:
            out.append((d.attrib.get("ratingKey", ""), title))
    return out


def detect_corrupt_thumb_header(head: bytes):
    return head.startswith(b"----------------") and (b"Content-Disposition" in head)


def is_valid_image_header(head: bytes):
    return head.startswith(b"\xff\xd8\xff") or head.startswith(b"\x89PNG") or head.startswith(b"RIFF")


def choose_best_image(files, location_root):
    def rank(path: str):
        p = path.lower()
        b = os.path.basename(p)
        score = 100
        if b.startswith("cover."):
            score = 1
        elif b.startswith("folder."):
            score = 2
        elif b.startswith("front."):
            score = 3
        elif b.startswith("album."):
            score = 4
        elif b.startswith("artist."):
            score = 5
        if "/scan/" in p:
            score += 15
        depth = max(0, p.count("/") - location_root.lower().count("/"))
        return (score, depth, len(path))

    return sorted(files, key=rank)[0]


def cmd_export_artist_tracks(args):
    client = PlexClient(args.base_url, args.token, args.timeout)
    names = [x.strip() for x in args.artist_names.split(",") if x.strip()]
    found = find_artists_by_name(client, args.section, names)
    if not found:
        raise SystemExit("No matching artist names found")

    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "artist_id",
            "artist_title",
            "album_id",
            "album_title",
            "track_id",
            "track_title",
            "plex_file",
            "expected_folder",
        ])

        rows = 0
        for aid, atitle in found:
            albums_root = client.get_xml(f"/library/metadata/{aid}/children")
            albums = albums_root.findall("Directory")
            for alb in albums:
                albid = alb.attrib.get("ratingKey", "")
                altitle = alb.attrib.get("title", "")
                tracks_root = client.get_xml(f"/library/metadata/{albid}/children")
                for tr in tracks_root.findall("Track"):
                    part = tr.find("./Media/Part")
                    if part is None:
                        continue
                    pfile = part.attrib.get("file", "")
                    expected = os.path.basename(os.path.dirname(pfile))
                    w.writerow([
                        aid,
                        atitle,
                        albid,
                        altitle,
                        tr.attrib.get("ratingKey", ""),
                        tr.attrib.get("title", ""),
                        pfile,
                        expected,
                    ])
                    rows += 1

    print(f"artists_found={len(found)}")
    print(f"rows_written={rows}")
    print(f"csv={args.out_csv}")


def cmd_retag_from_csv(args):
    if MutagenFile is None:
        raise SystemExit("mutagen is required for retag-from-csv")

    maps = parse_map(args.path_map)
    seen = set()
    rows = []
    updated = 0

    with open(args.in_csv, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            p = row["plex_file"]
            host = apply_maps(p, maps)
            expected = row["expected_folder"]

            if host in seen:
                continue
            seen.add(host)

            if not os.path.exists(host):
                rows.append([host, "missing", expected, "", ""])
                continue
            if not os.access(host, os.W_OK):
                rows.append([host, "permission_denied", expected, "", ""])
                continue

            try:
                audio = MutagenFile(host, easy=True)
                if audio is None:
                    rows.append([host, "unreadable", expected, "", ""])
                    continue

                before_album = (audio.get("album") or [""])[0]
                before_albumartist = (audio.get("albumartist") or [""])[0]

                changed = False
                if before_album != expected:
                    audio["album"] = [expected]
                    changed = True
                if before_albumartist != expected:
                    audio["albumartist"] = [expected]
                    changed = True

                if changed and not args.dry_run:
                    audio.save()
                    updated += 1
                    rows.append([host, "updated", expected, before_album, before_albumartist])
                elif changed and args.dry_run:
                    rows.append([host, "would_update", expected, before_album, before_albumartist])
                else:
                    rows.append([host, "ok_already", expected, before_album, before_albumartist])
            except Exception as e:
                rows.append([host, "error", expected, "", str(e)])

    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "status", "expected_folder", "before_album", "before_albumartist_or_error"])
        w.writerows(rows)

    counts = Counter(r[1] for r in rows)
    print(f"processed={len(rows)}")
    print(f"updated={updated}")
    for k in sorted(counts):
        print(f"{k}={counts[k]}")
    print(f"csv={args.out_csv}")


def cmd_fix_track_numbers(args):
    if MutagenFile is None:
        raise SystemExit("mutagen is required for fix-track-numbers")

    maps = parse_map(args.path_map)
    seen = set()
    rows = []
    updated = 0

    with open(args.in_csv, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            p = row["plex_file"]
            host = apply_maps(p, maps)
            if host in seen:
                continue
            seen.add(host)

            desired = extract_track_number_from_filename(host)
            if desired is None:
                rows.append([host, "no_track_number_in_filename", "", ""])
                continue

            if not os.path.exists(host):
                rows.append([host, "missing", desired, ""])
                continue
            if not os.access(host, os.W_OK):
                rows.append([host, "permission_denied", desired, ""])
                continue

            try:
                audio = MutagenFile(host, easy=True)
                if audio is None:
                    rows.append([host, "unreadable", desired, ""])
                    continue

                before = (audio.get("tracknumber") or [""])[0]
                before_main = before.split("/", 1)[0].strip()
                desired_str = str(desired)

                if before_main == desired_str:
                    rows.append([host, "ok_already", desired, before])
                    continue

                new_value = desired_str
                if args.preserve_total and "/" in before:
                    total_part = before.split("/", 1)[1].strip()
                    if total_part:
                        new_value = f"{desired_str}/{total_part}"

                if args.dry_run:
                    rows.append([host, "would_update", desired, before])
                else:
                    audio["tracknumber"] = [new_value]
                    audio.save()
                    updated += 1
                    rows.append([host, "updated", desired, before])
            except Exception as e:
                rows.append([host, "error", desired, str(e)])

    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "status", "desired_tracknumber", "before_tracknumber_or_error"])
        w.writerows(rows)

    counts = Counter(r[1] for r in rows)
    print(f"processed={len(rows)}")
    print(f"updated={updated}")
    for k in sorted(counts):
        print(f"{k}={counts[k]}")
    print(f"csv={args.out_csv}")


def cmd_cleanup_artists(args):
    client = PlexClient(args.base_url, args.token, args.timeout)

    ids = []
    if args.artist_ids:
        ids.extend([x.strip() for x in args.artist_ids.split(",") if x.strip()])
    if args.artist_names:
        names = [x.strip() for x in args.artist_names.split(",") if x.strip()]
        ids.extend([x[0] for x in find_artists_by_name(client, args.section, names)])

    ids = sorted(set(ids))
    deleted = 0
    for aid in ids:
        try:
            client.delete(f"/library/metadata/{aid}")
            deleted += 1
        except Exception as e:
            eprint(f"delete_failed artist_id={aid}: {e}")

    scans_ok = 0
    scans_err = 0
    if args.scan_csv:
        maps = parse_map(args.path_map)
        scan_root = args.scan_root_prefix.rstrip("/")
        if not scan_root:
            scan_root = "/"
        folders = []
        seen = set()
        with open(args.scan_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                fd = row["expected_folder"]
                if fd not in seen:
                    seen.add(fd)
                    folders.append(fd)

        for fd in folders:
            if scan_root == "/":
                p = f"/{fd}"
            else:
                p = f"{scan_root}/{fd}"
            p = apply_maps(p, maps)
            try:
                client.get(f"/library/sections/{args.section}/refresh", {"path": p})
                scans_ok += 1
            except Exception:
                scans_err += 1

    if args.section_refresh:
        client.get(f"/library/sections/{args.section}/refresh")

    if args.wait_seconds > 0:
        time.sleep(args.wait_seconds)

    if args.empty_trash:
        try:
            client.put(f"/library/sections/{args.section}/emptyTrash")
        except Exception as e:
            eprint(f"emptyTrash_failed: {e}")

    print(f"artists_deleted={deleted}")
    print(f"scan_path_ok={scans_ok}")
    print(f"scan_path_err={scans_err}")


def cmd_repair_artist_posters(args):
    client = PlexClient(args.base_url, args.token, args.timeout)
    maps = parse_map(args.path_map)

    root = load_all_artists(client, args.section)
    rows = []
    fixed = 0

    for d in root.findall("Directory"):
        aid = d.attrib.get("ratingKey", "")
        title = d.attrib.get("title", "")
        thumb = d.attrib.get("thumb", "")

        need_fix = False
        if not thumb and args.fix_missing:
            need_fix = True
        elif thumb and args.fix_corrupt:
            head = client.get_bytes(thumb)[:220]
            if detect_corrupt_thumb_header(head):
                need_fix = True

        if not need_fix:
            continue

        source = ""
        status = ""
        error = ""

        try:
            # 1) album thumb
            alb_root = client.get_xml(f"/library/metadata/{aid}/children")
            album_thumb = ""
            for alb in alb_root.findall("Directory"):
                t = alb.attrib.get("thumb", "")
                if not t:
                    continue
                head = client.get_bytes(t)[:220]
                if not detect_corrupt_thumb_header(head):
                    album_thumb = t
                    break

            if album_thumb:
                client.post_url_poster(aid, f"{args.base_url.rstrip('/')}{album_thumb}?X-Plex-Token={args.token}")
                source = f"album_thumb:{album_thumb}"
            else:
                # 2) local image from artist location
                meta = client.get_xml(f"/library/metadata/{aid}")
                md = meta.find("Directory")
                loc = ""
                if md is not None:
                    ln = md.find("Location")
                    if ln is not None:
                        loc = ln.attrib.get("path", "")
                host_loc = apply_maps(loc, maps)

                images = []
                if host_loc and os.path.isdir(host_loc):
                    for root_dir, _dirs, files in os.walk(host_loc):
                        depth = root_dir.count(os.sep) - host_loc.count(os.sep)
                        if depth > args.max_image_depth:
                            continue
                        for fn in files:
                            if fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                                images.append(os.path.join(root_dir, fn))

                if images:
                    best = choose_best_image(images, host_loc)
                    client.post_raw_poster(aid, best)
                    source = f"file:{best}"
                elif args.generate_missing:
                    try:
                        from PIL import Image, ImageDraw, ImageFont

                        gen = os.path.join(args.tmp_dir, f"artist_{aid}_generated.jpg")
                        os.makedirs(args.tmp_dir, exist_ok=True)
                        img = Image.new("RGB", (1500, 1500), (17, 22, 35))
                        draw = ImageDraw.Draw(img)
                        try:
                            f1 = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 110)
                            f2 = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 36)
                        except Exception:
                            f1 = ImageFont.load_default()
                            f2 = ImageFont.load_default()
                        title_wrapped = title.replace(" - ", "\n")
                        bb = draw.multiline_textbbox((0, 0), title_wrapped, font=f1, spacing=16, align="center")
                        tw, th = bb[2] - bb[0], bb[3] - bb[1]
                        draw.multiline_text(((1500 - tw) // 2, (1500 - th) // 2), title_wrapped, fill=(106, 216, 255), font=f1, spacing=16, align="center")
                        draw.text((120, 1380), "Generated cover", fill=(200, 200, 220), font=f2)
                        img.save(gen, "JPEG", quality=95)
                        client.post_raw_poster(aid, gen)
                        source = f"generated:{gen}"
                    except Exception as ge:
                        raise RuntimeError(f"generate_failed: {ge}")
                else:
                    source = "none"

            new_thumb = client.get_xml(f"/library/metadata/{aid}").find("Directory").attrib.get("thumb", "")
            if new_thumb:
                new_head = client.get_bytes(new_thumb)[:220]
                if is_valid_image_header(new_head) and not detect_corrupt_thumb_header(new_head):
                    status = "fixed"
                    fixed += 1
                else:
                    status = "failed_after_apply"
            else:
                status = "failed_no_thumb"

            rows.append([aid, title, thumb, source, status, ""])
        except Exception as e:
            error = str(e)
            rows.append([aid, title, thumb, source, "error", error])

    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["artist_id", "title", "old_thumb", "source", "status", "error"])
        w.writerows(rows)

    print(f"fixed={fixed}")
    print(f"rows={len(rows)}")
    print(f"csv={args.out_csv}")


def cmd_verify_artists(args):
    client = PlexClient(args.base_url, args.token, args.timeout)
    root = load_all_artists(client, args.section)

    missing = []
    corrupt = []

    for d in root.findall("Directory"):
        rid = d.attrib.get("ratingKey", "")
        title = d.attrib.get("title", "")
        thumb = d.attrib.get("thumb", "")

        if not thumb:
            missing.append((rid, title))
            continue

        head = client.get_bytes(thumb)[:220]
        if detect_corrupt_thumb_header(head):
            corrupt.append((rid, title))

    print(f"artists_total={root.attrib.get('size', '0')}")
    print(f"missing_thumb={len(missing)}")
    print(f"corrupt_thumb={len(corrupt)}")

    if args.show and missing:
        print("missing_examples:")
        for rid, title in missing[: args.show]:
            print(f"  {rid} | {title}")

    if args.show and corrupt:
        print("corrupt_examples:")
        for rid, title in corrupt[: args.show]:
            print(f"  {rid} | {title}")


def cmd_doctor(args):
    failures = 0
    warnings = 0

    def ok(msg):
        print(f"OK    {msg}")

    def warn(msg):
        nonlocal warnings
        warnings += 1
        print(f"WARN  {msg}")

    def fail(msg):
        nonlocal failures
        failures += 1
        print(f"FAIL  {msg}")

    try:
        maps = parse_map(args.path_map)
        ok(f"path-map syntax valid ({len(maps)} entries)")
    except Exception as e:
        fail(f"path-map parse failed: {e}")
        maps = []

    if args.server != "plex":
        warn(
            f"--server {args.server}: API doctor checks are not implemented yet; "
            "run file workflow checks only (retag/track-number commands)"
        )
        print(f"summary failures={failures} warnings={warnings}")
        if failures:
            raise SystemExit(2)
        return

    client = PlexClient(args.base_url, args.token, args.timeout)

    # 1) Connectivity + token
    try:
        sections = client.get_xml("/library/sections")
        dirs = sections.findall("Directory")
        ok(f"connected to Plex at {args.base_url} (sections={len(dirs)})")
    except Exception as e:
        fail(f"cannot connect/auth to Plex API: {e}")
        print(f"summary failures={failures} warnings={warnings}")
        raise SystemExit(2)

    # 2) Music section check
    section_dir = None
    for d in dirs:
        if d.attrib.get("key") == str(args.section):
            section_dir = d
            break
    if section_dir is None:
        fail(f"section {args.section} not found")
        print(f"summary failures={failures} warnings={warnings}")
        raise SystemExit(2)

    sec_type = section_dir.attrib.get("type", "")
    sec_title = section_dir.attrib.get("title", "")
    if sec_type != "artist":
        warn(f"section {args.section} ({sec_title}) is type '{sec_type}', expected 'artist'")
    else:
        ok(f"section {args.section} ({sec_title}) is a music/artist section")

    # 3) Library root path + path-map coverage
    locations = section_dir.findall("Location")
    if not locations:
        warn(f"section {args.section} has no Location paths")
    for loc in locations:
        plex_root = loc.attrib.get("path", "")
        if not plex_root:
            continue
        ok(f"plex library root: {plex_root}")

        if maps:
            host_root = apply_maps(plex_root, maps)
            if host_root == plex_root:
                warn(f"no path-map matched plex root {plex_root}")
            elif os.path.isdir(host_root):
                ok(f"mapped host root exists: {host_root}")
            else:
                fail(f"mapped host root does not exist: {host_root}")
        else:
            if os.path.isdir(plex_root):
                ok(f"plex root exists on this host: {plex_root}")
            else:
                warn("no --path-map provided and plex root is not local on this host")

    # 4) Scan-root sanity check
    scan_root = args.scan_root_prefix.rstrip("/") or "/"
    ok(f"scan root prefix set: {scan_root}")
    if locations:
        for loc in locations:
            plex_root = loc.attrib.get("path", "")
            if plex_root and not plex_root.startswith(scan_root):
                warn(f"scan-root-prefix {scan_root} does not prefix section root {plex_root}")

    # 5) Lightweight API permission check
    try:
        root = client.get_xml(f"/library/sections/{args.section}/all", {"type": "8"})
        size = root.attrib.get("size", "0")
        ok(f"can query artists in section {args.section} (size={size})")
    except Exception as e:
        fail(f"cannot query artists for section {args.section}: {e}")

    print(f"summary failures={failures} warnings={warnings}")
    if failures:
        raise SystemExit(2)


def build_parser():
    p = argparse.ArgumentParser(description="Plex Music Toolkit")
    p.add_argument(
        "--server",
        default=os.getenv("MEDIA_SERVER", "plex"),
        choices=["plex", "jellyfin", "emby"],
        help="Media server backend",
    )
    p.add_argument("--base-url", default=os.getenv("PLEX_BASE_URL", "http://127.0.0.1:32400"))
    p.add_argument("--token", default=os.getenv("PLEX_TOKEN", ""))
    p.add_argument("--section", default=os.getenv("PLEX_MUSIC_SECTION", "6"))
    p.add_argument("--timeout", type=int, default=60)

    sub = p.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("export-artist-tracks")
    s1.add_argument("--artist-names", required=True, help="Comma-separated names")
    s1.add_argument("--out-csv", required=True)
    s1.set_defaults(func=cmd_export_artist_tracks)

    s2 = sub.add_parser("retag-from-csv")
    s2.add_argument("--in-csv", required=True)
    s2.add_argument("--out-csv", required=True)
    s2.add_argument("--path-map", action="append", default=[], help="prefix map SRC=DST (repeatable)")
    s2.add_argument("--dry-run", action="store_true")
    s2.set_defaults(func=cmd_retag_from_csv)

    s3 = sub.add_parser("fix-track-numbers")
    s3.add_argument("--in-csv", required=True)
    s3.add_argument("--out-csv", required=True)
    s3.add_argument("--path-map", action="append", default=[], help="prefix map SRC=DST (repeatable)")
    s3.add_argument("--preserve-total", action="store_true", help="Preserve total when existing value is N/TOTAL")
    s3.add_argument("--dry-run", action="store_true")
    s3.set_defaults(func=cmd_fix_track_numbers)

    s4 = sub.add_parser("cleanup-artists")
    s4.add_argument("--artist-ids", default="")
    s4.add_argument("--artist-names", default="")
    s4.add_argument("--scan-csv", default="")
    s4.add_argument(
        "--scan-root-prefix",
        default="/Music",
        help="Plex library root prefix for targeted refresh paths, e.g. /Music",
    )
    s4.add_argument("--path-map", action="append", default=[])
    s4.add_argument("--section-refresh", action="store_true")
    s4.add_argument("--empty-trash", action="store_true")
    s4.add_argument("--wait-seconds", type=int, default=20)
    s4.set_defaults(func=cmd_cleanup_artists)

    s5 = sub.add_parser("repair-artist-posters")
    s5.add_argument("--out-csv", required=True)
    s5.add_argument("--path-map", action="append", default=[])
    s5.add_argument("--fix-missing", action="store_true")
    s5.add_argument("--fix-corrupt", action="store_true")
    s5.add_argument("--generate-missing", action="store_true")
    s5.add_argument("--max-image-depth", type=int, default=4)
    s5.add_argument("--tmp-dir", default="/tmp/plex_artist_generated")
    s5.set_defaults(func=cmd_repair_artist_posters)

    s6 = sub.add_parser("verify-artists")
    s6.add_argument("--show", type=int, default=20)
    s6.set_defaults(func=cmd_verify_artists)

    s7 = sub.add_parser("doctor")
    s7.add_argument("--path-map", action="append", default=[], help="prefix map SRC=DST (repeatable)")
    s7.add_argument(
        "--scan-root-prefix",
        default="/Music",
        help="Plex library root prefix for targeted refresh paths, e.g. /Music",
    )
    s7.set_defaults(func=cmd_doctor)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    api_cmds = {
        "export-artist-tracks",
        "cleanup-artists",
        "repair-artist-posters",
        "verify-artists",
        "doctor",
    }
    if args.cmd in api_cmds and args.server != "plex":
        raise SystemExit(
            f"--server {args.server} adapter is not implemented yet for API workflows. "
            "Use --server plex, or run retag-from-csv for server-agnostic file tag repair."
        )
    if args.cmd in api_cmds and not args.token:
        raise SystemExit("Missing --token or PLEX_TOKEN")
    args.func(args)


if __name__ == "__main__":
    main()
