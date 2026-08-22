"""One-off importer for the real "АгроВзгляд" content pack (cource_1/) —
10 topics, each with a lecture (text + inline photo examples) and 30
photocases. Run locally (see instructions at the bottom of this file), not
part of the normal app runtime.
"""

import asyncio
import re
import shutil
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from app.core.config import get_settings
from app.crud import content_item as content_item_crud
from app.crud import content_item_image as image_crud
from app.crud import course as course_crud
from app.crud import photocase as photocase_crud
from app.crud import tag as tag_crud
from app.crud import topic as topic_crud
from app.crud import user as user_crud
from app.db.base import async_session_maker
from app.models.content_item import ContentItemType

settings = get_settings()

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "cource_1" / "Курс_АгроВзгляд"
COURSE_SLUG_TITLE = "Визуальная диагностика проблем растений"

OPTION_LETTERS = ["А", "Б", "В", "Г"]


# --------------------------------------------------------------------------
# Small markdown helpers
# --------------------------------------------------------------------------


def inline_format(text: str) -> str:
    """**bold** -> <strong>, [text](url) -> <a>, applied to a text span."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<a href="\2" target="_blank" rel="noopener">\1</a>',
        text,
    )
    return text


@dataclass
class CatalogEntry:
    label: str
    hints: str
    author: str
    license_text: str
    license_url: str
    source_text: str
    source_url: str


def parse_catalog(path: Path) -> dict[str, CatalogEntry]:
    if not path.exists():
        return {}
    entries: dict[str, CatalogEntry] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        if re.match(r"^\|[\s:-]+\|", line) or line.startswith("| №"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        num, label, hints, author, license_md, source_md = cells[:6]
        license_match = re.match(r"\[([^\]]+)\]\(([^)]*)\)", license_md)
        source_match = re.match(r"\[([^\]]+)\]\(([^)]*)\)", source_md)
        entries[num] = CatalogEntry(
            label=label,
            hints=hints,
            author=author,
            license_text=license_match.group(1) if license_match else license_md,
            license_url=license_match.group(2) if license_match else "",
            source_text=source_match.group(1) if source_match else source_md,
            source_url=source_match.group(2) if source_match else "",
        )
    return entries


IMAGE_CELL_RE = re.compile(r"\[!\[[^\]]*\]\(([^)]+)\)\]\([^)]+\)<br>\*\*([^*]+)\*\*")


def render_table_row_images(row: str, topic_dir: Path, catalog: dict[str, CatalogEntry], image_cache: dict) -> str:
    html_parts = []
    for src, caption in IMAGE_CELL_RE.findall(row):
        src_path = (topic_dir / src).resolve()
        if not src_path.exists():
            continue
        url = get_or_copy_image(src_path, image_cache)
        num_match = re.match(r"(\d+)", caption)
        entry = catalog.get(num_match.group(1)) if num_match else None
        html_parts.append(f'<img src="{url}" alt="{caption}">')
        html_parts.append(f"<p><strong>{caption}</strong></p>")
        if entry and entry.author:
            credit = f"Фото: {entry.author}. Лицензия: {entry.license_text}"
            if entry.source_url:
                credit += f' (<a href="{entry.source_url}" target="_blank" rel="noopener">источник</a>)'
            html_parts.append(f'<p><em>{credit}.</em></p>')
    return "".join(html_parts)


def get_or_copy_image(src_path: Path, cache: dict[Path, str]) -> str:
    if src_path in cache:
        return cache[src_path]
    subdir = cache["__subdir__"]
    ext = src_path.suffix.lower()
    filename = f"{uuid.uuid4()}{ext}"
    target_dir = Path(settings.media_root) / "images" / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src_path, target_dir / filename)
    url = f"/media/images/{subdir}/{filename}"
    cache[src_path] = url
    return url


# The expert agronomy/phytopathology review this content pack asked for has
# since happened and came back clean, so the "draft pending review" framing
# and the click-to-enlarge instruction (there's no click-to-enlarge in the
# lecture body — that's only wired up for the standalone photo gallery) no
# longer apply. Each substitution keeps any still-useful methodological point
# and drops only the review-status claim.
REVIEW_STATUS_FIXES = [
    (
        "Статус: учебный черновик; требуется агрономическая и методическая проверка. "
        "Визуальные признаки дают предварительную гипотезу, а не окончательный лабораторный диагноз.",
        "Визуальные признаки дают предварительную гипотезу, которую уточняют дополнительным осмотром "
        "и, при необходимости, лабораторным тестом.",
    ),
    (" Нажмите на изображение, чтобы открыть исходный файл.", ""),
    (
        "Метки ожидают экспертной проверки и не заменяют лабораторный диагноз.",
        "Визуальная метка не заменяет лабораторный диагноз.",
    ),
    (" Метка отражает контекст страницы-источника и также подлежит экспертной проверке.", ""),
    ("## Источники для экспертной сверки", "## Дополнительные источники"),
]


def apply_review_status_fixes(md_text: str) -> str:
    for old, new in REVIEW_STATUS_FIXES:
        md_text = md_text.replace(old, new)
    return md_text


def render_lecture_markdown(md_text: str, topic_dir: Path, catalog: dict[str, CatalogEntry], subdir: str) -> str:
    md_text = apply_review_status_fixes(md_text)
    image_cache: dict = {"__subdir__": subdir}
    lines = md_text.splitlines()
    html: list[str] = []
    i = 0
    n = len(lines)

    def flush_paragraph(buf: list[str]):
        if buf:
            html.append(f"<p>{inline_format(' '.join(buf))}</p>")
            buf.clear()

    para_buf: list[str] = []

    while i < n:
        line = lines[i].rstrip()

        if line.startswith("<!--"):
            i += 1
            continue
        if not line.strip():
            flush_paragraph(para_buf)
            i += 1
            continue
        if line.startswith("# ") and i == 0:
            # document title handled separately by the caller
            i += 1
            continue
        if line.startswith("#### "):
            flush_paragraph(para_buf)
            html.append(f"<h4>{inline_format(line[5:].strip())}</h4>")
            i += 1
            continue
        if line.startswith("### "):
            flush_paragraph(para_buf)
            html.append(f"<h3>{inline_format(line[4:].strip())}</h3>")
            i += 1
            continue
        if line.startswith("## "):
            flush_paragraph(para_buf)
            html.append(f"<h2>{inline_format(line[3:].strip())}</h2>")
            i += 1
            continue
        if line.startswith("> "):
            flush_paragraph(para_buf)
            quote_lines = []
            while i < n and lines[i].startswith(">"):
                quote_lines.append(lines[i].lstrip(">").strip())
                i += 1
            html.append(f"<blockquote><p>{inline_format(' '.join(quote_lines))}</p></blockquote>")
            continue
        if line.startswith("| ["):
            flush_paragraph(para_buf)
            html.append(render_table_row_images(line, topic_dir, catalog, image_cache))
            i += 1
            # skip the separator row(s) and any following image rows belonging to the same table
            while i < n and (re.match(r"^\|[\s:-]+\|", lines[i]) or lines[i].startswith("| [")):
                if lines[i].startswith("| ["):
                    html.append(render_table_row_images(lines[i], topic_dir, catalog, image_cache))
                i += 1
            continue
        if re.match(r"^\d+\. ", line):
            flush_paragraph(para_buf)
            items = []
            while i < n and re.match(r"^\d+\. ", lines[i]):
                items.append(f"<li>{inline_format(re.sub(r'^\d+\. ', '', lines[i]))}</li>")
                i += 1
            html.append(f"<ol>{''.join(items)}</ol>")
            continue
        if line.startswith("- "):
            flush_paragraph(para_buf)
            items = []
            while i < n and lines[i].startswith("- "):
                items.append(f"<li>{inline_format(lines[i][2:])}</li>")
                i += 1
            html.append(f"<ul>{''.join(items)}</ul>")
            continue

        para_buf.append(line.strip())
        i += 1

    flush_paragraph(para_buf)
    return "\n".join(html)


# --------------------------------------------------------------------------
# Photocase parsing
# --------------------------------------------------------------------------


@dataclass
class CaseOption:
    letter: str
    label: str
    is_correct: bool = False
    explanation: str = ""


@dataclass
class ParsedCase:
    image_filename: str
    attribution: str
    question_intro: str
    options: list[CaseOption]
    next_steps: str


def build_plain_attribution(text: str) -> str:
    """Attribution renders inside a plain-text field on the frontend (no HTML),
    so build a readable plain string instead of reusing inline_format's <a> tags."""
    author_match = re.search(r"Автор: (.+?)\. Лицензия:", text)
    license_match = re.search(r"Лицензия: \[([^\]]+)\]\(([^)]*)\)", text)
    source_match = re.search(r"Страница изображения: \[[^\]]+\]\(([^)]+)\)", text)

    parts = []
    if author_match:
        parts.append(f"Автор: {author_match.group(1).strip()}")
    if license_match:
        license_text = license_match.group(1)
        license_url = license_match.group(2)
        parts.append(f"Лицензия: {license_text}" + (f" ({license_url})" if license_url else ""))
    if source_match:
        parts.append(f"Источник: {source_match.group(1)}")
    return "Атрибуция фото. " + ". ".join(parts) + "." if parts else ""


