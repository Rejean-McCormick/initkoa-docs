from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
CACHE_DIR = ROOT / ".wiki-cache"
MKDOCS_FILE = ROOT / "mkdocs.yml"

PROJECTS = [
    {
        "title": "SemantiK Architect",
        "wiki_url": "https://github.com/Rejean-McCormick/SemantiK_Architect.wiki.git",
    },
    {
        "title": "Kristal Framework",
        "wiki_url": "https://github.com/Rejean-McCormick/kristal-framework.wiki.git",
    },
    {
        "title": "kOA Digital Ecosystem",
        "wiki_url": "https://github.com/Rejean-McCormick/kOA_Digital_Ecosystem.wiki.git",
    },
    {
        "title": "Konnaxion",
        "wiki_url": "https://github.com/Rejean-McCormick/Konnaxion.wiki.git",
    },
    {
        "title": "Orgo",
        "wiki_url": "https://github.com/Rejean-McCormick/Orgo.wiki.git",
    },
    {
        "title": "SenTient",
        "wiki_url": "https://github.com/Rejean-McCormick/SenTient.wiki.git",
    },
]

SPECIAL_WIKI_FILES = {"_Footer.md", "_Header.md", "_Sidebar.md"}
WIKI_META_FILES = SPECIAL_WIKI_FILES | {".git"}


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        shell=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )
    return result


def safe_folder_name(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "_", name).strip()


def clear_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def clone_or_update_wiki(title: str, wiki_url: str) -> Path | None:
    target = CACHE_DIR / safe_folder_name(title)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if (target / ".git").exists():
        print(f"[update] {title}")
        result = run(["git", "pull", "--ff-only"], cwd=target, check=False)
        if result.returncode == 0:
            return target

        print(f"[reset ] {title} (pull failed, recloning)")
        shutil.rmtree(target, ignore_errors=True)

    print(f"[clone ] {title}")
    result = run(["git", "clone", "--depth", "1", wiki_url, str(target)], check=False)
    if result.returncode != 0:
        print(f"[skip  ] {title} -> wiki not found or not accessible")
        return None

    return target


def copy_wiki_contents(source: Path, destination: Path) -> None:
    clear_dir(destination)

    for item in source.iterdir():
        if item.name in WIKI_META_FILES:
            continue

        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)

    home_md = destination / "Home.md"
    index_md = destination / "index.md"

    if home_md.exists():
        if index_md.exists():
            index_md.unlink()
        home_md.rename(index_md)


def normalize_page_key(value: str) -> str:
    value = unquote(value).strip()
    value = value.replace("\\", "/")
    if value.lower().endswith(".md"):
        value = value[:-3]

    value = value.replace("&", " and ")
    value = value.replace("–", " ")
    value = value.replace("—", " ")
    value = value.replace("-", " ")
    value = value.replace("_", " ")
    value = re.sub(r"[^\w\s/]", " ", value, flags=re.UNICODE)
    value = re.sub(r"\s+", " ", value)
    return value.strip().lower()


def prettify_title(value: str) -> str:
    value = value.replace("-", " ").replace("_", " ").strip()
    value = re.sub(r"\s+", " ", value)
    return value


def build_page_lookup(project_dir: Path, project_title: str) -> dict[str, Path]:
    lookup: dict[str, Path] = {}

    for md_file in project_dir.rglob("*.md"):
        if md_file.name in SPECIAL_WIKI_FILES:
            continue

        rel = md_file.relative_to(project_dir)
        rel_no_ext = rel.with_suffix("").as_posix()

        keys = {
            normalize_page_key(md_file.stem),
            normalize_page_key(rel_no_ext),
            normalize_page_key(rel_no_ext.replace("/", " ")),
        }

        if rel.as_posix() == "index.md":
            keys.add(normalize_page_key("Home"))
            keys.add(normalize_page_key(project_title))

        for key in keys:
            lookup.setdefault(key, rel)

    return lookup


