#!/usr/bin/env python3
"""Standalone script to load Torah people into Neo4j. No backend deps needed."""

from neo4j import GraphDatabase

URI = "bolt://localhost:7688"
USER = "neo4j"
PASSWORD = "torah-graph-secure"

PEOPLE = [
    {"ref": "adam", "name": "אדם הראשון", "name_en": "Adam", "role": "אדם ראשון", "period": "בריאה", "book": "בראשית", "hebrew_normalized": "אדם"},
    {"ref": "eve", "name": "חוה", "name_en": "Eve", "role": "אם כל חי", "period": "בריאה", "book": "בראשית", "hebrew_normalized": "חוה"},
    {"ref": "noah", "name": "נח", "name_en": "Noah", "role": "צדיק", "period": "דור המבול", "book": "בראשית", "hebrew_normalized": "נח"},
    {"ref": "abraham", "name": "אברהם אבינו", "name_en": "Abraham", "role": "אב האומה", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "אברהם"},
    {"ref": "sarah", "name": "שרה אמנו", "name_en": "Sarah", "role": "אם האומה", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "שרה"},
    {"ref": "isaac", "name": "יצחק אבינו", "name_en": "Isaac", "role": "אב", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "יצחק"},
    {"ref": "rebecca", "name": "רבקה אמנו", "name_en": "Rebecca", "role": "אם", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "רבקה"},
    {"ref": "jacob", "name": "יעקב אבינו", "name_en": "Jacob", "role": "אב", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "יעקב"},
    {"ref": "leah", "name": "לאה אמנו", "name_en": "Leah", "role": "אם", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "לאה"},
    {"ref": "rachel", "name": "רחל אמנו", "name_en": "Rachel", "role": "אם", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "רחל"},
    {"ref": "reuben", "name": "ראובן", "name_en": "Reuben", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "ראובן"},
    {"ref": "simeon", "name": "שמעון", "name_en": "Simeon", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "שמעון"},
    {"ref": "levi", "name": "לוי", "name_en": "Levi", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "לוי"},
    {"ref": "judah", "name": "יהודה", "name_en": "Judah", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "יהודה"},
    {"ref": "joseph", "name": "יוסף הצדיק", "name_en": "Joseph", "role": "שליט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "יוסף"},
    {"ref": "benjamin", "name": "בנימין", "name_en": "Benjamin", "role": "שבט", "period": "דור האבות", "book": "בראשית", "hebrew_normalized": "בנימין"},
    {"ref": "moshe", "name": "משה רבנו", "name_en": "Moses", "role": "נביא", "period": "יציאת מצרים", "book": "שמות", "hebrew_normalized": "משה"},
    {"ref": "aaron", "name": "אהרן הכהן", "name_en": "Aaron", "role": "כהן גדול", "period": "יציאת מצרים", "book": "שמות", "hebrew_normalized": "אהרן"},
    {"ref": "miriam", "name": "מרים הנביאה", "name_en": "Miriam", "role": "נביאה", "period": "יציאת מצרים", "book": "שמות", "hebrew_normalized": "מרים"},
    {"ref": "joshua", "name": "יהושע בן נון", "name_en": "Joshua", "role": "מנהיג", "period": "כיבוש הארץ", "book": "יהושע", "hebrew_normalized": "יהושע"},
    {"ref": "caleb", "name": "כלב בן יפונה", "name_en": "Caleb", "role": "מנהיג", "period": "כיבוש הארץ", "book": "יהושע", "hebrew_normalized": "כלב"},
    {"ref": "deborah", "name": "דבורה הנביאה", "name_en": "Deborah", "role": "נביאה", "period": "שופטים", "book": "שופטים", "hebrew_normalized": "דבורה"},
    {"ref": "gideon", "name": "גדעון בן יואש", "name_en": "Gideon", "role": "שופט", "period": "שופטים", "book": "שופטים", "hebrew_normalized": "גדעון"},
    {"ref": "samson", "name": "שמשון הגיבור", "name_en": "Samson", "role": "שופט", "period": "שופטים", "book": "שופטים", "hebrew_normalized": "שמשון"},
    {"ref": "samuel", "name": "שמואל הנביא", "name_en": "Samuel", "role": "נביא", "period": "שופטים", "book": "שמואל", "hebrew_normalized": "שמואל"},
    {"ref": "saul", "name": "שאול המלך", "name_en": "King Saul", "role": "מלך", "period": "מלכות שאול", "book": "שמואל", "hebrew_normalized": "שאול"},
    {"ref": "david", "name": "דוד המלך", "name_en": "King David", "role": "מלך", "period": "מלכות דוד", "book": "שמואל", "hebrew_normalized": "דוד"},
    {"ref": "solomon", "name": "שלמה המלך", "name_en": "King Solomon", "role": "מלך", "period": "מלכות דוד", "book": "מלכים", "hebrew_normalized": "שלמה"},
    {"ref": "elijah", "name": "אליהו הנביא", "name_en": "Elijah", "role": "נביא", "period": "מלכות ישראל", "book": "מלכים", "hebrew_normalized": "אליהו"},
    {"ref": "elisha", "name": "אלישע הנביא", "name_en": "Elisha", "role": "נביא", "period": "מלכות ישראל", "book": "מלכים", "hebrew_normalized": "אלישע"},
    {"ref": "isaiah", "name": "ישעיהו הנביא", "name_en": "Isaiah", "role": "נביא", "period": "מלכות יהודה", "book": "ישעיהו", "hebrew_normalized": "ישעיהו"},
    {"ref": "jeremiah", "name": "ירמיהו הנביא", "name_en": "Jeremiah", "role": "נביא", "period": "חורבן בית ראשון", "book": "ירמיהו", "hebrew_normalized": "ירמיהו"},
    {"ref": "ezekiel", "name": "יחזקאל הנביא", "name_en": "Ezekiel", "role": "נביא", "period": "חורבן בית ראשון", "book": "יחזקאל", "hebrew_normalized": "יחזקאל"},
    {"ref": "daniel", "name": "דניאל החכם", "name_en": "Daniel", "role": "חכם", "period": "גלות בבל", "book": "דניאל", "hebrew_normalized": "דניאל"},
    {"ref": "ezra", "name": "עזרא הסופר", "name_en": "Ezra", "role": "סופר", "period": "שיבת ציון", "book": "עזרא", "hebrew_normalized": "עזרא"},
    {"ref": "nehemiah", "name": "נחמיה המושל", "name_en": "Nehemiah", "role": "מושל", "period": "שיבת ציון", "book": "נחמיה", "hebrew_normalized": "נחמיה"},
    {"ref": "esther", "name": "אסתר המלכה", "name_en": "Queen Esther", "role": "מלכה", "period": "מלכות פרס", "book": "אסתר", "hebrew_normalized": "אסתר"},
    {"ref": "mordechai", "name": "מרדכי היהודי", "name_en": "Mordechai", "role": "מנהיג", "period": "מלכות פרס", "book": "אסתר", "hebrew_normalized": "מרדכי"},
    {"ref": "haman", "name": "המן", "name_en": "Haman", "role": "שר", "period": "מלכות פרס", "book": "אסתר", "hebrew_normalized": "המן"},
    {"ref": "job", "name": "איוב", "name_en": "Job", "role": "צדיק", "period": "דור האבות", "book": "איוב", "hebrew_normalized": "איוב"},
    {"ref": "ruth", "name": "רות המואביה", "name_en": "Ruth", "role": "גיורת", "period": "שופטים", "book": "רות", "hebrew_normalized": "רות"},
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

FAMILY = [
    ("abraham", "FATHER_OF", "isaac"),
    ("abraham", "HUSBAND_OF", "sarah"),
    ("isaac", "FATHER_OF", "jacob"),
    ("jacob", "FATHER_OF", "joseph"),
    ("jacob", "FATHER_OF", "reuben"),
    ("jacob", "FATHER_OF", "simeon"),
    ("jacob", "FATHER_OF", "levi"),
    ("jacob", "FATHER_OF", "judah"),
    ("jacob", "FATHER_OF", "benjamin"),
    ("jacob", "HUSBAND_OF", "leah"),
    ("jacob", "HUSBAND_OF", "rachel"),
    ("moshe", "BROTHER_OF", "aaron"),
    ("moshe", "BROTHER_OF", "miriam"),
    ("david", "FATHER_OF", "solomon"),
]


def main():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    with driver.session() as session:
        # Clear
        session.run("MATCH (p:Person) DETACH DELETE p")
        print("Cleared old people")

        # Create
        total = 0
        for i in range(0, len(PEOPLE), 20):
            batch = PEOPLE[i : i + 20]
            session.run("""
                UNWIND $people AS p
                CREATE (person:Person)
                SET person = p
                SET person.id = p.ref
            """, people=batch)
            total += len(batch)
            print(f"Loaded {total}/{len(PEOPLE)}")

        # MENTIONS
        print("Creating MENTIONS...")
        session.run("""
            MATCH (p:Person)
            WITH p, p.hebrew_normalized AS name
            WHERE size(name) > 2
            MATCH (v:Verse)
            WHERE v.hebrew_normalized CONTAINS name
            WITH p, v LIMIT 100000
            MERGE (v)-[:MENTIONS]->(p)
        """)
        print("MENTIONS done")

        # Family
        for f, rel, t in FAMILY:
            try:
                session.run(f"""
                    MATCH (a:Person {{ref: $f}}), (b:Person {{ref: $t}})
                    MERGE (a)-[:{rel}]->(b)
                """, f=f, t=t)
            except Exception as e:
                print(f"Family rel failed: {f}-{rel}-{t}: {e}")

        # Stats
        result = session.run("""
            CALL apoc.meta.stats() YIELD labels, relTypesCount
            RETURN labels, relTypesCount
        """)
        record = result.single()
        print(f"\nDone!")
        print(f"  People: {record['labels'].get('Person', 0)}")
        print(f"  Relationships: {record['relTypesCount']}")

    driver.close()


if __name__ == "__main__":
    main()