def parse_case_file(path: Path) -> ParsedCase:
    text = path.read_text(encoding="utf-8")

    image_match = re.search(r"!\[Диагностическое фото\]\(([^)]+)\)", text)
    image_filename = image_match.group(1) if image_match else ""

    attribution = build_plain_attribution(text)

    situation_match = re.search(
        r"## Ситуация и вопрос\s*\n\n(.+?)\n\n[АБВГ]\. ", text, re.DOTALL
    )
    question_intro = situation_match.group(1).strip().replace("\n", " ") if situation_match else ""

    options: dict[str, CaseOption] = {}
    for letter, label in re.findall(r"^([АБВГ])\. (.+)$", text, re.MULTILINE):
        options[letter] = CaseOption(letter=letter, label=label.strip())

    for letter, verdict, explanation in re.findall(
        r"^\*\*([АБВГ]) — (правильный|неправильный)\.\*\* (.+)$", text, re.MULTILINE
    ):
        if letter in options:
            options[letter].is_correct = verdict == "правильный"
            options[letter].explanation = explanation.strip()

    next_steps_match = re.search(r"## Что проверить до практического решения\s*\n\n(.+)$", text, re.DOTALL)
    next_steps = next_steps_match.group(1).strip().replace("\n", " ") if next_steps_match else ""

    return ParsedCase(
        image_filename=image_filename,
        attribution=attribution,
        question_intro=question_intro,
        options=[options[letter] for letter in OPTION_LETTERS if letter in options],
        next_steps=next_steps,
    )


