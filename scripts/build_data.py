#!/usr/bin/env python3
"""Convert the NUS SoC SEP pre-approved course mapping list (ps.xls, actually
an HTML table saved with an .xls extension) into a single data.json consumed
by the static front end.
"""
import json
import math
import re
from pathlib import Path

import pandas as pd

SRC = Path("/Users/carls/Downloads/ps.xls")
OUT = Path(__file__).resolve().parent.parent / "data" / "data.json"

# Best-effort country/region tagging for filtering purposes only.
# Not exhaustive facts about the institution -- just a browsing aid.
COUNTRY = {
    "Aachen University of Technology": "Germany",
    "Aalto University": "Finland",
    "Aarhus University": "Denmark",
    "Arizona State University": "United States",
    "Australian National University, The": "Australia",
    "Beihang University": "China",
    "Bilkent University": "Turkey",
    "Bogazici University, Turkey": "Turkey",
    "Boston College": "United States",
    "Boston University": "United States",
    "Brandeis University": "United States",
    "Budapest University of Technology and Economics": "Hungary",
    "Carnegie Mellon University": "United States",
    "Case Western Reserve University": "United States",
    "Chalmers University of Technology": "Sweden",
    "Chang Gung University": "Taiwan",
    "Chinese University of Hong Kong, The": "Hong Kong",
    "Chulalongkorn University": "Thailand",
    "City University of Hong Kong": "Hong Kong",
    "Clarkson University": "United States",
    "Colgate University": "United States",
    "Columbia University": "United States",
    "Concordia University": "Canada",
    "Cornell Univ Coll of Agriculture & Life Sciences": "United States",
    "Cornell Univ Coll of Human Ecology": "United States",
    "Cracow University of Technology": "Poland",
    "Dalhousie University": "Canada",
    "Delft University of Technology": "Netherlands",
    "Duke University": "United States",
    "ETH Zurich": "Switzerland",
    "Ecole Polytechnique Federale de Lausanne (EPFL)": "Switzerland",
    "Eindhoven University of Technology": "Netherlands",
    "Ewha Women's University,Seoul": "South Korea",
    "Fudan University": "China",
    "George Washington University, The": "United States",
    "Georgetown University": "United States",
    "Georgia Institute of Technology": "United States",
    "HEC Montreal": "Canada",
    "Hamburg University of Technology": "Germany",
    "Heidelberg University": "Germany",
    "Hong Kong Polytechnic University, The": "Hong Kong",
    "Hong Kong University of Science & Technology": "Hong Kong",
    "INSA Lyon": "France",
    "Imperial College London": "United Kingdom",
    "Indiana University, Bloomington": "United States",
    "Institute of Science Tokyo": "Japan",
    "Iowa State University": "United States",
    "Johns Hopkins University": "United States",
    "KTH-Royal Institute of Technology": "Sweden",
    "KU Leuven": "Belgium",
    "Karlsruhe Institute of Technology": "Germany",
    "Keio University": "Japan",
    "King's College London": "United Kingdom",
    "Korea Advanced Institute of Science and Technology": "South Korea",
    "Korea University": "South Korea",
    "Kyoto University": "Japan",
    "Kyushu University": "Japan",
    "LaTrobe University": "Australia",
    "Linkoping University": "Sweden",
    "London School of Economics & Political Science": "United Kingdom",
    "Ludwig Maximilian University of Munich": "Germany",
    "Lund University": "Sweden",
    "McGill University": "Canada",
    "Monash University": "Australia",
    "Nagoya University": "Japan",
    "Nanjing University": "China",
    "Nanyang Technological University": "Singapore",
    "National Cheng Kung University": "Taiwan",
    "National Chengchi University": "Taiwan",
    "National Chiao Tung University": "Taiwan",
    "National Taiwan University": "Taiwan",
    "National Tsing Hua University": "Taiwan",
    "National Yang Ming Chiao Tung University": "Taiwan",
    "New York University": "United States",
    "Newcastle University": "United Kingdom",
    "Northwestern University": "United States",
    "Norwegian School of Economics": "Norway",
    "Norwegian University of Science and Technology": "Norway",
    "Peking University": "China",
    "Pennsylvania State University, The": "United States",
    "Pohang University of Science and Technology": "South Korea",
    "Purdue University": "United States",
    "Queen's University at Kingston": "Canada",
    "RWTH Aachen University": "Germany",
    "Reichman University": "Israel",
    "Renmin University of China": "China",
    "Richard Ivey Sch of Biz, Univ of Western Ontario": "Canada",
    "Sabanci University": "Turkey",
    "Seoul National University": "South Korea",
    "Shanghai Jiao Tong University": "China",
    "Shanghai University of Finance and Economics": "China",
    "Simon Fraser University": "Canada",
    "Singapore Institute of Technology": "Singapore",
    "Singapore Management University": "Singapore",
    "Singapore University of Social Sciences": "Singapore",
    "Singapore University of Technology and Design": "Singapore",
    "Stanford University": "United States",
    "Stockholm University": "Sweden",
    "Sungkyunkwan University": "South Korea",
    "Swiss Federal Institute of Technology Lausanne": "Switzerland",
    "Tallinn University of Technology": "Estonia",
    "Tec de Monterrey": "Mexico",
    "Technical University of Berlin": "Germany",
    "Technical University of Darmstadt": "Germany",
    "Technical University of Denmark": "Denmark",
    "Technical University of Munich": "Germany",
    "Telecom Paris": "France",
    "Texas A&M University": "United States",
    "The University of Adelaide": "Australia",
    "Tilburg University": "Netherlands",
    "Tohoku University": "Japan",
    "Tongji University": "China",
    "Trinity College Dublin": "Ireland",
    "Tsinghua University": "China",
    "Tulane University": "United States",
    "Universitat Autonoma de Barcelona": "Spain",
    "Universite Grenoble Alpes": "France",
    "University College Cork": "Ireland",
    "University College Dublin": "Ireland",
    "University College London": "United Kingdom",
    "University of Alberta": "Canada",
    "University of Amsterdam": "Netherlands",
    "University of Antwerp": "Belgium",
    "University of Applied Sciences Esslingen": "Germany",
    "University of Arizona, The": "United States",
    "University of Auckland, The": "New Zealand",
    "University of Bath": "United Kingdom",
    "University of Birmingham": "United Kingdom",
    "University of Bologna": "Italy",
    "University of Bristol": "United Kingdom",
    "University of British Columbia, The": "Canada",
    "University of Calgary": "Canada",
    "University of California": "United States",
    "University of California, Davis": "United States",
    "University of California, Irvine": "United States",
    "University of California, Los Angeles": "United States",
    "University of California, Merced": "United States",
    "University of California, Riverside": "United States",
    "University of California, San Diego": "United States",
    "University of California, Santa Barbara": "United States",
    "University of California, Santa Cruz": "United States",
    "University of Colorado Boulder": "United States",
    "University of Commerce 'Luigi Bocconi' Milan": "Italy",
    "University of Connecticut": "United States",
    "University of Copenhagen": "Denmark",
    "University of Dundee": "United Kingdom",
    "University of Edinburgh, The": "United Kingdom",
    "University of Freiburg": "Germany",
    "University of Geneva": "Switzerland",
    "University of Georgia": "United States",
    "University of Glasgow": "United Kingdom",
    "University of Goteborg": "Sweden",
    "University of Gothenburg": "Sweden",
    "University of Guelph": "Canada",
    "University of Hawaii at Manoa": "United States",
    "University of Helsinki": "Finland",
    "University of Hohenheim": "Germany",
    "University of Hong Kong, The": "Hong Kong",
    "University of Iceland": "Iceland",
    "University of Illinois Urbana-Champaign": "United States",
    "University of Kaiserslautern, FRG": "Germany",
    "University of Konstanz": "Germany",
    "University of Lausanne": "Switzerland",
    "University of Leeds": "United Kingdom",
    "University of Liverpool": "United Kingdom",
    "University of Manchester, The": "United Kingdom",
    "University of Mannheim": "Germany",
    "University of Maryland": "United States",
    "University of Melbourne, The": "Australia",
    "University of Miami": "United States",
    "University of Michigan": "United States",
    "University of Minnesota": "United States",
    "University of New South Wales": "Australia",
    "University of Newcastle": "Australia",
    "University of North Carolina at Chapel Hill, The": "United States",
    "University of Nottingham": "United Kingdom",
    "University of Osaka": "Japan",
    "University of Oslo": "Norway",
    "University of Otago": "New Zealand",
    "University of Ottawa": "Canada",
    "University of Oxford": "United Kingdom",
    "University of Pennsylvania": "United States",
    "University of Pittsburgh": "United States",
    "University of Queensland, The": "Australia",
    "University of San Diego": "United States",
    "University of Sheffield, The": "United Kingdom",
    "University of Southampton": "United Kingdom",
    "University of Southern California": "United States",
    "University of St Andrews": "United Kingdom",
    "University of Stuttgart": "Germany",
    "University of Sydney, The": "Australia",
    "University of Technology of Troyes": "France",
    "University of Texas at Austin, The": "United States",
    "University of Tokyo, The": "Japan",
    "University of Toronto": "Canada",
    "University of Toronto (Mississauga)": "Canada",
    "University of Toronto (Scarborough)": "Canada",
    "University of Victoria": "Canada",
    "University of Virginia": "United States",
    "University of Warwick": "United Kingdom",
    "University of Washington": "United States",
    "University of Waterloo": "Canada",
    "University of Western Australia, The": "Australia",
    "University of Wisconsin-Madison": "United States",
    "University of York": "United Kingdom",
    "University of Zurich": "Switzerland",
    "Uppsala University": "Sweden",
    "Utrecht University": "Netherlands",
    "Vanderbilt University": "United States",
    "Vassar College": "United States",
    "Victoria University of Wellington": "New Zealand",
    "Vilnius University": "Lithuania",
    "WHU - Otto Beisheim School of Management": "Germany",
    "Warsaw University of Technology": "Poland",
    "Waseda University": "Japan",
    "Western University": "Canada",
    "William & Mary": "United States",
    "Yonsei University": "South Korea",
    "York University": "Canada",
    "Zhejiang University": "China",
}

