#!/usr/bin/env python3
"""Load Torah people into Neo4j with MENTIONS relationships.

Usage:
    uv run python scripts/load_people_to_neo4j.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.neo4j_client import neo4j_client
import structlog

logger = structlog.get_logger()

# ── Torah People Data ───────────────────────────────────

PEOPLE = [
    {"ref": "adam", "name": "אדם הראשון", "name_en": "Adam", "role": "אדם ראשון", "period": "בריאה", "book": "בראשית", "hebrew_normalized": "אדם הראשון"},
    {"ref": "eve", "name": "חוה", "name_en": "Eve", "role": "אם כל חי", "period": "בריאה", "book": "בראשית", "hebrew_normalized": "חוה"},
    {"ref": "cain", "name": "קין", "name_en": "Cain", "role": "בן אדם", "period": "דור ראשון", "book": "בראשית", "hebrew_normalized": "קין"},
    {"ref": "abel", "name": "הבל", "name_en": "Abel", "role": "בן אדם", "period": "דור ראשון", "book": "בראשית", "hebrew_normalized": "הבל"},
    {"ref": "seth", "name": "שת", "name_en": "Seth", "role": "בן אדם", "period": "דור ראשון", "book": "בראשית", "hebrew_normalized": "שת"},
    {"ref": "enoch", "name": "חנוך", "name_en": "Enoch", "role": "צדיק", "period": "דור ראשון", "book": "בראשית", "hebrew_normalized": "חנוך"},
    {"ref": "methuselah", "name": "מתושלח", "name_en": "Methuselah", "role": "בן אדם", "period": "דור ראשון", "book": "בראשית", "hebrew_normalized": "מתושלח"},
    {"ref": "noah", "name": "נח", "name_en": "Noah", "role": "צדיק", "period": "דור המבול", "book": "בראשית", "hebrew_normalized": "נח"},
    {"ref": "terah", "name": "תרח", "name_en": "Terah", "role": "אב אברהם", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "תרח"},
    {"ref": "abraham", "name": "אברהם אבינו", "name_en": "Abraham", "role": "אב האומה", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "אברהם"},
    {"ref": "sarah", "name": "שרה אמנו", "name_en": "Sarah", "role": "אם האומה", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "שרה"},
    {"ref": "ishmael", "name": "ישמעאל", "name_en": "Ishmael", "role": "בן אברהם", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "ישמעאל"},
    {"ref": "isaac", "name": "יצחק אבינו", "name_en": "Isaac", "role": "אב", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "יצחק"},
    {"ref": "rebecca", "name": "רבקה אמנו", "name_en": "Rebecca", "role": "אם", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "רבקה"},
    {"ref": "esau", "name": "עשו", "name_en": "Esau", "role": "בן יצחק", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "עשו"},
    {"ref": "jacob", "name": "יעקב אבינו", "name_en": "Jacob", "role": "אב", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "יעקב"},
    {"ref": "leah", "name": "לאה אמנו", "name_en": "Leah", "role": "אם", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "לאה"},
    {"ref": "rachel", "name": "רחל אמנו", "name_en": "Rachel", "role": "אם", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "רחל"},
    {"ref": "reuben", "name": "ראובן", "name_en": "Reuben", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "ראובן"},
    {"ref": "simeon", "name": "שמעון", "name_en": "Simeon", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "שמעון"},
    {"ref": "levi", "name": "לוי", "name_en": "Levi", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "לוי"},
    {"ref": "judah", "name": "יהודה", "name_en": "Judah", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "יהודה"},
    {"ref": "issachar", "name": "יששכר", "name_en": "Issachar", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "יששכר"},
    {"ref": "zebulun", "name": "זבולון", "name_en": "Zebulun", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "זבולון"},
    {"ref": "dan", "name": "דן", "name_en": "Dan", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "דן"},
    {"ref": "naphtali", "name": "נפתלי", "name_en": "Naphtali", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "נפתלי"},
    {"ref": "gad", "name": "גד", "name_en": "Gad", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "גד"},
    {"ref": "asher", "name": "אשר", "name_en": "Asher", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "אשר"},
    {"ref": "joseph", "name": "יוסף הצדיק", "name_en": "Joseph", "role": "שליט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "יוסף"},
    {"ref": "benjamin", "name": "בנימין", "name_en": "Benjamin", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "בנימין"},
    {"ref": "ephraim", "name": "אפרים", "name_en": "Ephraim", "role": "בן יוסף", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "אפרים"},
    {"ref": "manasseh", "name": "מנשה", "name_en": "Manasseh", "role": "בן יוסף", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "מנשה"},
    {"ref": "tamar", "name": "תמר", "name_en": "Tamar", "role": "כלה", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "תמר"},
    {"ref": "potiphar", "name": "פוטיפר", "name_en": "Potiphar", "role": "שר", "period": "מצרים", "book": "בראשית", "hebrew_normalized": "פוטיפר"},
    {"ref": "pharaoh", "name": "פרעה", "name_en": "Pharaoh", "role": "מלך", "period": "מצרים", "book": "שמות", "hebrew_normalized": "פרעה"},
    {"ref": "amram", "name": "עמרם", "name_en": "Amram", "role": "אב משה", "period": "יציאת מצרים", "book": "שמות", "hebrew_normalized": "עמרם"},
    {"ref": "jochebed", "name": "יוכבד", "name_en": "Jochebed", "role": "אם משה", "period": "יציאת מצרים", "book": "שמות", "hebrew_normalized": "יוכבד"},
    {"ref": "moshe", "name": "משה רבנו", "name_en": "Moses", "role": "נביא", "period": "יציאת מצרים", "book": "שמות", "hebrew_normalized": "משה"},
    {"ref": "aaron", "name": "אהרן הכהן", "name_en": "Aaron", "role": "כהן גדול", "period": "יציאת מצרים", "book": "שמות", "hebrew_normalized": "אהרן"},
    {"ref": "miriam", "name": "מרים הנביאה", "name_en": "Miriam", "role": "נביאה", "period": "יציאת מצרים", "book": "שמות", "hebrew_normalized": "מרים"},
    {"ref": "jethro", "name": "יתרו", "name_en": "Jethro", "role": "כהן מדין", "period": "מדבר", "book": "שמות", "hebrew_normalized": "יתרו"},
    {"ref": "korah", "name": "קורח", "name_en": "Korah", "role": "לוי", "period": "מדבר", "book": "במדבר", "hebrew_normalized": "קורח"},
    {"ref": "balak", "name": "בלק", "name_en": "Balak", "role": "מלך", "period": "מדבר", "book": "במדבר", "hebrew_normalized": "בלק"},
    {"ref": "balaam", "name": "בלעם", "name_en": "Balaam", "role": "מכשף", "period": "מדבר", "book": "במדבר", "hebrew_normalized": "בלעם"},
    {"ref": "joshua", "name": "יהושע בן נון", "name_en": "Joshua", "role": "מנהיג", "period": "כיבוש הארץ", "book": "יהושע", "hebrew_normalized": "יהושע"},
    {"ref": "caleb", "name": "כלב בן יפונה", "name_en": "Caleb", "role": "מנהיג", "period": "כיבוש הארץ", "book": "יהושע", "hebrew_normalized": "כלב"},
    {"ref": "rahav", "name": "רחב", "name_en": "Rahab", "role": "זונה", "period": "כיבוש הארץ", "book": "יהושע", "hebrew_normalized": "רחב"},
    {"ref": "achan", "name": "עכן", "name_en": "Achan", "role": "חוטא", "period": "כיבוש הארץ", "book": "יהושע", "hebrew_normalized": "עכן"},
    {"ref": "og", "name": "עוג מלך הבשן", "name_en": "Og", "role": "מלך", "period": "כיבוש הארץ", "book": "יהושע", "hebrew_normalized": "עוג"},
    {"ref": "deborah", "name": "דבורה הנביאה", "name_en": "Deborah", "role": "נביאה", "period": "שופטים", "book": "שופטים", "hebrew_normalized": "דבורה"},
    {"ref": "barak", "name": "ברק", "name_en": "Barak", "role": "צבא", "period": "שופטים", "book": "שופטים", "hebrew_normalized": "ברק"},
    {"ref": "gideon", "name": "גדעון בן יואש", "name_en": "Gideon", "role": "שופט", "period": "שופטים", "book": "שופטים", "hebrew_normalized": "גדעון"},
    {"ref": "samson", "name": "שמשון הגיבור", "name_en": "Samson", "role": "שופט", "period": "שופטים", "book": "שופטים", "hebrew_normalized": "שמשון"},
    {"ref": "jephthah", "name": "יפתח", "name_en": "Jephthah", "role": "שופט", "period": "שופטים", "book": "שופטים", "hebrew_normalized": "יפתח"},
    {"ref": "samuel", "name": "שמואל הנביא", "name_en": "Samuel", "role": "נביא", "period": "שופטים", "book": "שמואל", "hebrew_normalized": "שמואל"},
    {"ref": "eli", "name": "עלי הכהן", "name_en": "Eli", "role": "כהן גדול", "period": "שופטים", "book": "שמואל", "hebrew_normalized": "עלי"},
    {"ref": "hannah", "name": "חנה", "name_en": "Hannah", "role": "אם שמואל", "period": "שופטים", "book": "שמואל", "hebrew_normalized": "חנה"},
    {"ref": "saul", "name": "שאול המלך", "name_en": "King Saul", "role": "מלך", "period": "מלכות שאול", "book": "שמואל", "hebrew_normalized": "שאול"},
    {"ref": "jonathan", "name": "יהונתן", "name_en": "Jonathan", "role": "שר", "period": "מלכות שאול", "book": "שמואל", "hebrew_normalized": "יהונתן"},
    {"ref": "abner", "name": "אבנר", "name_en": "Abner", "role": "שר", "period": "מלכות שאול", "book": "שמואל", "hebrew_normalized": "אבנר"},
    {"ref": "goliath", "name": "גוליית", "name_en": "Goliath", "role": "לוחם", "period": "מלכות שאול", "book": "שמואל", "hebrew_normalized": "גוליית"},
    {"ref": "david", "name": "דוד המלך", "name_en": "King David", "role": "מלך", "period": "מלכות דוד", "book": "שמואל", "hebrew_normalized": "דוד"},
    {"ref": "joab", "name": "יואב", "name_en": "Joab", "role": "צבא", "period": "מלכות דוד", "book": "שמואל", "hebrew_normalized": "יואב"},
    {"ref": "absalom", "name": "אבשלום", "name_en": "Absalom", "role": "בן מלך", "period": "מלכות דוד", "book": "שמואל", "hebrew_normalized": "אבשלום"},
    {"ref": "bathsheba", "name": "בת שבע", "name_en": "Bathsheba", "role": "מלכה", "period": "מלכות דוד", "book": "שמואל", "hebrew_normalized": "בת שבע"},
    {"ref": "nathan", "name": "נתן הנביא", "name_en": "Nathan", "role": "נביא", "period": "מלכות דוד", "book": "שמואל", "hebrew_normalized": "נתן"},
    {"ref": "uriah", "name": "אוריה החתי", "name_en": "Uriah", "role": "חייל", "period": "מלכות דוד", "book": "שמואל", "hebrew_normalized": "אוריה"},
    {"ref": "solomon", "name": "שלמה המלך", "name_en": "King Solomon", "role": "מלך", "period": "מלכות דוד", "book": "מלכים", "hebrew_normalized": "שלמה"},
    {"ref": "adonijah", "name": "אדניה", "name_en": "Adonijah", "role": "בן דוד", "period": "מלכות דוד", "book": "מלכים", "hebrew_normalized": "אדניה"},
    {"ref": "rehoboam", "name": "רחבעם", "name_en": "Rehoboam", "role": "מלך", "period": "מלכות דוד", "book": "מלכים", "hebrew_normalized": "רחבעם"},
    {"ref": "jeroboam", "name": "ירבעם", "name_en": "Jeroboam", "role": "מלך", "period": "מלכות ישראל", "book": "מלכים", "hebrew_normalized": "ירבעם"},
    {"ref": "ahab", "name": "אחאב המלך", "name_en": "Ahab", "role": "מלך", "period": "מלכות ישראל", "book": "מלכים", "hebrew_normalized": "אחאב"},
    {"ref": "jezebel", "name": "איזבל", "name_en": "Jezebel", "role": "מלכה", "period": "מלכות ישראל", "book": "מלכים", "hebrew_normalized": "איזבל"},
    {"ref": "elijah", "name": "אליהו הנביא", "name_en": "Elijah", "role": "נביא", "period": "מלכות ישראל", "book": "מלכים", "hebrew_normalized": "אליהו"},
    {"ref": "elisha", "name": "אלישע הנביא", "name_en": "Elisha", "role": "נביא", "period": "מלכות ישראל", "book": "מלכים", "hebrew_normalized": "אלישע"},
    {"ref": "jehu", "name": "יהוא", "name_en": "Jehu", "role": "מלך", "period": "מלכות ישראל", "book": "מלכים", "hebrew_normalized": "יהוא"},
    {"ref": "hezekiah", "name": "חזקיהו המלך", "name_en": "Hezekiah", "role": "מלך", "period": "מלכות יהודה", "book": "מלכים", "hebrew_normalized": "חזקיהו"},
    {"ref": "josiah", "name": "יאשיהו המלך", "name_en": "Josiah", "role": "מלך", "period": "מלכות יהודה", "book": "מלכים", "hebrew_normalized": "יאשיהו"},
    {"ref": "isaiah", "name": "ישעיהו הנביא", "name_en": "Isaiah", "role": "נביא", "period": "מלכות יהודה", "book": "ישעיהו", "hebrew_normalized": "ישעיהו"},
    {"ref": "jeremiah", "name": "ירמיהו הנביא", "name_en": "Jeremiah", "role": "נביא", "period": "חורבן בית ראשון", "book": "ירמיהו", "hebrew_normalized": "ירמיהו"},
    {"ref": "ezekiel", "name": "יחזקאל הנביא", "name_en": "Ezekiel", "role": "נביא", "period": "חורבן בית ראשון", "book": "יחזקאל", "hebrew_normalized": "יחזקאל"},
    {"ref": "daniel", "name": "דניאל החכם", "name_en": "Daniel", "role": "חכם", "period": "גלות בבל", "book": "דניאל", "hebrew_normalized": "דניאל"},
    {"ref": "nebuchadnezzar", "name": "נבוכדנצר", "name_en": "Nebuchadnezzar", "role": "מלך", "period": "גלות בבל", "book": "דניאל", "hebrew_normalized": "נבוכדנצר"},
    {"ref": "ezra", "name": "עזרא הסופר", "name_en": "Ezra", "role": "סופר", "period": "שיבת ציון", "book": "עזרא", "hebrew_normalized": "עזרא"},
    {"ref": "nehemiah", "name": "נחמיה המושל", "name_en": "Nehemiah", "role": "מושל", "period": "שיבת ציון", "book": "נחמיה", "hebrew_normalized": "נחמיה"},
    {"ref": "esther", "name": "אסתר המלכה", "name_en": "Queen Esther", "role": "מלכה", "period": "מלכות פרס", "book": "אסתר", "hebrew_normalized": "אסתר"},
    {"ref": "mordechai", "name": "מרדכי היהודי", "name_en": "Mordechai", "role": "מנהיג", "period": "מלכות פרס", "book": "אסתר", "hebrew_normalized": "מרדכי"},
    {"ref": "haman", "name": "המן", "name_en": "Haman", "role": "שר", "period": "מלכות פרס", "book": "אסתר", "hebrew_normalized": "המן"},
    {"ref": "job", "name": "איוב", "name_en": "Job", "role": "צדיק", "period": "דור האבות", "book": "איוב", "hebrew_normalized": "איוב"},
    {"ref": "ruth", "name": "רות המואביה", "name_en": "Ruth", "role": "גיורת", "period": "שופטים", "book": "רות", "hebrew_normalized": "רות"},
    {"ref": "naomi", "name": "נעמי", "name_en": "Naomi", "role": "אם", "period": "שופטים", "book": "רות", "hebrew_normalized": "נעמי"},
    {"ref": "boaz", "name": "בעז", "name_en": "Boaz", "role": "שופט", "period": "שופטים", "book": "רות", "hebrew_normalized": "בעז"},
    {"ref": "jonah", "name": "יונה הנביא", "name_en": "Jonah", "role": "נביא", "period": "מלכות ישראל", "book": "יונה", "hebrew_normalized": "יונה"},
    {"ref": "amos", "name": "עמוס הנביא", "name_en": "Amos", "role": "נביא", "period": "מלכות ישראל", "book": "עמוס", "hebrew_normalized": "עמוס"},
    {"ref": "hosea", "name": "הושע הנביא", "name_en": "Hosea", "role": "נביא", "period": "מלכות ישראל", "book": "הושע", "hebrew_normalized": "הושע"},
    {"ref": "micha", "name": "מיכה הנביא", "name_en": "Micah", "role": "נביא", "period": "מלכות יהודה", "book": "מיכה", "hebrew_normalized": "מיכה"},
    {"ref": "habakkuk", "name": "חבקוק הנביא", "name_en": "Habakkuk", "role": "נביא", "period": "מלכות יהודה", "book": "חבקוק", "hebrew_normalized": "חבקוק"},
    {"ref": "zephaniah", "name": "צפניה הנביא", "name_en": "Zephaniah", "role": "נביא", "period": "מלכות יהודה", "book": "צפניה", "hebrew_normalized": "צפניה"},
    {"ref": "haggai", "name": "חגי הנביא", "name_en": "Haggai", "role": "נביא", "period": "שיבת ציון", "book": "חגי", "hebrew_normalized": "חגי"},
    {"ref": "zechariah", "name": "זכריה הנביא", "name_en": "Zechariah", "role": "נביא", "period": "שיבת ציון", "book": "זכריה", "hebrew_normalized": "זכריה"},
    {"ref": "malachi", "name": "מלאכי הנביא", "name_en": "Malachi", "role": "נביא", "period": "שיבת ציון", "book": "מלאכי", "hebrew_normalized": "מלאכי"},
]

# ── Family relationships ──────────────────────────────────

FAMILY_RELS = [
    ("abraham", "FATHER_OF", "isaac"),
    ("abraham", "HUSBAND_OF", "sarah"),
    ("isaac", "FATHER_OF", "jacob"),
    ("isaac", "FATHER_OF", "esau"),
    ("jacob", "FATHER_OF", "joseph"),
    ("jacob", "FATHER_OF", "reuben"),
    ("jacob", "FATHER_OF", "simeon"),
    ("jacob", "FATHER_OF", "levi"),
    ("jacob", "FATHER_OF", "judah"),
    ("jacob", "FATHER_OF", "issachar"),
    ("jacob", "FATHER_OF", "zebulun"),
    ("jacob", "FATHER_OF", "dan"),
    ("jacob", "FATHER_OF", "naphtali"),
    ("jacob", "FATHER_OF", "gad"),
    ("jacob", "FATHER_OF", "asher"),
    ("jacob", "FATHER_OF", "benjamin"),
    ("jacob", "HUSBAND_OF", "leah"),
    ("jacob", "HUSBAND_OF", "rachel"),
    ("joseph", "FATHER_OF", "ephraim"),
    ("joseph", "FATHER_OF", "manasseh"),
    ("moshe", "BROTHER_OF", "aaron"),
    ("moshe", "BROTHER_OF", "miriam"),
    ("amram", "FATHER_OF", "moshe"),
    ("jochebed", "MOTHER_OF", "moshe"),
    ("david", "FATHER_OF", "solomon"),
    ("david", "FATHER_OF", "absalom"),
    ("elkanah", "FATHER_OF", "samuel"),
    ("hannah", "MOTHER_OF", "samuel"),
]


def main():
    logger.info("loading_torah_people", count=len(PEOPLE))

    # 1. Clear old Person data
    neo4j_client.driver.execute_query("MATCH (p:Person) DETACH DELETE p")
    logger.info("cleared_old_people")

    # 2. Create Person nodes in batches
    BATCH_SIZE = 50
    total = 0
    for i in range(0, len(PEOPLE), BATCH_SIZE):
        batch = PEOPLE[i : i + BATCH_SIZE]
        cypher = """
        UNWIND $people AS p
        CREATE (person:Person)
        SET person = p
        SET person.id = p.ref
        """
        neo4j_client.driver.execute_query(cypher, people=batch)
        total += len(batch)
        logger.info("people_batch_loaded", loaded=total, total=len(PEOPLE))

    # 3. Create MENTIONS relationships (Person name appears in verse text)
    logger.info("creating_mentions_relationships")
    mention_cypher = """
    MATCH (p:Person)
    WITH p, p.hebrew_normalized AS name
    WHERE size(name) > 2
    MATCH (v:Verse)
    WHERE v.hebrew_normalized CONTAINS name
    WITH p, v
    LIMIT 100000
    MERGE (v)-[:MENTIONS]->(p)
    """
    neo4j_client.driver.execute_query(mention_cypher)
    logger.info("mentions_created")

    # 4. Create family relationships
    logger.info("creating_family_relationships", count=len(FAMILY_RELS))
    for from_ref, rel_type, to_ref in FAMILY_RELS:
        try:
            neo4j_client.driver.execute_query(
                f"""
                MATCH (a:Person {{ref: $from_ref}}), (b:Person {{ref: $to_ref}})
                MERGE (a)-[:{rel_type}]->(b)
                """,
                from_ref=from_ref,
                to_ref=to_ref,
            )
        except Exception as e:
            logger.warning("family_rel_failed", from_ref=from_ref, to_ref=to_ref, error=str(e))

    # 5. Stats
    stats, _, _ = neo4j_client.driver.execute_query(
        """
        CALL apoc.meta.stats() YIELD labels, relTypesCount
        RETURN labels, relTypesCount
        """
    )
    if stats:
        logger.info(
            "people_load_complete",
            labels=stats[0]["labels"],
            relationships=stats[0]["relTypesCount"],
        )
        print(f"\nDone!")
        print(f"  People: {stats[0]['labels'].get('Person', 0)}")
        print(f"  Relationships: {stats[0]['relTypesCount']}")


if __name__ == "__main__":
    main()