# --------------------------------------------------------------------------
# Import orchestration
# --------------------------------------------------------------------------


def topic_folders() -> list[Path]:
    return sorted(p for p in SOURCE_ROOT.iterdir() if p.is_dir() and re.match(r"^\d{2}_", p.name))


TOPIC_TITLE_OVERRIDES = {
    "Дефицит азота фосфора калия": "Дефицит азота, фосфора и калия",
}


def topic_title(folder: Path) -> str:
    raw = re.sub(r"^\d{2}_", "", folder.name).replace("_", " ")
    return TOPIC_TITLE_OVERRIDES.get(raw, raw)


async def import_topic(db, course_id, folder: Path, order_index: int) -> None:
    title = topic_title(folder)
    print(f"[import] topic {order_index}: {title}")

    topic = await topic_crud.create_topic(db, course_id=course_id, title=title, description="", order_index=order_index)

    lecture_path = folder / "Лекция.md"
    lecture_md = lecture_path.read_text(encoding="utf-8")
    lecture_title_match = re.search(r"^# Лекция \d+\.\s*(.+)$", lecture_md, re.MULTILINE)
    lecture_title = lecture_title_match.group(1).strip() if lecture_title_match else title

    lecture_item = await content_item_crud.create_content_item(
        db, topic_id=topic.id, type=ContentItemType.text_lecture, title=lecture_title, order_index=0, text_body=""
    )

    catalog = parse_catalog(folder / "фото-примеры" / "Каталог.md")
    lecture_html = render_lecture_markdown(lecture_md, folder, catalog, subdir=str(lecture_item.id))
    await content_item_crud.update_content_item(db, lecture_item, text_body=lecture_html)

    case_files = sorted((folder / "фото-кейсы").glob("*.md"))
    for case_index, case_path in enumerate(case_files, start=1):
        parsed = parse_case_file(case_path)
        if not parsed.options or not parsed.image_filename:
            print(f"  [skip] {case_path.name}: incomplete parse")
            continue

        correct = next((o for o in parsed.options if o.is_correct), None)
        case_title = f"Кейс {case_index:03d}: {correct.label if correct else '?'}"

        case_item = await content_item_crud.create_content_item(
            db,
            topic_id=topic.id,
            type=ContentItemType.photocase,
            title=case_title,
            order_index=case_index,
            text_body=parsed.question_intro or None,
        )

        next_steps = parsed.next_steps
        if parsed.attribution:
            next_steps = f"{next_steps}\n\n{parsed.attribution}".strip()

        await content_item_crud.update_content_item(
            db,
            case_item,
            key_signs=(correct.explanation if correct else None),
            next_steps=next_steps or None,
        )

        image_src = (folder / "фото-кейсы" / parsed.image_filename).resolve()
        if image_src.exists():
            image_cache: dict = {"__subdir__": str(case_item.id)}
            url = get_or_copy_image(image_src, image_cache)
            await image_crud.add_image(db, content_item_id=case_item.id, image_path=url)

        for option in parsed.options:
            await photocase_crud.create_option(
                db,
                content_item_id=case_item.id,
                label=option.label,
                is_correct=option.is_correct,
                explanation=option.explanation,
                order_index=OPTION_LETTERS.index(option.letter),
            )

    print(f"  -> {len(case_files)} cases imported")