def resolve_target(raw_target: str, current_file: Path, project_dir: Path, lookup: dict[str, Path]) -> str | None:
    raw_target = raw_target.strip()
    if not raw_target:
        return None

    if raw_target.startswith("#"):
        return raw_target

    parsed = urlparse(raw_target)
    anchor = f"#{parsed.fragment}" if parsed.fragment else ""
    no_anchor = raw_target.split("#", 1)[0].strip()

    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", no_anchor):
        if "/wiki/" not in no_anchor:
            return None
        wiki_tail = no_anchor.rsplit("/wiki/", 1)[-1]
        candidate_key = normalize_page_key(wiki_tail)
    else:
        candidate_key = normalize_page_key(no_anchor)

    rel_target = lookup.get(candidate_key)
    if rel_target is None:
        possible_path = (project_dir / no_anchor).resolve()
        try:
            possible_path.relative_to(project_dir.resolve())
            if possible_path.exists() and possible_path.suffix.lower() == ".md":
                rel_target = possible_path.relative_to(project_dir)
        except ValueError:
            pass

    if rel_target is None:
        return None

    link = os.path.relpath(project_dir / rel_target, start=current_file.parent)
    return link.replace("\\", "/") + anchor


def rewrite_wiki_links(text: str, current_file: Path, project_dir: Path, lookup: dict[str, Path]) -> str:
    wiki_link_pattern = re.compile(r"\[\[([^\]]+)\]\]")

    def wiki_link_replacer(match: re.Match[str]) -> str:
        inner = match.group(1).strip()
        if not inner:
            return match.group(0)

        if "|" in inner:
            left, right = [part.strip() for part in inner.split("|", 1)]
            left_target = resolve_target(left, current_file, project_dir, lookup)
            right_target = resolve_target(right, current_file, project_dir, lookup)

            if left_target:
                target_raw = left
                label = right
            elif right_target:
                target_raw = right
                label = left
            else:
                target_raw = left
                label = right
        else:
            target_raw = inner
            label = inner

        resolved = resolve_target(target_raw, current_file, project_dir, lookup)
        if not resolved:
            return match.group(0)

        return f"[{label}]({resolved})"

    return wiki_link_pattern.sub(wiki_link_replacer, text)


def rewrite_markdown_links(text: str, current_file: Path, project_dir: Path, lookup: dict[str, Path]) -> str:
    markdown_link_pattern = re.compile(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)')

    def markdown_link_replacer(match: re.Match[str]) -> str:
        label = match.group(1)
        target = match.group(2).strip()

        resolved = resolve_target(target, current_file, project_dir, lookup)
        if not resolved:
            return match.group(0)

        return f"[{label}]({resolved})"

    return markdown_link_pattern.sub(markdown_link_replacer, text)


def rewrite_links_in_project(project_dir: Path, project_title: str) -> None:
    lookup = build_page_lookup(project_dir, project_title)

    for md_file in project_dir.rglob("*.md"):
        if md_file.name in SPECIAL_WIKI_FILES:
            continue

        original = md_file.read_text(encoding="utf-8")
        updated = rewrite_wiki_links(original, md_file, project_dir, lookup)
        updated = rewrite_markdown_links(updated, md_file, project_dir, lookup)

        if updated != original:
            md_file.write_text(updated, encoding="utf-8")


def strip_wrapping_markdown(text: str) -> str:
    text = text.strip()

    patterns = [
        r"^\*\*(.+)\*\*$",
        r"^__(.+)__$",
        r"^\*(.+)\*$",
        r"^_(.+)_$",
        r"^`(.+)`$",
    ]

    changed = True
    while changed:
        changed = False
        for pattern in patterns:
            match = re.fullmatch(pattern, text)
            if match:
                text = match.group(1).strip()
                changed = True

    return text.strip()


