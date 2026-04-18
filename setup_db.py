import sqlite3
import json

def parse_rarity(rarity_str):
    if rarity_str.startswith("TIER_"):
        return int(rarity_str.split("_")[1])
    return 0

def clean_name(name):
    """Remove leading/trailing single or double quotes if present."""
    if not name:
        return ""
    name = name.strip()
    if name.startswith("'") and name.endswith("'"):
        name = name[1:-1]
    if name.startswith('"') and name.endswith('"'):
        name = name[1:-1]
    return name

def init_db():
    conn = sqlite3.connect('rhodes.db')
    cursor = conn.cursor()

    with open('schema.sql', 'r') as f:
        schema = f.read()
    cursor.executescript(schema)

    # ----- Load roguelike data (IS3) -----
    with open('roguelike_topic_table.json', 'r', encoding='utf-8') as f:
        rogue_data = json.load(f)

    details = rogue_data.get("details", {})
    topic = details.get("rogue_3", {})
    items = topic.get("items", {})

    if not items:
        print("Warning: No items found in details.rogue_3.")
    else:
        print(f"Found {len(items)} total items in rogue_3.")

    # ----- SQUADS (type == "BAND") -----
    squads = []
    for item_id, details_item in items.items():
        if details_item.get("type") == "BAND":
            name = clean_name(details_item.get("name", "Unknown Squad"))
            buff = details_item.get("usage", "")
            squads.append((name, buff))
    print(f"Found {len(squads)} squads")
    if not squads:
        squads = [("Leader Squad", "Default buff"), ("Gathering Squad", "Default buff")]
    cursor.executemany("INSERT INTO Squad (Squad_Name, Passive_Buff) VALUES (?, ?)", squads)

    # ----- RELICS (type == "RELIC") -----
    relics = []
    for item_id, details_item in items.items():
        if details_item.get("type") == "RELIC":
            name = clean_name(details_item.get("name", "Unknown Relic"))
            effect = details_item.get("usage", "")
            category = details_item.get("subType", "")
            relics.append((name, effect, category))
    print(f"Found {len(relics)} relics")
    cursor.executemany("INSERT INTO Relic (Name, Effect_Description, Category) VALUES (?, ?, ?)", relics)

    # ----- OPERATORS from character_table.json -----
    with open('character_table.json', 'r', encoding='utf-8') as f:
        char_data = json.load(f)

    operators = []
    for op_id, info in char_data.items():
        if not op_id.startswith("char_"):
            continue
        if info.get("isNotObtainable", False):
            continue
        name = clean_name(info.get("name", ""))
        rarity = parse_rarity(info.get("rarity", "TIER_0"))
        prof = info.get("profession", "")
        archetype = info.get("subProfessionId", "")
        operators.append((op_id, name, rarity, prof, archetype))
    print(f"Found {len(operators)} operators")
    cursor.executemany("""
        INSERT INTO Operator (OperatorID, Name, Rarity, Class, Archetype)
        VALUES (?, ?, ?, ?, ?)
    """, operators)

    # ----- Create junction tables -----
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Run_Relic (
            RunID INTEGER,
            RelicID INTEGER,
            PRIMARY KEY (RunID, RelicID),
            FOREIGN KEY (RunID) REFERENCES Run(RunID),
            FOREIGN KEY (RelicID) REFERENCES Relic(RelicID)
        );
        CREATE TABLE IF NOT EXISTS Run_Operator (
            RunID INTEGER,
            OperatorID TEXT,
            PRIMARY KEY (RunID, OperatorID),
            FOREIGN KEY (RunID) REFERENCES Run(RunID),
            FOREIGN KEY (OperatorID) REFERENCES Operator(OperatorID)
        );
        CREATE TABLE IF NOT EXISTS Squad_Synergy (
            SquadID INTEGER,
            OperatorID TEXT,
            PRIMARY KEY (SquadID, OperatorID),
            FOREIGN KEY (SquadID) REFERENCES Squad(SquadID),
            FOREIGN KEY (OperatorID) REFERENCES Operator(OperatorID)
        );
    """)

    # ----- Example runs with relics and operators -----
    cursor.execute("SELECT SquadID FROM Squad LIMIT 2")
    squad_ids = [row[0] for row in cursor.fetchall()]
    if len(squad_ids) >= 2:
        # First run
        cursor.execute("""
            INSERT INTO Run (Date, Difficulty_Level, Ending_Reached, Final_Score, SquadID)
            VALUES (?, ?, ?, ?, ?)
        """, ('2026-04-17', 7, 'Ending 1', 4500, squad_ids[0]))
        run_id = cursor.lastrowid
        # Add first two relics and first two operators (if exist)
        cursor.execute("SELECT RelicID FROM Relic LIMIT 2")
        relic_ids = [row[0] for row in cursor.fetchall()]
        for rid in relic_ids:
            cursor.execute("INSERT INTO Run_Relic (RunID, RelicID) VALUES (?, ?)", (run_id, rid))
        cursor.execute("SELECT OperatorID FROM Operator LIMIT 2")
        op_ids = [row[0] for row in cursor.fetchall()]
        for oid in op_ids:
            cursor.execute("INSERT INTO Run_Operator (RunID, OperatorID) VALUES (?, ?)", (run_id, oid))
        # Second run
        cursor.execute("""
            INSERT INTO Run (Date, Difficulty_Level, Ending_Reached, Final_Score, SquadID)
            VALUES (?, ?, ?, ?, ?)
        """, ('2026-04-16', 15, 'Failed', 1200, squad_ids[1]))
        print("Inserted 2 example runs with relics and operators.")

    conn.commit()
    conn.close()
    print("Database successfully initialized with clean names!")

if __name__ == '__main__':
    init_db()