async def main() -> None:
    async with async_session_maker() as db:
        existing = await course_crud.get_by_slug(db, "vizualnaya-diagnostika-problem-rasteniy")
        if existing is not None:
            print("[import] course already exists, aborting (delete it first to re-import)")
            return

        admin = await user_crud.get_by_email(db, "admin@agrovision.ru")
        if admin is None:
            print("[import] admin user not found — run app.seed first")
            return

        diagnostics_tag = await tag_crud.create_tag(db, "Диагностика")
        field_crops_tag = await tag_crud.create_tag(db, "Полевые культуры")

        course = await course_crud.create_course(
            db,
            title=COURSE_SLUG_TITLE,
            description=(
                "Полный курс визуальной диагностики проблем растений: 10 учебных тем, "
                "каждая с конспектом лекции и 30 фотокейсами на реальных фотографиях "
                "(300 фотокейсов и 300 фото-примеров всего). Материалы проверены агрономом; "
                "источники и лицензии указаны при каждом фото."
            ),
            price=0,
            tag_ids=[diagnostics_tag.id, field_crops_tag.id],
            created_by=admin.id,
        )
        print(f"[import] created course: {course.title} ({course.slug}) — left unpublished (draft)")

        for order_index, folder in enumerate(topic_folders()):
            await import_topic(db, course.id, folder, order_index)

        print("[import] done")


if __name__ == "__main__":
    asyncio.run(main())

# To run locally against the dockerized Postgres + media volume:
#   cd backend
#   python3 -m venv .venv_import && source .venv_import/bin/activate
#   pip install -r requirements.txt
#   DATABASE_URL=postgresql+asyncpg://agrovision:agrovision@localhost:5432/agrovision \
#   MEDIA_ROOT=/absolute/path/to/backend/media \
#   python -m app.import_course_1