def extract_single_link(text: str) -> tuple[str, str] | None:
    wiki_match = re.fullmatch(r"\[\[([^\]]+)\]\]", text)
    if wiki_match:
        inner = wiki_match.group(1).strip()
        if "|" in inner:
            left, right = [part.strip() for part in inner.split("|", 1)]
            return (right or left), (left or right)
        return inner, inner

    md_match = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", text)
    if md_match:
        return md_match.group(1).strip(), md_match.group(2).strip()

    return None


def parse_sidebar_item(text: str) -> tuple[str, str | None, bool]:
    text = text.strip()
    link = extract_single_link(text)
    if link:
        title, target = link
        return title, target, True

    clean = strip_wrapping_markdown(text).rstrip(":").strip()
    return clean, None, False


def is_separator_line(text: str) -> bool:
    return bool(re.fullmatch(r"[-*_]{3,}", text.strip()))


def is_plain_heading_candidate(text: str) -> bool:
    if not text:
        return False
    if extract_single_link(text):
        return False
    if text.startswith(">"):
        return False
    return True


def parse_sidebar(project_dir: Path) -> list[dict[str, Any]]:
    sidebar = project_dir / "_Sidebar.md"
    if not sidebar.exists():
        return []

    items: list[dict[str, Any]] = []
    heading_stack: list[tuple[int, list[dict[str, Any]]]] = [(0, items)]
    list_stack: list[tuple[int, list[dict[str, Any]]]] = []
    current_inline_section_children: list[dict[str, Any]] | None = None

    def current_base_children() -> list[dict[str, Any]]:
        return current_inline_section_children if current_inline_section_children is not None else heading_stack[-1][1]

    for raw_line in sidebar.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            list_stack = []
            current_inline_section_children = None
            continue

        if is_separator_line(stripped):
            list_stack = []
            current_inline_section_children = None
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading_match:
            level = len(heading_match.group(1))
            title, target, is_link = parse_sidebar_item(heading_match.group(2))
            if not title:
                list_stack = []
                current_inline_section_children = None
                continue

            node = {
                "title": title,
                "target": target if is_link else None,
                "children": [],
            }

            while len(heading_stack) > 1 and level <= heading_stack[-1][0]:
                heading_stack.pop()

            heading_stack[-1][1].append(node)
            heading_stack.append((level, node["children"]))
            list_stack = []
            current_inline_section_children = None
            continue

        bullet_match = re.match(r"^([ \t]*)[-*+]\s+(.*)$", line)
        if bullet_match:
            indent_text, content = bullet_match.groups()
            indent = len(indent_text.replace("\t", "    "))

            title, target, is_link = parse_sidebar_item(content)
            if not title:
                continue

            while list_stack and indent <= list_stack[-1][0]:
                list_stack.pop()

            parent_children = list_stack[-1][1] if list_stack else current_base_children()

            node = {
                "title": title,
                "target": target if is_link else None,
                "children": [],
            }
            parent_children.append(node)
            list_stack.append((indent, node["children"]))
            continue

        numbered_match = re.match(r"^([ \t]*)\d+[.)]\s+(.*)$", line)
        if numbered_match:
            indent_text, content = numbered_match.groups()
            indent = len(indent_text.replace("\t", "    "))

            title, target, is_link = parse_sidebar_item(content)
            if not title:
                continue

            while list_stack and indent <= list_stack[-1][0]:
                list_stack.pop()

            parent_children = list_stack[-1][1] if list_stack else current_base_children()

            node = {
                "title": title,
                "target": target if is_link else None,
                "children": [],
            }
            parent_children.append(node)
            list_stack.append((indent, node["children"]))
            continue

        title, target, is_link = parse_sidebar_item(stripped)
        if not title:
            continue

        if is_link:
            current_base_children().append(
                {"title": title, "target": target, "children": []}
            )
        elif is_plain_heading_candidate(title):
            node = {"title": title, "target": None, "children": []}
            heading_stack[-1][1].append(node)
            current_inline_section_children = node["children"]
        else:
            current_inline_section_children = None

        list_stack = []

    return items


