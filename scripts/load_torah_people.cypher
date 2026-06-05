// Torah People Nodes + Relationships
// Run via: cypher-shell -u neo4j -p torah-graph-secure --file load_torah_people.cypher

CREATE CONSTRAINT person_ref IF NOT EXISTS FOR (p:Person) REQUIRE p.ref IS UNIQUE;

// ── CREATE PEOPLE ─────────────────────────────────────────

UNWIND [
  {ref: "moshe", name: "משה רבנו", name_en: "Moses", role: "נביא", period: "יציאת מצרים", book: "שמות", birth: null, death: null, hebrew_normalized: "משה רבנו"},
  {ref: "abraham", name: "אברהם אבינו", name_en: "Abraham", role: "אב האומה", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "אברהם אבינו"},
  {ref: "isaac", name: "יצחק אבינו", name_en: "Isaac", role: "אב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "יצחק אבינו"},
  {ref: "jacob", name: "יעקב אבינו", name_en: "Jacob", role: "אב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "יעקב אבינו"},
  {ref: "joseph", name: "יוסף הצדיק", name_en: "Joseph", role: "שליט", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "יוסף הצדיק"},
  {ref: "aaron", name: "אהרן הכהן", name_en: "Aaron", role: "כהן גדול", period: "יציאת מצרים", book: "שמות", birth: null, death: null, hebrew_normalized: "אהרן הכהן"},
  {ref: "miriam", name: "מרים הנביאה", name_en: "Miriam", role: "נביאה", period: "יציאת מצרים", book: "שמות", birth: null, death: null, hebrew_normalized: "מרים הנביאה"},
  {ref: "joshua", name: "יהושע בן נון", name_en: "Joshua", role: "מנהיג", period: "כיבוש הארץ", book: "יהושע", birth: null, death: null, hebrew_normalized: "יהושע בן נון"},
  {ref: "caleb", name: "כלב בן יפונה", name_en: "Caleb", role: "מנהיג", period: "כיבוש הארץ", book: "יהושע", birth: null, death: null, hebrew_normalized: "כלב בן יפונה"},
  {ref: "deborah", name: "דבורה הנביאה", name_en: "Deborah", role: "נביאה", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "דבורה הנביאה"},
  {ref: "gideon", name: "גדעון בן יואש", name_en: "Gideon", role: "שופט", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "גדעון בן יואש"},
  {ref: "samson", name: "שמשון הגיבור", name_en: "Samson", role: "שופט", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "שמשון הגיבור"},
  {ref: "samuel", name: "שמואל הנביא", name_en: "Samuel", role: "נביא", period: "שופטים", book: "שמואל", birth: null, death: null, hebrew_normalized: "שמואל הנביא"},
  {ref: "saul", name: "שאול המלך", name_en: "King Saul", role: "מלך", period: "מלכות שאול", book: "שמואל", birth: null, death: null, hebrew_normalized: "שאול המלך"},
  {ref: "david", name: "דוד המלך", name_en: "King David", role: "מלך", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "דוד המלך"},
  {ref: "solomon", name: "שלמה המלך", name_en: "King Solomon", role: "מלך", period: "מלכות דוד", book: "מלכים", birth: null, death: null, hebrew_normalized: "שלמה המלך"},
  {ref: "elijah", name: "אליהו הנביא", name_en: "Elijah", role: "נביא", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "אליהו הנביא"},
  {ref: "elisha", name: "אלישע הנביא", name_en: "Elisha", role: "נביא", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "אלישע הנביא"},
  {ref: "isaiah", name: "ישעיהו הנביא", name_en: "Isaiah", role: "נביא", period: "מלכות יהודה", book: "ישעיהו", birth: null, death: null, hebrew_normalized: "ישעיהו הנביא"},
  {ref: "jeremiah", name: "ירמיהו הנביא", name_en: "Jeremiah", role: "נביא", period: "חורבן בית ראשון", book: "ירמיהו", birth: null, death: null, hebrew_normalized: "ירמיהו הנביא"},
  {ref: "ezekiel", name: "יחזקאל הנביא", name_en: "Ezekiel", role: "נביא", period: "חורבן בית ראשון", book: "יחזקאל", birth: null, death: null, hebrew_normalized: "יחזקאל הנביא"},
  {ref: "daniel", name: "דניאל החכם", name_en: "Daniel", role: "חכם", period: "גלות בבל", book: "דניאל", birth: null, death: null, hebrew_normalized: "דניאל החכם"},
  {ref: "ezra", name: "עזרא הסופר", name_en: "Ezra", role: "סופר", period: "שיבת ציון", book: "עזרא", birth: null, death: null, hebrew_normalized: "עזרא הסופר"},
  {ref: "nehemiah", name: "נחמיה המושל", name_en: "Nehemiah", role: "מושל", period: "שיבת ציון", book: "נחמיה", birth: null, death: null, hebrew_normalized: "נחמיה המושל"},
  {ref: "esther", name: "אסתר המלכה", name_en: "Queen Esther", role: "מלכה", period: "מלכות פרס", book: "אסתר", birth: null, death: null, hebrew_normalized: "אסתר המלכה"},
  {ref: "mordechai", name: "מרדכי היהודי", name_en: "Mordechai", role: "מנהיג", period: "מלכות פרס", book: "אסתר", birth: null, death: null, hebrew_normalized: "מרדכי היהודי"},
  {ref: "ruth", name: "רות המואביה", name_en: "Ruth", role: "גיורת", period: "שופטים", book: "רות", birth: null, death: null, hebrew_normalized: "רות המואביה"},
  {ref: "boaz", name: "בעז", name_en: "Boaz", role: "שופט", period: "שופטים", book: "רות", birth: null, death: null, hebrew_normalized: "בעז"},
  {ref: "job", name: "איוב", name_en: "Job", role: "צדיק", period: "דור האבות", book: "איוב", birth: null, death: null, hebrew_normalized: "איוב"},
  {ref: "jonah", name: "יונה הנביא", name_en: "Jonah", role: "נביא", period: "מלכות ישראל", book: "יונה", birth: null, death: null, hebrew_normalized: "יונה הנביא"},
  {ref: "amos", name: "עמוס הנביא", name_en: "Amos", role: "נביא", period: "מלכות ישראל", book: "עמוס", birth: null, death: null, hebrew_normalized: "עמוס הנביא"},
  {ref: "hosea", name: "הושע הנביא", name_en: "Hosea", role: "נביא", period: "מלכות ישראל", book: "הושע", birth: null, death: null, hebrew_normalized: "הושע הנביא"},
  {ref: "micha", name: "מיכה הנביא", name_en: "Micah", role: "נביא", period: "מלכות יהודה", book: "מיכה", birth: null, death: null, hebrew_normalized: "מיכה הנביא"},
  {ref: "habakkuk", name: "חבקוק הנביא", name_en: "Habakkuk", role: "נביא", period: "מלכות יהודה", book: "חבקוק", birth: null, death: null, hebrew_normalized: "חבקוק הנביא"},
  {ref: "zephaniah", name: "צפניה הנביא", name_en: "Zephaniah", role: "נביא", period: "מלכות יהודה", book: "צפניה", birth: null, death: null, hebrew_normalized: "צפניה הנביא"},
  {ref: "haggai", name: "חגי הנביא", name_en: "Haggai", role: "נביא", period: "שיבת ציון", book: "חגי", birth: null, death: null, hebrew_normalized: "חגי הנביא"},
  {ref: "zechariah", name: "זכריה הנביא", name_en: "Zechariah", role: "נביא", period: "שיבת ציון", book: "זכריה", birth: null, death: null, hebrew_normalized: "זכריה הנביא"},
  {ref: "malachi", name: "מלאכי הנביא", name_en: "Malachi", role: "נביא", period: "שיבת ציון", book: "מלאכי", birth: null, death: null, hebrew_normalized: "מלאכי הנביא"},
  {ref: "noah", name: "נח", name_en: "Noah", role: "צדיק", period: "דור המבול", book: "בראשית", birth: null, death: null, hebrew_normalized: "נח"},
  {ref: "adam", name: "אדם הראשון", name_en: "Adam", role: "אדם ראשון", period: "בריאה", book: "בראשית", birth: null, death: null, hebrew_normalized: "אדם הראשון"},
  {ref: "eve", name: "חוה", name_en: "Eve", role: "אם כל חי", period: "בריאה", book: "בראשית", birth: null, death: null, hebrew_normalized: "חוה"},
  {ref: "cain", name: "קין", name_en: "Cain", role: "בן אדם", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "קין"},
  {ref: "abel", name: "הבל", name_en: "Abel", role: "בן אדם", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "הבל"},
  {ref: "seth", name: "שת", name_en: "Seth", role: "בן אדם", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "שת"},
  {ref: "enoch", name: "חנוך", name_en: "Enoch", role: "צדיק", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "חנוך"},
  {ref: "methuselah", name: "מתושלח", name_en: "Methuselah", role: "בן אדם", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "מתושלח"},
  {ref: "terah", name: "תרח", name_en: "Terah", role: "אב אברהם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "תרח"},
  {ref: "sarah", name: "שרה אמנו", name_en: "Sarah", role: "אם האומה", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "שרה אמנו"},
  {ref: "rebekah", name: "רבקה אמנו", name_en: "Rebekah", role: "אם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "רבקה אמנו"},
  {ref: "leah", name: "לאה אמנו", name_en: "Leah", role: "אם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "לאה אמנו"},
  {ref: "rachel", name: "רחל אמנו", name_en: "Rachel", role: "אם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "רחל אמנו"},
  {ref: "rebekah2", name: "רבקה", name_en: "Rebekah", role: "אם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "רבקה"},
  {ref: "esau", name: "עשו", name_en: "Esau", role: "בן יצחק", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "עשו"},
  {ref: "judah", name: "יהודה", name_en: "Judah", role: "שבט", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "יהודה"},
  {ref: "levi", name: "לוי", name_en: "Levi", role: "שבט", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "לוי"},
  {ref: "benjamin", name: "בנימין", name_en: "Benjamin", role: "שבט", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "בנימין"},
  {ref: "reuven", name: "ראובן", name_en: "Reuben", role: "שבט", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "ראובן"},
  {ref: "shimom", name: "שמעון", name_en: "Simeon", role: "שבט", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "שמעון"},
  {ref: "dan", name: "דן", name_en: "Dan", role: "שבט", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "דן"},
  {ref: "naphtali", name: "נפתלי", name_en: "Naphtali", role: "שבט", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "נפתלי"},
  {ref: "gad", name: "גד", name_en: "Gad", role: "שבט", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "גד"},
  {ref: "asher", name: "אשר", name_en: "Asher", role: "שבט", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "אשר"},
  {ref: "issachar", name: "יששכר", name_en: "Issachar", role: "שבט", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "יששכר"},
  {ref: "zevulun", name: "זבולון", name_en: "Zebulun", role: "שבט", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "זבולון"},
  {ref: "joseph2", name: "יוסף", name_en: "Joseph", role: "שבט", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "יוסף"},
  {ref: "potiphar", name: "פוטיפר", name_en: "Potiphar", role: "שר", period: "מצרים", book: "בראשית", birth: null, death: null, hebrew_normalized: "פוטיפר"},
  {ref: "pharaoh", name: "פרעה", name_en: "Pharaoh", role: "מלך", period: "מצרים", book: "שמות", birth: null, death: null, hebrew_normalized: "פרעה"},
  {ref: "jethro", name: "יתרו", name_en: "Jethro", role: "כהן מדין", period: "מדבר", book: "שמות", birth: null, death: null, hebrew_normalized: "יתרו"},
  {ref: "balak", name: "בלק", name_en: "Balak", role: "מלך", period: "מדבר", book: "במדבר", birth: null, death: null, hebrew_normalized: "בלק"},
  {ref: "balaam", name: "בלעם", name_en: "Balaam", role: "מכשף", period: "מדבר", book: "במדבר", birth: null, death: null, hebrew_normalized: "בלעם"},
  {ref: "deborah2", name: "דבורה", name_en: "Deborah", role: "נביאה", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "דבורה"},
  {ref: "barak", name: "ברק", name_en: "Barak", role: "צבא", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "ברק"},
  {ref: "goliath", name: "גוליית", name_en: "Goliath", role: "לוחם", period: "מלכות שאול", book: "שמואל", birth: null, death: null, hebrew_normalized: "גוליית"},
  {ref: "jonathan", name: "יהונתן", name_en: "Jonathan", role: "שר", period: "מלכות שאול", book: "שמואל", birth: null, death: null, hebrew_normalized: "יהונתן"},
  {ref: "abner", name: "אבנר", name_en: "Abner", role: "שר", period: "מלכות שאול", book: "שמואל", birth: null, death: null, hebrew_normalized: "אבנר"},
  {ref: "joab", name: "יואב", name_en: "Joab", role: "צבא", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "יואב"},
  {ref: "absalom", name: "אבשלום", name_en: "Absalom", role: "בן מלך", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "אבשלום"},
  {ref: "bathsheba", name: "בת שבע", name_en: "Bathsheba", role: "מלכה", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "בת שבע"},
  {ref: "nathan", name: "נתן הנביא", name_en: "Nathan", role: "נביא", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "נתן הנביא"},
  {ref: "uriah", name: "אוריה החתי", name_en: "Uriah", role: "חייל", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "אוריה החתי"},
  {ref: "ahab", name: "אחאב המלך", name_en: "Ahab", role: "מלך", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "אחאב המלך"},
  {ref: "jezebel", name: "איזבל", name_en: "Jezebel", role: "מלכה", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "איזבל"},
  {ref: "obadiah", name: "עובדיהו", name_en: "Obadiah", role: "שר", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "עובדיהו"},
  {ref: "ahab2", name: "אחאב", name_en: "Ahab", role: "נביא", period: "מלכות יהודה", book: "דברי הימים", birth: null, death: null, hebrew_normalized: "אחאב"},
  {ref: "hezekiah", name: "חזקיהו המלך", name_en: "Hezekiah", role: "מלך", period: "מלכות יהודה", book: "מלכים", birth: null, death: null, hebrew_normalized: "חזקיהו המלך"},
  {ref: "josiah", name: "יאשיהו המלך", name_en: "Josiah", role: "מלך", period: "מלכות יהודה", book: "מלכים", birth: null, death: null, hebrew_normalized: "יאשיהו המלך"},
  {ref: "jehoiakim", name: "יהויכין", name_en: "Jehoiakim", role: "מלך", period: "מלכות יהודה", book: "מלכים", birth: null, death: null, hebrew_normalized: "יהויכין"},
  {ref: "zerubbabel", name: "זרובבל", name_en: "Zerubbabel", role: "מנהיג", period: "שיבת ציון", book: "עזרא", birth: null, death: null, hebrew_normalized: "זרובבל"},
  {ref: "haman", name: "המן", name_en: "Haman", role: "שר", period: "מלכות פרס", book: "אסתר", birth: null, death: null, hebrew_normalized: "המן"},
  {ref: "vashti", name: "ושתי", name_en: "Vashti", role: "מלכה", period: "מלכות פרס", book: "אסתר", birth: null, death: null, hebrew_normalized: "ושתי"},
  {ref: "naomi", name: "נעמי", name_en: "Naomi", role: "אם", period: "שופטים", book: "רות", birth: null, death: null, hebrew_normalized: "נעמי"},
  {ref: "orpa", name: "ערפה", name_en: "Orpah", role: "כלה", period: "שופטים", book: "רות", birth: null, death: null, hebrew_normalized: "ערפה"},
  {ref: "obed", name: "עובד", name_en: "Obed", role: "בן", period: "שופטים", book: "רות", birth: null, death: null, hebrew_normalized: "עובד"},
  {ref: "abraham2", name: "אברם", name_en: "Abram", role: "אב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "אברם"},
  {ref: "ishmael", name: "ישמעאל", name_en: "Ishmael", role: "בן אברהם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "ישמעאל"},
  {ref: "isaac2", name: "יצחק", name_en: "Isaac", role: "בן אברהם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "יצחק"},
  {ref: "rebecca", name: "רבקה", name_en: "Rebecca", role: "אם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "רבקה"},
  {ref: "laban", name: "לבן", name_en: "Laban", role: "דוד", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "לבן"},
  {ref: "esau2", name: "עשו", name_en: "Esau", role: "בן יצחק", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "עשו"},
  {ref: "jacob2", name: "יעקב", name_en: "Jacob", role: "בן יצחק", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "יעקב"},
  {ref: "dinah", name: "דינה", name_en: "Dinah", role: "בת יעקב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "דינה"},
  {ref: "shechem", name: "שכם", name_en: "Shechem", role: "נסיך", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "שכם"},
  {ref: "reuben2", name: "ראובן", name_en: "Reuben", role: "בן יעקב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "ראובן"},
  {ref: "simeon", name: "שמעון", name_en: "Simeon", role: "בן יעקב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "שמעון"},
  {ref: "levi2", name: "לוי", name_en: "Levi", role: "בן יעקב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "לוי"},
  {ref: "judah2", name: "יהודה", name_en: "Judah", role: "בן יעקב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "יהודה"},
  {ref: "issachar2", name: "יששכר", name_en: "Issachar", role: "בן יעקב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "יששכר"},
  {ref: "zebulun", name: "זבולון", name_en: "Zebulun", role: "בן יעקב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "זבולון"},
  {ref: "dan2", name: "דן", name_en: "Dan", role: "בן יעקב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "דן"},
  {ref: "naphtali2", name: "נפתלי", name_en: "Naphtali", role: "בן יעקב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "נפתלי"},
  {ref: "gad2", name: "גד", name_en: "Gad", role: "בן יעקב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "גד"},
  {ref: "asher2", name: "אשר", name_en: "Asher", role: "בן יעקב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "אשר"},
  {ref: "joseph3", name: "יוסף", name_en: "Joseph", role: "בן יעקב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "יוסף"},
  {ref: "benjamin2", name: "בנימין", name_en: "Benjamin", role: "בן יעקב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "בנימין"},
  {ref: "tamar", name: "תמר", name_en: "Tamar", role: "כלה", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "תמר"},
  {ref: "pharez", name: "פרץ", name_en: "Perez", role: "בן", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "פרץ"},
  {ref: "zarah", name: "זרח", name_en: "Zerah", role: "בן", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "זרח"},
  {ref: "ephraim", name: "אפרים", name_en: "Ephraim", role: "בן יוסף", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "אפרים"},
  {ref: "manasseh", name: "מנשה", name_en: "Manasseh", role: "בן יוסף", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "מנשה"},
  {ref: "amram", name: "עמרם", name_en: "Amram", role: "אב משה", period: "יציאת מצרים", book: "שמות", birth: null, death: null, hebrew_normalized: "עמרם"},
  {ref: "jochebed", name: "יוכבד", name_en: "Jochebed", role: "אם משה", period: "יציאת מצרים", book: "שמות", birth: null, death: null, hebrew_normalized: "יוכבד"},
  {ref: "nadab", name: "נדב", name_en: "Nadab", role: "בן אהרן", period: "מדבר", book: "ויקרא", birth: null, death: null, hebrew_normalized: "נדב"},
  {ref: "abihu", name: "אביהוא", name_en: "Abihu", role: "בן אהרן", period: "מדבר", book: "ויקרא", birth: null, death: null, hebrew_normalized: "אביהוא"},
  {ref: "eleazar", name: "אלעזר", name_en: "Eleazar", role: "כהן גדול", period: "מדבר", book: "במדבר", birth: null, death: null, hebrew_normalized: "אלעזר"},
  {ref: "ithamar", name: "איתמר", name_en: "Ithamar", role: "כהן", period: "מדבר", book: "במדבר", birth: null, death: null, hebrew_normalized: "איתמר"},
  {ref: "korah", name: "קורח", name_en: "Korah", role: "לוי", period: "מדבר", book: "במדבר", birth: null, death: null, hebrew_normalized: "קורח"},
  {ref: "dathan", name: "דתן", name_en: "Dathan", role: "מרד", period: "מדבר", book: "במדבר", birth: null, death: null, hebrew_normalized: "דתן"},
  {ref: "abiram", name: "אבירם", name_en: "Abiram", role: "מרד", period: "מדבר", book: "במדבר", birth: null, death: null, hebrew_normalized: "אבירם"},
  {ref: "balaam2", name: "בלעם בן בעור", name_en: "Balaam", role: "מכשף", period: "מדבר", book: "במדבר", birth: null, death: null, hebrew_normalized: "בלעם בן בעור"},
  {ref: "balak2", name: "בלק בן ציפור", name_en: "Balak", role: "מלך", period: "מדבר", book: "במדבר", birth: null, death: null, hebrew_normalized: "בלק בן ציפור"},
  {ref: "og", name: "עוג מלך הבשן", name_en: "Og", role: "מלך", period: "כיבוש הארץ", book: "יהושע", birth: null, death: null, hebrew_normalized: "עוג מלך הבשן"},
  {ref: "sihon", name: "סיחון מלך האמורי", name_en: "Sihon", role: "מלך", period: "כיבוש הארץ", book: "יהושע", birth: null, death: null, hebrew_normalized: "סיחון מלך האמורי"},
  {ref: "rahab", name: "רחב", name_en: "Rahab", role: "זונה", period: "כיבוש הארץ", book: "יהושע", birth: null, death: null, hebrew_normalized: "רחב"},
  {ref: "achan", name: "עכן", name_en: "Achan", role: "חוטא", period: "כיבוש הארץ", book: "יהושע", birth: null, death: null, hebrew_normalized: "עכן"},
  {ref: "othniel", name: "עתניאל בן קנז", name_en: "Othniel", role: "שופט", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "עתניאל בן קנז"},
  {ref: "ehud", name: "אהוד בן גרא", name_en: "Ehud", role: "שופט", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "אהוד בן גרא"},
  {ref: "shamgar", name: "שמגר", name_en: "Shamgar", role: "שופט", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "שמגר"},
  {ref: "tola", name: "תולע", name_en: "Tola", role: "שופט", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "תולע"},
  {ref: "jair", name: "יאיר", name_en: "Jair", role: "שופט", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "יאיר"},
  {ref: "jephthah", name: "יפתח", name_en: "Jephthah", role: "שופט", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "יפתח"},
  {ref: "ibzan", name: "אבצן", name_en: "Ibzan", role: "שופט", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "אבצן"},
  {ref: "elon", name: "אלון", name_en: "Elon", role: "שופט", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "אלון"},
  {ref: "abdon", name: "עבדון", name_en: "Abdon", role: "שופט", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "עבדון"},
  {ref: "elkanah", name: "אלקנה", name_en: "Elkanah", role: "אב שמואל", period: "שופטים", book: "שמואל", birth: null, death: null, hebrew_normalized: "אלקנה"},
  {ref: "hannah", name: "חנה", name_en: "Hannah", role: "אם שמואל", period: "שופטים", book: "שמואל", birth: null, death: null, hebrew_normalized: "חנה"},
  {ref: "peninnah", name: "פנינה", name_en: "Peninnah", role: "כלה", period: "שופטים", book: "שמואל", birth: null, death: null, hebrew_normalized: "פנינה"},
  {ref: "eli", name: "עלי הכהן", name_en: "Eli", role: "כהן גדול", period: "שופטים", book: "שמואל", birth: null, death: null, hebrew_normalized: "עלי הכהן"},
  {ref: "hopni", name: "חופני", name_en: "Hopni", role: "בן עלי", period: "שופטים", book: "שמואל", birth: null, death: null, hebrew_normalized: "חופני"},
  {ref: "phinehas", name: "פינחס", name_en: "Phinehas", role: "בן עלי", period: "שופטים", book: "שמואל", birth: null, death: null, hebrew_normalized: "פינחס"},
  {ref: "ishbosheth", name: "אישבשת", name_en: "Ishbosheth", role: "מלך", period: "מלכות שאול", book: "שמואל", birth: null, death: null, hebrew_normalized: "אישבשת"},
  {ref: "mephibosheth", name: "מפיבושת", name_en: "Mephibosheth", role: "בן שאול", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "מפיבושת"},
  {ref: "ziba", name: "ציבא", name_en: "Ziba", role: "עבד", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "ציבא"},
  {ref: "hushai", name: "חושי", name_en: "Hushai", role: "יועץ", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "חושי"},
  {ref: "ahithophel", name: "אחיתופל", name_en: "Ahithophel", role: "יועץ", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "אחיתופל"},
  {ref: "abiathar", name: "אביתר", name_en: "Abiathar", role: "כהן", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "אביתר"},
  {ref: "zadok", name: "צדוק", name_en: "Zadok", role: "כהן", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "צדוק"},
  {ref: "benaiah", name: "בניה", name_en: "Benaiah", role: "גיבור", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "בניה"},
  {ref: "hiram", name: "חירם מלך צור", name_en: "Hiram", role: "מלך", period: "מלכות דוד", book: "מלכים", birth: null, death: null, hebrew_normalized: "חירם מלך צור"},
  {ref: "abishag", name: "אבישג", name_en: "Abishag", role: "נערה", period: "מלכות דוד", book: "מלכים", birth: null, death: null, hebrew_normalized: "אבישג"},
  {ref: "adonijah", name: "אדניה", name_en: "Adonijah", role: "בן דוד", period: "מלכות דוד", book: "מלכים", birth: null, death: null, hebrew_normalized: "אדניה"},
  {ref: "shimei", name: "שמעי בן גרא", name_en: "Shimei", role: "מרד", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "שמעי בן גרא"},
  {ref: "rehoboam", name: "רחבעם", name_en: "Rehoboam", role: "מלך", period: "מלכות דוד", book: "מלכים", birth: null, death: null, hebrew_normalized: "רחבעם"},
  {ref: "jeroboam", name: "ירבעם", name_en: "Jeroboam", role: "מלך", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "ירבעם"},
  {ref: "ahijah", name: "אחיה הנביא", name_en: "Ahijah", role: "נביא", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "אחיה הנביא"},
  {ref: "baasha", name: "בעשא", name_en: "Baasha", role: "מלך", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "בעשא"},
  {ref: "omri", name: "עמרי", name_en: "Omri", role: "מלך", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "עמרי"},
  {ref: "tibni", name: "תבני", name_en: "Tibni", role: "מלך", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "תבני"},
  {ref: "zimri", name: "זמרי", name_en: "Zimri", role: "מלך", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "זמרי"},
  {ref: "ahaziah", name: "אחזיה", name_en: "Ahaziah", role: "מלך", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "אחזיה"},
  {ref: "jehoram", name: "יהורם", name_en: "Jehoram", role: "מלך", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "יהורם"},
  {ref: "jehu", name: "יהוא", name_en: "Jehu", role: "מלך", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "יהוא"},
  {ref: "athaliah", name: "עתליה", name_en: "Athaliah", role: "מלכה", period: "מלכות יהודה", book: "מלכים", birth: null, death: null, hebrew_normalized: "עתליה"},
  {ref: "joash2", name: "יהואש", name_en: "Joash", role: "מלך", period: "מלכות יהודה", book: "מלכים", birth: null, death: null, hebrew_normalized: "יהואש"},
  {ref: "amaziah", name: "אמציה", name_en: "Amaziah", role: "מלך", period: "מלכות יהודה", book: "מלכים", birth: null, death: null, hebrew_normalized: "אמציה"},
  {ref: "uzziah", name: "עזיהו", name_en: "Uzziah", role: "מלך", period: "מלכות יהודה", book: "מלכים", birth: null, death: null, hebrew_normalized: "עזיהו"},
  {ref: "jotham", name: "יותם", name_en: "Jotham", role: "מלך", period: "מלכות יהודה", book: "מלכים", birth: null, death: null, hebrew_normalized: "יותם"},
  {ref: "ahaz", name: "אחז", name_en: "Ahaz", role: "מלך", period: "מלכות יהודה", book: "מלכים", birth: null, death: null, hebrew_normalized: "אחז"},
  {ref: "manasseh2", name: "מנשה", name_en: "Manasseh", role: "מלך", period: "מלכות יהודה", book: "מלכים", birth: null, death: null, hebrew_normalized: "מנשה"},
  {ref: "amon", name: "אמון", name_en: "Amon", role: "מלך", period: "מלכות יהודה", book: "מלכים", birth: null, death: null, hebrew_normalized: "אמון"},
  {ref: "jehoahaz", name: "יהואחז", name_en: "Jehoahaz", role: "מלך", period: "מלכות יהודה", book: "מלכים", birth: null, death: null, hebrew_normalized: "יהואחז"},
  {ref: "jehoiakim2", name: "יהויקים", name_en: "Jehoiakim", role: "מלך", period: "מלכות יהודה", book: "מלכים", birth: null, death: null, hebrew_normalized: "יהויקים"},
  {ref: "zedeiah", name: "צדקיהו", name_en: "Zedekiah", role: "מלך", period: "מלכות יהודה", book: "מלכים", birth: null, death: null, hebrew_normalized: "צדקיהו"},
  {ref: "nebuchadnezzar", name: "נבוכדנצר", name_en: "Nebuchadnezzar", role: "מלך", period: "גלות בבל", book: "דניאל", birth: null, death: null, hebrew_normalized: "נבוכדנצר"},
  {ref: "belshazzar", name: "בלשאצר", name_en: "Belshazzar", role: "מלך", period: "גלות בבל", book: "דניאל", birth: null, death: null, hebrew_normalized: "בלשאצר"},
  {ref: "darius", name: "דריוש", name_en: "Darius", role: "מלך", period: "גלות בבל", book: "דניאל", birth: null, death: null, hebrew_normalized: "דריוש"},
  {ref: "cyrus", name: "כורש", name_en: "Cyrus", role: "מלך", period: "שיבת ציון", book: "עזרא", birth: null, death: null, hebrew_normalized: "כורש"},
  {ref: "artaxerxes", name: "ארתחששתא", name_en: "Artaxerxes", role: "מלך", period: "שיבת ציון", book: "עזרא", birth: null, death: null, hebrew_normalized: "ארתחששתא"},
  {ref: "sanballat", name: "סנבלט", name_en: "Sanballat", role: "אויב", period: "שיבת ציון", book: "נחמיה", birth: null, death: null, hebrew_normalized: "סנבלט"},
  {ref: "tobiah", name: "טוביה העמוני", name_en: "Tobiah", role: "אויב", period: "שיבת ציון", book: "נחמיה", birth: null, death: null, hebrew_normalized: "טוביה העמוני"},
  {ref: "gashmu", name: "גשם", name_en: "Gashmu", role: "אויב", period: "שיבת ציון", book: "נחמיה", birth: null, death: null, hebrew_normalized: "גשם"},
  {ref: "eliezer", name: "אליעזר", name_en: "Eliezer", role: "עבד אברהם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "אליעזר"},
  {ref: "melchizedek", name: "מלכי צדק", name_en: "Melchizedek", role: "כהן", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "מלכי צדק"},
  {ref: "king", name: "אבימלך", name_en: "Abimelech", role: "מלך", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "אבימלך"},
  {ref: "hagar", name: "הagar", name_en: "Hagar", role: "שפחה", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "הagar"},
  {ref: "keturah", name: "קטורה", name_en: "Keturah", role: "אשה", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "קטורה"},
  {ref: "midian", name: "מדן", name_en: "Midian", role: "בן אברהם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "מדן"},
  {ref: "jokshan", name: "יקשן", name_en: "Jokshan", role: "בן אברהם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "יקשן"},
  {ref: "medan", name: "מדן", name_en: "Medan", role: "בן אברהם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "מדן"},
  {ref: "ishbak", name: "ישבק", name_en: "Ishbak", role: "בן אברהם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "ישבק"},
  {ref: "shuah", name: "שוח", name_en: "Shuah", role: "בן אברהם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "שוח"},
  {ref: "lot", name: "לוט", name_en: "Lot", role: "בן אחי אברהם", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "לוט"},
  {ref: "milcah", name: "מלכה", name_en: "Milcah", role: "אשה", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "מלכה"},
  {ref: "betheul", name: "בתואל", name_en: "Bethuel", role: "אב רבקה", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "בתואל"},
  {ref: "reumah", name: "רומה", name_en: "Reumah", role: "פילגש", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "רומה"},
  {ref: "timna", name: "תמנע", name_en: "Timna", role: "פילגש", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "תמנע"},
  {ref: "oholibamah", name: "אהליבמה", name_en: "Oholibamah", role: "אשה", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "אהליבמה"},
  {ref: "anah", name: "ענה", name_en: "Anah", role: "אב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "ענה"},
  {ref: "zibeon", name: "צבעון", name_en: "Zibeon", role: "אב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "צבעון"},
  {ref: "zohar", name: "צחר", name_en: "Zohar", role: "אב", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "צחר"},
  {ref: "hamor", name: "חמור", name_en: "Hamor", role: "נשיא", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "חמור"},
  {ref: "shechem2", name: "שכם בן חמור", name_en: "Shechem", role: "נסיך", period: "דור האבות", book: "בראשית", birth: null, death: null, hebrew_normalized: "שכם בן חמור"},
  {ref: "debir", name: "דביר", name_en: "Debir", role: "מלך", period: "כיבוש הארץ", book: "יהושע", birth: null, death: null, hebrew_normalized: "דביר"},
  {ref: "jabin", name: "יאבין", name_en: "Jabin", role: "מלך", period: "כיבוש הארץ", book: "יהושע", birth: null, death: null, hebrew_normalized: "יאבין"},
  {ref: "hazor", name: "חצור", name_en: "Hazor", role: "מלך", period: "כיבוש הארץ", book: "יהושע", birth: null, death: null, hebrew_normalized: "חצור"},
  {ref: "hebron", name: "חברון", name_en: "Hebron", role: "מלך", period: "כיבוש הארץ", book: "יהושע", birth: null, death: null, hebrew_normalized: "חברון"},
  {ref: "eglon", name: "אגלון", name_en: "Eglon", role: "מלך", period: "כיבוש הארץ", book: "יהושע", birth: null, death: null, hebrew_normalized: "אגלון"},
  {ref: "zalmunna", name: "צלמנה", name_en: "Zalmunna", role: "מלך", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "צלמנה"},
  {ref: "zebah", name: "זבח", name_en: "Zebah", role: "מלך", period: "שופטים", book: "שופטים", birth: null, death: null, hebrew_normalized: "זבח"},
  {ref: "husham", name: "הושם", name_en: "Husham", role: "מלך", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "הושם"},
  {ref: "hadad", name: "הדד", name_en: "Hadad", role: "מלך", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "הדד"},
  {ref: "samlah", name: "שמלה", name_en: "Samlah", role: "מלך", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "שמלה"},
  {ref: "shaul", name: "שאול", name_en: "Shaul", role: "מלך", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "שאול"},
  {ref: "baal-hanan", name: "בעל חנן", name_en: "Baal-Hanan", role: "מלך", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "בעל חנן"},
  {ref: "achbor", name: "עכבור", name_en: "Achbor", role: "מלך", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "עכבור"},
  {ref: "jobab", name: "יובב", name_en: "Jobab", role: "מלך", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "יובב"},
  {ref: "husham2", name: "הושם", name_en: "Husham", role: "מלך", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "הושם"},
  {ref: "hadar", name: "הדר", name_en: "Hadar", role: "מלך", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "הדר"},
  {ref: "bela", name: "בלע", name_en: "Bela", role: "מלך", period: "דור ראשון", book: "בראשית", birth: null, death: null, hebrew_normalized: "בלע"},
  {ref: "beor", name: "בעור", name_en: "Beor", role: "אב", period: "מדבר", book: "במדבר", birth: null, death: null, hebrew_normalized: "בעור"},
  {ref: "reuel", name: "רעואל", name_en: "Reuel", role: "אב", period: "מדבר", book: "שמות", birth: null, death: null, hebrew_normalized: "רעואל"},
  {ref: "hobab", name: "חובב", name_en: "Hobab", role: "חותן", period: "מדבר", book: "שמות", birth: null, death: null, hebrew_normalized: "חובב"},
  {ref: "hoshea", name: "הושע", name_en: "Hoshea", role: "מנהיג", period: "כיבוש הארץ", book: "יהושע", birth: null, death: null, hebrew_normalized: "הושע"},
  {ref: "shmuel", name: "שמואל", name_en: "Samuel", role: "נביא", period: "שופטים", book: "שמואל", birth: null, death: null, hebrew_normalized: "שמואל"},
  {ref: "gad2", name: "גד הנביא", name_en: "Gad", role: "נביא", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "גד הנביא"},
  {ref: "nathan2", name: "נתן", name_en: "Nathan", role: "נביא", period: "מלכות דוד", book: "שמואל", birth: null, death: null, hebrew_normalized: "נתן"},
  {ref: "ahijah2", name: "אחיה", name_en: "Ahijah", role: "נביא", period: "מלכות ירבעם", book: "מלכים", birth: null, death: null, hebrew_normalized: "אחיה"},
  {ref: "jehu2", name: "יהוא בן חנני", name_en: "Jehu", role: "נביא", period: "מלכות יהורם", book: "מלכים", birth: null, death: null, hebrew_normalized: "יהוא בן חנני"},
  {ref: "elisha2", name: "אלישע", name_en: "Elisha", role: "נביא", period: "מלכות ישראל", book: "מלכים", birth: null, death: null, hebrew_normalized: "אלישע"},
  {ref: "jonah2", name: "יונה בן אמתי", name_en: "Jonah", role: "נביא", period: "מלכות ישראל", book: "יונה", birth: null, death: null, hebrew_normalized: "יונה בן אמתי"},
  {ref: "amos2", name: "עמוס", name_en: "Amos", role: "נביא", period: "מלכות ישראל", book: "עמוס", birth: null, death: null, hebrew_normalized: "עמוס"},
  {ref: "hosea2", name: "הושע בן בארי", name_en: "Hosea", role: "נביא", period: "מלכות ישראל", book: "הושע", birth: null, death: null, hebrew_normalized: "הושע בן בארי"},
  {ref: "micha2", name: "מיכה המרשתי", name_en: "Micah", role: "נביא", period: "מלכות יהודה", book: "מיכה", birth: null, death: null, hebrew_normalized: "מיכה המרשתי"},
  {ref: "isaiah2", name: "ישעיהו בן אמוץ", name_en: "Isaiah", role: "נביא", period: "מלכות יהודה", book: "ישעיהו", birth: null, death: null, hebrew_normalized: "ישעיהו בן אמוץ"},
  {ref: "habakkuk2", name: "חבקוק", name_en: "Habakkuk", role: "נביא", period: "מלכות יהודה", book: "חבקוק", birth: null, death: null, hebrew_normalized: "חבקוק"},
  {ref: "zephaniah2", name: "צפניה בן כושי", name_en: "Zephaniah", role: "נביא", period: "מלכות יהודה", book: "צפניה", birth: null, death: null, hebrew_normalized: "צפניה בן כושי"},
  {ref: "haggai2", name: "חגי", name_en: "Haggai", role: "נביא", period: "שיבת ציון", book: "חגי", birth: null, death: null, hebrew_normalized: "חגי"},
  {ref: "zechariah2", name: "זכריה בן ברכיה", name_en: "Zechariah", role: "נביא", period: "שיבת ציון", book: "זכריה", birth: null, death: null, hebrew_normalized: "זכריה בן ברכיה"},
  {ref: "malachi2", name: "מלאכי", name_en: "Malachi", role: "נביא", period: "שיבת ציון", book: "מלאכי", birth: null, death: null, hebrew_normalized: "מלאכי"},
  {ref: "jeremiah2", name: "ירמיהו בן חלקיה", name_en: "Jeremiah", role: "נביא", period: "חורבן בית ראשון", book: "ירמיהו", birth: null, death: null, hebrew_normalized: "ירמיהו בן חלקיה"},
  {ref: "ezekiel2", name: "יחזקאל בן בוזי", name_en: "Ezekiel", role: "נביא", period: "חורבן בית ראשון", book: "יחזקאל", birth: null, death: null, hebrew_normalized: "יחזקאל בן בוזי"},
  {ref: "daniel2", name: "דניאל", name_en: "Daniel", role: "חכם", period: "גלות בבל", book: "דניאל", birth: null, death: null, hebrew_normalized: "דניאל"},
  {ref: "ezra2", name: "עזרא הסופר", name_en: "Ezra", role: "סופר", period: "שיבת ציון", book: "עזרא", birth: null, death: null, hebrew_normalized: "עזרא הסופר"},
  {ref: "nehemiah2", name: "נחמיה בן חכליה", name_en: "Nehemiah", role: "מושל", period: "שיבת ציון", book: "נחמיה", birth: null, death: null, hebrew_normalized: "נחמיה בן חכליה"},
  {ref: "esther2", name: "אסתר", name_en: "Esther", role: "מלכה", period: "מלכות פרס", book: "אסתר", birth: null, death: null, hebrew_normalized: "אסתר"},
  {ref: "mordechai2", name: "מרדכי בן יאיר", name_en: "Mordechai", role: "מנהיג", period: "מלכות פרס", book: "אסתר", birth: null, death: null, hebrew_normalized: "מרדכי בן יאיר"},
  {ref: "vashti2", name: "ושתי", name_en: "Vashti", role: "מלכה", period: "מלכות פרס", book: "אסתר", birth: null, death: null, hebrew_normalized: "ושתי"},
  {ref: "haman2", name: "המן האגגי", name_en: "Haman", role: "שר", period: "מלכות פרס", book: "אסתר", birth: null, death: null, hebrew_normalized: "המן האגגי"},
  {ref: "zerubbabel2", name: "זרובבל בן שאלתיאל", name_en: "Zerubbabel", role: "מנהיג", period: "שיבת ציון", book: "עגני", birth: null, death: null, hebrew_normalized: "זרובבל בן שאלתיאל"},
  {ref: "joshua2", name: "יהושע בן יהוצדק", name_en: "Joshua", role: "כהן גדול", period: "שיבת ציון", book: "זכריה", birth: null, death: null, hebrew_normalized: "יהושע בן יהוצדק"}
] AS personData

CREATE (p:Person)
SET p = personData
SET p.id = personData.ref;

// ── CREATE MENTIONS RELATIONSHIPS ─────────────────────
// Link people to verses where their name appears in hebrew_normalized

MATCH (p:Person)
WITH p
MATCH (v:Verse)
WHERE v.hebrew_normalized CONTAINS p.hebrew_normalized
  AND size(p.hebrew_normalized) > 2
WITH p, v
MERGE (v)-[:MENTIONS]->(p)
ON CREATE SET v.mentions_count = coalesce(v.mentions_count, 0) + 1;

// ── CREATE FAMILY RELATIONSHIPS ──────────────────────

// Abraham family
MATCH (a:Person {ref: "abraham"}), (i:Person {ref: "isaac"})
MERGE (a)-[:FATHER_OF]->(i);
MATCH (a:Person {ref: "abraham"}), (s:Person {ref: "sarah"})
MERGE (a)-[:HUSBAND_OF]->(s);

// Isaac family
MATCH (i:Person {ref: "isaac"}), (j:Person {ref: "jacob"})
MERGE (i)-[:FATHER_OF]->(j);
MATCH (i:Person {ref: "isaac"}), (e:Person {ref: "esau"})
MERGE (i)-[:FATHER_OF]->(e);

// Jacob family
MATCH (j:Person {ref: "jacob"}), (jo:Person {ref: "joseph"})
MERGE (j)-[:FATHER_OF]->(jo);
MATCH (j:Person {ref: "jacob"}), (l:Person {ref: "leah"})
MERGE (j)-[:HUSBAND_OF]->(l);
MATCH (j:Person {ref: "jacob"}), (r:Person {ref: "rachel"})
MERGE (j)-[:HUSBAND_OF]->(r);

// Moses family
MATCH (m:Person {ref: "moshe"}), (a:Person {ref: "amram"})
MERGE (a)-[:FATHER_OF]->(m);
MATCH (m:Person {ref: "moshe"}), (j:Person {ref: "jochebed"})
MERGE (j)-[:MOTHER_OF]->(m);
MATCH (m:Person {ref: "moshe"}), (a2:Person {ref: "aaron"})
MERGE (m)-[:BROTHER_OF]->(a2);
MATCH (m:Person {ref: "moshe"}), (mi:Person {ref: "miriam"})
MERGE (m)-[:BROTHER_OF]->(mi);

// David family
MATCH (d:Person {ref: "david"}), (s:Person {ref: "solomon"})
MERGE (d)-[:FATHER_OF]->(s);
MATCH (d:Person {ref: "david"}), (a:Person {ref: "absalom"})
MERGE (d)-[:FATHER_OF]->(a);

// ── STATS ───────────────────────────────────────────
MATCH (p:Person) RETURN count(p) AS total_people;
MATCH ()-[r:MENTIONS]->() RETURN count(r) AS total_mentions;
MATCH ()-[r:FATHER_OF]->() RETURN count(r) AS father_relationships;