REGION = {
    "Singapore": "Southeast Asia",
    "China": "East Asia", "Hong Kong": "East Asia", "Taiwan": "East Asia",
    "Japan": "East Asia", "South Korea": "East Asia",
    "Thailand": "Southeast Asia",
    "Australia": "Oceania", "New Zealand": "Oceania",
    "United States": "North America", "Canada": "North America", "Mexico": "North America",
    "United Kingdom": "Europe", "Ireland": "Europe", "Germany": "Europe", "France": "Europe",
    "Netherlands": "Europe", "Belgium": "Europe", "Switzerland": "Europe", "Sweden": "Europe",
    "Denmark": "Europe", "Norway": "Europe", "Finland": "Europe", "Iceland": "Europe",
    "Poland": "Europe", "Hungary": "Europe", "Estonia": "Europe", "Lithuania": "Europe",
    "Italy": "Europe", "Spain": "Europe", "Turkey": "Europe/Middle East", "Israel": "Europe/Middle East",
}


def clean(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    s = str(v).strip()
    return s or None


def clean_units(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    try:
        f = float(v)
        return int(f) if f.is_integer() else f
    except (TypeError, ValueError):
        return None


def main():
    tables = pd.read_html(SRC)
    df = tables[0]

    universities = {}
    order = []

    for _, row in df.iterrows():
        name = clean(row["Partner University"])
        if name is None:
            name = "(University not specified in source data)"

        if name not in universities:
            universities[name] = {
                "name": name,
                "country": COUNTRY.get(name, "Unknown"),
                "region": REGION.get(COUNTRY.get(name, ""), "Unknown"),
                "faculties": set(),
                "courses": [],
            }
            order.append(name)

        u = universities[name]
        faculty = clean(row["Faculty"])
        if faculty:
            u["faculties"].add(faculty)

        pu_courses = []
        for code_col, title_col, units_col in [
            ("PU Course 1", "PU Course 1 Title", "PU Crse1 Units"),
            ("PU Course 2", "PU Course 2 Title", "PU Crse2 Units"),
        ]:
            code = clean(row[code_col])
            if code:
                pu_courses.append({
                    "code": code,
                    "title": clean(row[title_col]),
                    "units": clean_units(row[units_col]),
                })

        nus_courses = []
        for code_col, title_col, units_col in [
            ("NUS Course 1", "NUS Course 1 Title", "NUS Crse1 Units"),
            ("NUS Course 2", "NUS Course 2 Title", "NUS Crse2 Units"),
        ]:
            code = clean(row[code_col])
            if code:
                nus_courses.append({
                    "code": code,
                    "title": clean(row[title_col]),
                    "units": clean_units(row[units_col]),
                })

        approved = clean(row["Pre Approved?"])
        approved_status = "yes" if approved == "Y" else ("no" if approved == "N" else "unspecified")

        u["courses"].append({
            "puCourses": pu_courses,
            "nusCourses": nus_courses,
            "approved": approved_status,
        })

    result = []
    for name in order:
        u = universities[name]
        approved_count = sum(1 for c in u["courses"] if c["approved"] == "yes")
        not_approved_count = sum(1 for c in u["courses"] if c["approved"] == "no")
        unspecified_count = sum(1 for c in u["courses"] if c["approved"] == "unspecified")
        result.append({
            "name": u["name"],
            "country": u["country"],
            "region": u["region"],
            "faculties": sorted(u["faculties"]),
            "totalMappings": len(u["courses"]),
            "approvedCount": approved_count,
            "notApprovedCount": not_approved_count,
            "unspecifiedCount": unspecified_count,
            "courses": u["courses"],
        })

    result.sort(key=lambda u: u["name"])

    meta = {
        "generatedFrom": str(SRC.name),
        "totalUniversities": len(result),
        "totalMappingRows": int(len(df)),
        "faculties": sorted({f for u in result for f in u["faculties"]}),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"meta": meta, "universities": result}, indent=1))
    print(f"Wrote {OUT} — {len(result)} universities, {len(df)} mapping rows")


if __name__ == "__main__":
    main()
