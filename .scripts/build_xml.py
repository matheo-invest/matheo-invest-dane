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
        if resources is None:
            continue

        resource = resources.find("resource")
        if resource is None:
            continue

        # 2.1. extIdent zasobu z datą
        res_extident = resource.find("extIdent")
        if res_extident is None:
            res_extident = ET.SubElement(resource, "extIdent")
        res_extident.text = f"{ds_ext_ident}_{date_compact}"

        # 2.2. dataDate = dzisiejsza data
        data_date = resource.find("dataDate")
        if data_date is None:
            data_date = ET.SubElement(resource, "dataDate")
        data_date.text = date_str

        # 2.3. Tytuł zasobu
        title = resource.find("title")
        if title is None:
            title = ET.SubElement(resource, "title")

        title_pl = title.find("polish")
        if title_pl is None:
            title_pl = ET.SubElement(title, "polish")
        title_pl.text = f"Ceny ofertowe mieszkań inwestycji {inv_pl} {date_str}"

        title_en = title.find("english")
        if title_en is None:
            title_en = ET.SubElement(title, "english")
        title_en.text = f"Offer prices for apartments in {inv_en} {date_str}"

        # 2.4. Opis zasobu
        descr = resource.find("description")
        if descr is None:
            descr = ET.SubElement(resource, "description")

        descr_pl = descr.find("polish")
        if descr_pl is None:
            descr_pl = ET.SubElement(descr, "polish")
        descr_pl.text = (
            f"Dane dotyczące cen ofertowych mieszkań inwestycji {inv_pl} dewelopera "
            f"Matheo Invest, udostępnione {date_str} zgodnie z art. 19b ust. 1 ustawy "
            f"z dnia 20 maja 2021 r. o ochronie praw nabywcy lokalu mieszkalnego "
            f"lub domu jednorodzinnego oraz Deweloperskim Funduszu Gwarancyjnym "
            f"(Dz. U. z 2024 r. poz. 695)."
        )

        descr_en = descr.find("english")
        if descr_en is None:
            descr_en = ET.SubElement(descr, "english")
        descr_en.text = (
            f"Data on offer prices of apartments in the {inv_en} investment of the "
            f"developer Matheo Invest, made available on {date_str} in accordance "
            f"with art. 19b(1) of the Act of 20 May 2021 on the protection of the "
            f"rights of the buyer of a residential unit or single-family house and "
            f"the Developers' Guarantee Fund."
        )

        # 2.5. Upewniamy się, że wymagane pola istnieją
        availability = resource.find("availability")
        if availability is None:
            availability = ET.SubElement(resource, "availability")
        availability.text = "local"

        specialSigns = resource.find("specialSigns")
        if specialSigns is None:
            specialSigns = ET.SubElement(resource, "specialSigns")
        specialSign = specialSigns.find("specialSign")
        if specialSign is None:
            specialSign = ET.SubElement(specialSigns, "specialSign")
        specialSign.text = "X"

        hasDynamicData = resource.find("hasDynamicData")
        if hasDynamicData is None:
            hasDynamicData = ET.SubElement(resource, "hasDynamicData")
        hasDynamicData.text = "false"

        hasHighValueData = resource.find("hasHighValueData")
        if hasHighValueData is None:
            hasHighValueData = ET.SubElement(resource, "hasHighValueData")
        hasHighValueData.text = "true"

        hasHighValueFromEC = resource.find(
            "hasHighValueDataFromEuropeanCommissionList"
        )
        if hasHighValueFromEC is None:
            hasHighValueFromEC = ET.SubElement(
                resource, "hasHighValueDataFromEuropeanCommissionList"
            )
        hasHighValueFromEC.text = "false"

        hasResearchData = resource.find("hasResearchData")
        if hasResearchData is None:
            hasResearchData = ET.SubElement(resource, "hasResearchData")
        hasResearchData.text = "false"

        containsProtectedData = resource.find("containsProtectedData")
        if containsProtectedData is None:
            containsProtectedData = ET.SubElement(resource, "containsProtectedData")
        containsProtectedData.text = "false"

    # 3. Zapisz zaktualizowany XML
    tree.write(XML_PATH, encoding="UTF-8", xml_declaration=True)

    # 4. Policz MD5 z zapisanego XML i zapisz do pliku .md5
    xml_bytes = XML_PATH.read_bytes()
    md5_hash = hashlib.md5(xml_bytes).hexdigest().upper()

    MD5_PATH.write_text(md5_hash, encoding="utf-8")
    print(f"Updated XML and MD5: {md5_hash}")


if __name__ == "__main__":
    update_xml_and_md5()
