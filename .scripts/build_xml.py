#!/usr/bin/env python3
import datetime
import hashlib
import pathlib
import xml.etree.ElementTree as ET

# Ścieżki plików
ROOT = pathlib.Path(".")
XML_PATH = ROOT / "Matheo_Invest_dane.xml"
MD5_PATH = ROOT / "Matheo_Invest_dane.md5"

# Konfiguracja inwestycji: extIdent datasetu -> nazwy
INVEST_CONFIG = {
    "MATHEO_INVEST_KLEBARK": {
        "pl": "Klebark Park",
        "en": "Klebark Park",
    },
    "MATHEO_INVEST_SZTABOWA": {
        "pl": "Apartamenty Sztabowa",
        "en": "Apartamenty Sztabowa",
    },
}


def update_xml_and_md5():
    today = datetime.date.today()
    date_str = today.strftime("%Y-%m-%d")   # np. 2025-11-20
    date_compact = today.strftime("%Y%m%d") # np. 20251120

    # 1. Wczytaj XML
    tree = ET.parse(XML_PATH)
    root = tree.getroot()

    # 2. Przejdź po wszystkich datasetach (w Twoim XML są BEZ namespace)
    for dataset in root.findall("dataset"):
        ds_ext_ident_elem = dataset.find("extIdent")
        if ds_ext_ident_elem is None or not ds_ext_ident_elem.text:
            continue

        ds_ext_ident = ds_ext_ident_elem.text.strip()
        config = INVEST_CONFIG.get(ds_ext_ident)
        if not config:
            # dataset, którego nie mamy w konfiguracji – pomijamy
            continue

        inv_pl = config["pl"]
        inv_en = config["en"]

        # Szukamy resource w danym datasecie (zakładamy 1 resource na inwestycję)
        resources = dataset.find("resources")
