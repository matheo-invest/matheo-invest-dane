from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import re
import shutil
import xml.etree.ElementTree as ET


# ---------------------------------------------------------
# ŚCIEŻKI
# ---------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

XML_PATH = ROOT_DIR / "Matheo_Invest_dane.xml"
MD5_PATH = ROOT_DIR / "Matheo_Invest_dane.md5"

PAGES_BASE_URL = "https://matheo-invest.github.io/matheo-invest-dane"


# ---------------------------------------------------------
# DATA - CZAS POLSKI
# ---------------------------------------------------------

today = datetime.now(ZoneInfo("Europe/Warsaw")).date()

date_str = today.strftime("%Y-%m-%d")
date_compact = today.strftime("%Y%m%d")


# ---------------------------------------------------------
# KONFIGURACJA INWESTYCJI
# ---------------------------------------------------------

DATASETS = {
    "MATHEO_INVEST_KLEBARK": {
        "source": ROOT_DIR / "datasets" / "klebark" / "ceny.xlsx",
        "archive_dir": ROOT_DIR / "datasets" / "klebark" / "archive",
        "archive_url": f"{PAGES_BASE_URL}/datasets/klebark/archive",
    },
    "MATHEO_INVEST_SZTABOWA": {
        "source": ROOT_DIR / "datasets" / "sztabowa" / "ceny.xlsx",
        "archive_dir": ROOT_DIR / "datasets" / "sztabowa" / "archive",
        "archive_url": f"{PAGES_BASE_URL}/datasets/sztabowa/archive",
    },
}


# ---------------------------------------------------------
# FUNKCJE POMOCNICZE
# ---------------------------------------------------------

def local_name(tag):
    """Zwraca nazwę elementu XML bez namespace."""
    return tag.split("}", 1)[-1]


def find_child(parent, name):
    """Znajduje bezpośrednie dziecko niezależnie od namespace."""
    for child in parent:
        if local_name(child.tag) == name:
            return child
    return None


def find_children(parent, name):
    """Znajduje wszystkie bezpośrednie dzieci o podanej nazwie."""
    return [
        child
        for child in parent
        if local_name(child.tag) == name
    ]


def replace_date(text):
    """
    Zamienia datę YYYY-MM-DD znajdującą się w istniejącym
    tytule lub opisie na dzisiejszą datę.
    """
    if not text:
        return text

    return re.sub(
        r"\b\d{4}-\d{2}-\d{2}\b",
        date_str,
        text
    )


# ---------------------------------------------------------
# WCZYTANIE XML
# ---------------------------------------------------------

tree = ET.parse(XML_PATH)
root = tree.getroot()

processed_datasets = []


# ---------------------------------------------------------
# AKTUALIZACJA KAŻDEGO DATASETU
# ---------------------------------------------------------

for dataset in root:
    if local_name(dataset.tag) != "dataset":
        continue

    dataset_ext_ident_element = find_child(dataset, "extIdent")

    if dataset_ext_ident_element is None:
        continue

    dataset_ext_ident = (dataset_ext_ident_element.text or "").strip()

    if dataset_ext_ident not in DATASETS:
        continue

    config = DATASETS[dataset_ext_ident]

    source_file = config["source"]
    archive_dir = config["archive_dir"]
    archive_url = config["archive_url"]

    # -----------------------------------------------------
    # SPRAWDZENIE PLIKU ŹRÓDŁOWEGO
    # -----------------------------------------------------

    if not source_file.exists():
        raise FileNotFoundError(
            f"Nie znaleziono pliku źródłowego: {source_file}"
        )

    # -----------------------------------------------------
    # UTWORZENIE DZIENNEGO SNAPSHOTA XLSX
    # -----------------------------------------------------

    archive_dir.mkdir(parents=True, exist_ok=True)

    archive_filename = f"ceny_{date_str}.xlsx"
    archive_file = archive_dir / archive_filename

    # Jeżeli workflow zostanie uruchomiony ponownie tego samego dnia,
    # snapshot tego dnia zostanie zaktualizowany najnowszym plikiem.
    shutil.copy2(source_file, archive_file)

    # -----------------------------------------------------
    # ZNALEZIENIE RESOURCE W XML
    # -----------------------------------------------------

    resources = find_child(dataset, "resources")

    if resources is None:
        raise RuntimeError(
            f"Brak sekcji <resources> dla {dataset_ext_ident}"
        )

    resource = find_child(resources, "resource")

    if resource is None:
        raise RuntimeError(
            f"Brak sekcji <resource> dla {dataset_ext_ident}"
        )

    # -----------------------------------------------------
    # EXTIDENT Z DATĄ
    # -----------------------------------------------------

    resource_ext_ident = find_child(resource, "extIdent")

    if resource_ext_ident is None:
        raise RuntimeError(
            f"Brak <extIdent> zasobu dla {dataset_ext_ident}"
        )

    resource_ext_ident.text = (
        f"{dataset_ext_ident}_{date_compact}"
    )

    # -----------------------------------------------------
    # URL DO NIEZMIENNEGO SNAPSHOTA
    # -----------------------------------------------------

    url = find_child(resource, "url")

    if url is None:
        raise RuntimeError(
            f"Brak <url> zasobu dla {dataset_ext_ident}"
        )

    url.text = f"{archive_url}/{archive_filename}"

    # -----------------------------------------------------
    # DATA ZASOBU
    # -----------------------------------------------------

    data_date = find_child(resource, "dataDate")

    if data_date is None:
        raise RuntimeError(
            f"Brak <dataDate> dla {dataset_ext_ident}"
        )

    data_date.text = date_str

    # -----------------------------------------------------
    # TYTUŁY ZASOBU
    # -----------------------------------------------------

    for title in find_children(resource, "title"):
        title.text = replace_date(title.text)

    # -----------------------------------------------------
    # OPISY ZASOBU
    # -----------------------------------------------------

    for description in find_children(resource, "description"):
        description.text = replace_date(description.text)

    # -----------------------------------------------------
    # DOSTĘPNOŚĆ
    # -----------------------------------------------------

    availability = find_child(resource, "availability")

    if availability is not None:
        availability.text = "local"

    # -----------------------------------------------------
    # SPECIAL SIGN
    # -----------------------------------------------------

    special_signs = find_child(resource, "specialSigns")

    if special_signs is not None:
        special_sign = find_child(special_signs, "specialSign")

        if special_sign is not None:
            special_sign.text = "X"

    processed_datasets.append(dataset_ext_ident)


# ---------------------------------------------------------
# KONTROLA
# ---------------------------------------------------------

if not processed_datasets:
    raise RuntimeError(
        "Nie znaleziono żadnego obsługiwanego datasetu w XML."
    )


# ---------------------------------------------------------
# ZAPIS XML
# ---------------------------------------------------------

ET.indent(tree, space="  ")

tree.write(
    XML_PATH,
    encoding="UTF-8",
    xml_declaration=True
)


# ---------------------------------------------------------
# MD5
# ---------------------------------------------------------

md5_hash = hashlib.md5(XML_PATH.read_bytes()).hexdigest().upper()

MD5_PATH.write_text(
    md5_hash + "\n",
    encoding="UTF-8"
)


# ---------------------------------------------------------
# LOG
# ---------------------------------------------------------

print(f"Data publikacji: {date_str}")

for dataset_name in processed_datasets:
    print(f"Zaktualizowano: {dataset_name}")

print(f"MD5: {md5_hash}")
print("XML, snapshoty XLSX i MD5 zostały przygotowane.")