def first_content_page(project_dir: Path) -> Path | None:
    index_md = project_dir / "index.md"
    if index_md.exists():
        return Path("index.md")

    candidates = sorted(
        p.relative_to(project_dir)
        for p in project_dir.rglob("*.md")
        if p.name not in SPECIAL_WIKI_FILES
    )
    return candidates[0] if candidates else None


def nav_page(title: str, path: str) -> dict[str, Any]:
    return {"kind": "page", "title": title, "path": path}


def nav_section(title: str, children: list[dict[str, Any]]) -> dict[str, Any]:
    return {"kind": "section", "title": title, "children": children}


def sidebar_nodes_to_nav(
    sidebar_nodes: list[dict[str, Any]],
    project_dir: Path,
    docs_prefix: str,
    lookup: dict[str, Path],
) -> list[dict[str, Any]]:
    sidebar_file = project_dir / "_Sidebar.md"
    output: list[dict[str, Any]] = []

    for node in sidebar_nodes:
        title = node["title"].strip()
        target = node["target"]
        children = node["children"]

        resolved_rel = None
        if target:
            resolved = resolve_target(target, sidebar_file, project_dir, lookup)
            if resolved and not resolved.startswith("#"):
                resolved_rel = resolved

        if children:
            section_children: list[dict[str, Any]] = []
            if resolved_rel:
                label = "Home" if resolved_rel == "index.md" else "Overview"
                section_children.append(nav_page(label, f"{docs_prefix}/{resolved_rel}"))

            section_children.extend(
                sidebar_nodes_to_nav(children, project_dir, docs_prefix, lookup)
            )

            if section_children:
                output.append(nav_section(title, section_children))
        elif resolved_rel:
            output.append(nav_page(title, f"{docs_prefix}/{resolved_rel}"))

    return output


def fallback_project_nav(project_dir: Path, docs_prefix: str) -> list[dict[str, Any]]:
    pages = sorted(
        p.relative_to(project_dir).as_posix()
        for p in project_dir.rglob("*.md")
        if p.name not in SPECIAL_WIKI_FILES and p.name.lower() != "index.md"
    )

    nodes: list[dict[str, Any]] = []
    for rel in pages:
        title = prettify_title(Path(rel).stem)
        nodes.append(nav_page(title, f"{docs_prefix}/{rel}"))
    return nodes


def collect_nav_paths(nodes: list[dict[str, Any]]) -> set[str]:
    paths: set[str] = set()

    for node in nodes:
        if node["kind"] == "page":
            paths.add(node["path"])
        else:
            paths.update(collect_nav_paths(node["children"]))

    return paths


def collapse_single_overview_section(children: list[dict[str, Any]]) -> list[dict[str, Any]]:
    collapsed: list[dict[str, Any]] = []

    for child in children:
        if child["kind"] == "section":
            title_key = normalize_page_key(child["title"])
            grand_children = child["children"]

            if title_key in {normalize_page_key("Overview"), normalize_page_key("Home")} and grand_children:
                collapsed.extend(collapse_single_overview_section(grand_children))
                continue

            child["children"] = collapse_single_overview_section(grand_children)

        collapsed.append(child)

    return collapsed


def filter_duplicate_home(children: list[dict[str, Any]], home_path: str | None, project_title: str) -> list[dict[str, Any]]:
    if not home_path:
        return children

    filtered: list[dict[str, Any]] = []
    for child in children:
        if child["kind"] == "page":
            same_path = child["path"] == home_path
            title_key = normalize_page_key(child["title"])
            if same_path and title_key in {
                normalize_page_key("Home"),
                normalize_page_key("Overview"),
                normalize_page_key(project_title),
            }:
                continue
        filtered.append(child)
    return filtered


