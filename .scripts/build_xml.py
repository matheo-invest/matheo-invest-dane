import hashlib, os, re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASE_URL = "https://matheo-invest.github.io/matheo-invest-dane"
DATASETS_DIR = REPO / "datasets" / "sztabowa"
OUT_XML = REPO / "Matheo_Invest_dane.xml"
OUT_MD5 = REPO / "Matheo_Invest_dane.md5"

def build():
    items = []
    for x in sorted(DATASETS_DIR.glob("*.xlsx")):
        m = re.match(r"(\d{4}-\d{2}-\d{2})\.xlsx$", x.name)
        if not m:
            continue
        date_str = m.group(1)
        url = f"{BASE_URL}/datasets/sztabowa/{x.name}"
        items.append((date_str, url))

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<p:datasets xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
    lines.append('             xsi:noNamespaceSchemaLocation="https://www.dane.gov.pl/static/xml/otwarte_dane_latest.xsd">')
    lines.append('  <dataset status="published">')
    lines.append('    <extIdent>mi_sztabowa_zbior</extIdent>')
    lines.append('    <title><polish>Apartamenty Sztabowa – ceny ofertowe</polish><english>Sztabowa Apartments – offer prices</english></title>')
    lines.append('    <description><polish>Zbiór zawiera aktualne ceny ofertowe mieszkań w inwestycji Apartamenty Sztabowa od Matheo Invest.</polish>')
    lines.append('                <english>The dataset contains current offer prices of apartments in the Sztabowa investment by Matheo Invest.</english></description>')
    lines.append(f'    <url>{BASE_URL}/</url>')
    lines.append('    <categories>ECON</categories>')
    lines.append('    <tags>Deweloper</tags>')
    lines.append('    <updateFrequency>daily</updateFrequency>')
    lines.append('    <hasDynamicData>false</hasDynamicData>')
    lines.append('    <hasHighValueData>true</hasHighValueData>')
    lines.append('    <hasHighValueDataFromEuropeanCommissionList>false</hasHighValueDataFromEuropeanCommissionList>')
    lines.append('    <hasResearchData>false</hasResearchData>')
    lines.append('    <resources>')
    for date_str, url in items:
        lines.append('      <resource status="published">')
        lines.append(f'        <extIdent>mi_sztabowa_{date_str.replace("-", "")}</extIdent>')
        lines.append(f'        <url>{url}</url>')
        lines.append(f'        <title><polish>Ceny ofertowe – {date_str}</polish><english>Offer prices – {date_str}</english></title>')
        lines.append(f'        <description><polish>Dane dotyczące cen ofertowych opublikowane {date_str}.</polish>')
        lines.append(f'                    <english>Offer prices published on {date_str}.</english></description>')
        lines.append('        <availability>local</availability>')
        lines.append(f'        <dataDate>{date_str}</dataDate>')
        lines.append('        <specialSigns><specialSign>X</specialSign></specialSigns>')
        lines.append('        <hasDynamicData>false</hasDynamicData>')
        lines.append('        <hasHighValueData>true</hasHighValueData>')
        lines.append('        <hasHighValueDataFromEuropeanCommissionList>false</hasHighValueDataFromEuropeanCommissionList>')
        lines.append('        <hasResearchData>false</hasResearchData>')
        lines.append('        <containsProtectedData>false</containsProtectedData>')
        lines.append('      </resource>')
    lines.append('    </resources>')
    lines.append('  </dataset>')
    lines.append('</p:datasets>')

    xml = "\n".join(lines)
    OUT_XML.write_text(xml, encoding="utf-8")
    OUT_MD5.write_text(hashlib.md5(xml.encode("utf-8")).hexdigest(), encoding="utf-8")

if __name__ == "__main__":
    build()
