import re
from typing import Any


# =========================================================
# 1. REGEX PATTERNS
# =========================================================

ARTICLE_PATTERN = re.compile(
    r"^(?:Члан|Član)\s+(\d+[а-яА-Яa-zA-Z]?)\.?$",
    re.IGNORECASE
)

# Examples: ПРВИ ДЕО, ДРУГИ ДЕО, ТРЕЋИ ДЕО
PART_PATTERN = re.compile(
    r"^(ПРВИ|ДРУГИ|ТРЕЋИ|ЧЕТВРТИ|ПЕТИ|ШЕСТИ|СЕДМИ|ОСМИ|ДЕВЕТИ|ДЕСЕТИ)\s+ДЕО(?:\s+(.+))?$",
    re.IGNORECASE
)

# Example: I ОСНОВНЕ ОДРЕДБЕ
CHAPTER_PATTERN = re.compile(
    r"^([IVXLCDM]+)\s+(.+)$",
    re.IGNORECASE
)

# Example: 1.1. Опште одредбе
SUBSECTION_PATTERN = re.compile(
    r"^(\d+(?:\.\d+)+)\.?\s+(.+)$"
)

# Example: 1. Предмет
SECTION_PATTERN = re.compile(
    r"^(\d+)\.\s+(.+)$"
)

FINAL_PART_PATTERN = re.compile(
    r"^(ПРЕЛАЗНЕ И ЗАВРШНЕ ОДРЕДБЕ|ПРЕЛАЗНЕ ОДРЕДБЕ|ЗАВРШНЕ ОДРЕДБЕ|СТУПАЊЕ НА СНАГУ)$",
    re.IGNORECASE
)


# =========================================================
# 2. HELPER FUNCTIONS
# =========================================================

def normalize_text(text: str) -> str:
    """
    Normalizes whitespace for classification.
    Original legal text is preserved separately.
    """
    return " ".join(text.split())


def create_node(
    element_type: str,
    number: str | None = None,
    title: str | None = None
) -> dict[str, Any]:

    node = {
        "type": element_type,
        "children": [],
        "source_element_ids": [],
        "page_numbers": []
    }

    if number is not None:
        node["number"] = number

    if title is not None:
        node["title"] = title

    return node


def add_source_reference(
    node: dict[str, Any],
    element: dict[str, Any],
    page_number: int | None
) -> None:
    """
    Preserves the connection between a structured legal element
    and its original PDF text blocks.
    """

    element_id = element.get("element_id")

    if element_id is not None:
        node["source_element_ids"].append(element_id)

    if page_number is not None:
        node["page_numbers"].append(page_number)


def normalize_references(node: dict[str, Any]) -> None:
    """
    Removes duplicate source IDs and page numbers recursively.
    """

    node["source_element_ids"] = list(
        dict.fromkeys(node["source_element_ids"])
    )

    node["page_numbers"] = list(
        dict.fromkeys(node["page_numbers"])
    )

    for child in node.get("children", []):
        normalize_references(child)


# =========================================================
# 3. DOCUMENT STRUCTURE PARSER
# =========================================================