def build_project_nav(project_title: str, project_dir: Path) -> dict[str, Any]:
    docs_prefix = project_dir.name
    lookup = build_page_lookup(project_dir, project_title)
    sidebar_nodes = parse_sidebar(project_dir)
    children = sidebar_nodes_to_nav(sidebar_nodes, project_dir, docs_prefix, lookup)
    children = collapse_single_overview_section(children)

    home_rel = first_content_page(project_dir)
    home_path = f"{docs_prefix}/{home_rel.as_posix()}" if home_rel else None
    children = filter_duplicate_home(children, home_path, project_title)

    final_children: list[dict[str, Any]] = []
    if home_path:
        final_children.append(nav_page("Home", home_path))

    if children:
        final_children.extend(children)

        referenced = collect_nav_paths(final_children)
        extras = [
            node
            for node in fallback_project_nav(project_dir, docs_prefix)
            if node["path"] not in referenced
        ]
        if extras:
            final_children.append(nav_section("Other pages", extras))
    else:
        final_children.extend(fallback_project_nav(project_dir, docs_prefix))

    return nav_section(project_title, final_children)


def yaml_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def render_nav_nodes(nodes: list[dict[str, Any]], indent: int = 2) -> list[str]:
    lines: list[str] = []

    for node in nodes:
        space = " " * indent
        if node["kind"] == "page":
            lines.append(f"{space}- {yaml_quote(node['title'])}: {yaml_quote(node['path'])}")
        else:
            lines.append(f"{space}- {yaml_quote(node['title'])}:")
            lines.extend(render_nav_nodes(node["children"], indent + 4))

    return lines


def build_nav_block(project_navs: list[dict[str, Any]]) -> str:
    lines = ["nav:", "  - 'Home': 'index.md'"]
    lines.extend(render_nav_nodes(project_navs, indent=2))
    return "\n".join(lines) + "\n"


def replace_nav_block(mkdocs_text: str, nav_block: str) -> str:
    lines = mkdocs_text.splitlines(keepends=True)

    start = None
    for i, line in enumerate(lines):
        if re.match(r"^nav:\s*$", line):
            start = i
            break

    if start is None:
        insert_at = 0
        for i, line in enumerate(lines):
            if re.match(r"^(site_url|docs_dir):\s*", line):
                insert_at = i + 1
        lines[insert_at:insert_at] = [nav_block, "\n"]
        return "".join(lines)

    end = len(lines)
    for i in range(start + 1, len(lines)):
        if re.match(r"^[A-Za-z0-9_]+\s*:\s*", lines[i]) and not lines[i].startswith(" "):
            end = i
            break

    new_lines = lines[:start] + [nav_block] + lines[end:]
    return "".join(new_lines)


def update_mkdocs_nav(project_navs: list[dict[str, Any]]) -> None:
    if not MKDOCS_FILE.exists():
        print("[warn  ] mkdocs.yml not found, skipping nav update")
        return

    original = MKDOCS_FILE.read_text(encoding="utf-8")
    updated = replace_nav_block(original, build_nav_block(project_navs))

    if updated != original:
        MKDOCS_FILE.write_text(updated, encoding="utf-8")
        print("[nav   ] mkdocs.yml updated")
    else:
        print("[nav   ] mkdocs.yml already up to date")


def main() -> int:
    if shutil.which("git") is None:
        print("ERROR: git is not installed or not in PATH.")
        return 1

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    project_navs: list[dict[str, Any]] = []

    for project in PROJECTS:
        title = project["title"]
        wiki_url = project["wiki_url"]
        source = clone_or_update_wiki(title, wiki_url)

        if source is None:
            continue

        destination = DOCS_DIR / title
        copy_wiki_contents(source, destination)
        rewrite_links_in_project(destination, title)
        project_navs.append(build_project_nav(title, destination))
        print(f"[done  ] {title}")

    update_mkdocs_nav(project_navs)

    print("\nWiki sync completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