def parse_legal_structure(raw_content: dict[str, Any]) -> dict[str, Any]:
    """
    Builds the first-level legal structure from raw PDF extraction.

    Supported elements:

        DOCUMENT
        ├── TITLE (stored as document metadata)
        ├── INTRODUCTORY_PART
        ├── MAIN_PART
        │   ├── PART
        │   ├── CHAPTER
        │   ├── SECTION
        │   ├── SUBSECTION
        │   └── ARTICLE
        └── FINAL_PART

    Paragraphs, points, subpoints and alineas
    will be implemented in the next phase.
    """

    # -----------------------------------------------------
    # DOCUMENT ROOT
    # -----------------------------------------------------

    result = {
        "type": "DOCUMENT",
        "title": None,
        "metadata": {
            "document_type": "LAW",
            "country": "RS",
            "language": "sr",
            "publication": None,
            "parser_version": "1.0"
        },
        "children": [],
        "source_element_ids": [],
        "page_numbers": []
    }

    # -----------------------------------------------------
    # CURRENT DOCUMENT CONTAINERS
    # -----------------------------------------------------

    introductory_part = None
    main_part = None
    final_part = None

    active_container = None

    # -----------------------------------------------------
    # CURRENT STRUCTURAL ELEMENTS
    # -----------------------------------------------------

    current_part = None
    current_chapter = None
    current_section = None
    current_subsection = None
    current_article = None

    article_content_parts = []

    # -----------------------------------------------------
    # CONTAINER FUNCTIONS
    # -----------------------------------------------------

    def ensure_main_part():
        nonlocal main_part, active_container

        if main_part is None:
            main_part = create_node("MAIN_PART")
            result["children"].append(main_part)

        active_container = main_part

        return main_part

    def ensure_introductory_part():
        nonlocal introductory_part

        if introductory_part is None:
            introductory_part = create_node("INTRODUCTORY_PART")
            result["children"].append(introductory_part)

        return introductory_part

    def ensure_final_part():
        nonlocal final_part, active_container

        if final_part is None:
            final_part = create_node("FINAL_PART")
            result["children"].append(final_part)

        active_container = final_part

        return final_part

    # -----------------------------------------------------
    # HIERARCHY FUNCTIONS
    # -----------------------------------------------------

    def get_current_parent():

        if current_subsection is not None:
            return current_subsection

        if current_section is not None:
            return current_section

        if current_chapter is not None:
            return current_chapter

        if current_part is not None:
            return current_part

        return active_container

    def close_article():
        nonlocal current_article, article_content_parts

        if current_article is None:
            return

        current_article["content"] = "\n\n".join(
            article_content_parts
        ).strip()

        parent = get_current_parent()

        if parent is not None:
            parent["children"].append(current_article)

        current_article = None
        article_content_parts = []

    def reset_hierarchy():
        nonlocal current_part
        nonlocal current_chapter
        nonlocal current_section
        nonlocal current_subsection

        close_article()

        current_part = None
        current_chapter = None
        current_section = None
        current_subsection = None

    # -----------------------------------------------------
    # RAW EXTRACTION ITERATOR
    # -----------------------------------------------------

    def get_elements():

        for page in raw_content.get("pages", []):

            page_number = page.get("page_number")

            for element in page.get("elements", []):

                yield element, page_number

    # -----------------------------------------------------
    # PROCESS PDF ELEMENTS
    # -----------------------------------------------------

    for element, page_number in get_elements():

        original_text = element.get("text") or ""
        text = normalize_text(original_text)

        if not text:
            continue

        # -------------------------------------------------
        # DOCUMENT TITLE
        # -------------------------------------------------

        if result["title"] is None:

            result["title"] = text

            add_source_reference(
                result,
                element,
                page_number
            )

            continue

        # -------------------------------------------------
        # PUBLICATION INFORMATION
        # -------------------------------------------------

        if (
            result["metadata"]["publication"] is None
            and main_part is None
            and re.search(
                r"Службени гласник|Službeni glasnik",
                text,
                re.IGNORECASE
            )
        ):

            result["metadata"]["publication"] = original_text

            add_source_reference(
                result,
                element,
                page_number
            )

            continue

        # -------------------------------------------------
        # FINAL PART
        # -------------------------------------------------

        if FINAL_PART_PATTERN.fullmatch(text):

            reset_hierarchy()

            final_part = ensure_final_part()
            final_part["title"] = text

            add_source_reference(
                final_part,
                element,
                page_number
            )

            continue

        # -------------------------------------------------
        # PART
        # -------------------------------------------------

        part_match = PART_PATTERN.fullmatch(text)

        if part_match:

            ensure_main_part()
            reset_hierarchy()

            current_part = create_node(
                "PART",
                number=part_match.group(1),
                title=part_match.group(2)
            )

            main_part["children"].append(current_part)

            add_source_reference(
                current_part,
                element,
                page_number
            )

            continue

        # -------------------------------------------------
        # CHAPTER
        # -------------------------------------------------

        chapter_match = CHAPTER_PATTERN.fullmatch(text)

        if chapter_match:

            chapter_title = normalize_text(
                chapter_match.group(2)
            )

            reset_hierarchy()

            if active_container is None:
                ensure_main_part()

            parent = get_current_parent()

            current_chapter = create_node(
                "CHAPTER",
                number=chapter_match.group(1),
                title=chapter_title
            )

            parent["children"].append(current_chapter)

            add_source_reference(
                current_chapter,
                element,
                page_number
            )

            continue

        # -------------------------------------------------
        # SUBSECTION
        # -------------------------------------------------

        subsection_match = SUBSECTION_PATTERN.fullmatch(text)

        if subsection_match:

            if active_container is None:
                ensure_main_part()

            close_article()

            current_subsection = None

            parent = get_current_parent()

            current_subsection = create_node(
                "SUBSECTION",
                number=subsection_match.group(1),
                title=normalize_text(subsection_match.group(2))
            )

            parent["children"].append(current_subsection)

            add_source_reference(
                current_subsection,
                element,
                page_number
            )

            continue

        # -------------------------------------------------
        # SECTION
        # -------------------------------------------------

        section_match = SECTION_PATTERN.fullmatch(text)

        if section_match:

            if active_container is None:
                ensure_main_part()

            close_article()

            current_section = None
            current_subsection = None

            parent = (
                current_chapter
                if current_chapter is not None
                else current_part
                if current_part is not None
                else active_container
            )

            current_section = create_node(
                "SECTION",
                number=section_match.group(1),
                title=normalize_text(section_match.group(2))
            )

            parent["children"].append(current_section)

            add_source_reference(
                current_section,
                element,
                page_number
            )

            continue

        # -------------------------------------------------
        # ARTICLE
        # -------------------------------------------------

        article_match = ARTICLE_PATTERN.fullmatch(text)

        if article_match:

            if active_container is None:
                ensure_main_part()

            close_article()

            current_article = create_node(
                "ARTICLE",
                number=article_match.group(1)
            )

            add_source_reference(
                current_article,
                element,
                page_number
            )

            continue

        # -------------------------------------------------
        # INTRODUCTORY CONTENT
        # -------------------------------------------------

        if main_part is None and final_part is None:

            introductory_part = ensure_introductory_part()

            introductory_part.setdefault(
                "content_parts", []
            ).append(original_text)

            add_source_reference(
                introductory_part,
                element,
                page_number
            )

            continue

        # -------------------------------------------------
        # ARTICLE CONTENT
        # -------------------------------------------------

        if current_article is not None:

            article_content_parts.append(original_text)

            add_source_reference(
                current_article,
                element,
                page_number
            )

    # -----------------------------------------------------
    # CLOSE LAST ARTICLE
    # -----------------------------------------------------

    close_article()

    # -----------------------------------------------------
    # FINAL NORMALIZATION
    # -----------------------------------------------------

    if introductory_part is not None:

        introductory_part["content"] = "\n\n".join(
            introductory_part.pop("content_parts", [])
        ).strip()

    normalize_references(result)

    return result
