import sqlite3

DATABASE_NAME = 'waste_instructions.db'
# Map your model's predicted index to the class name
CLASS_LABELS = {
    0: 'cardboard',
    1: 'glass',
    2: 'metal',
    3: 'paper',
    4: 'plastic',
    5: 'trash'
}
DISPOSAL_DATA = [
    ('cardboard', 'Recycle in PAPER/CARDBOARD bin. Flatten boxes.', 'Keep dry and clean.'),
    ('glass', 'Recycle in GLASS bin. Rinse jars and bottles.', 'Check rules for color sorting.'),
    ('metal', 'Recycle in METAL/CANS bin. Cans and foil.', 'Ensure cans are empty.'),
    ('paper', 'Recycle in PAPER bin. Newspapers and magazines.', 'Avoid wet or greasy paper.'),
    ('plastic', 'Recycle in PLASTIC bin. Check symbol #1-7.', 'No plastic bags or wrappers.'),
    ('trash', 'Dispose of in the general waste bin.', 'Not recyclable or compostable.')
]

def init_db():
    """Initializes the SQLite database with disposal instructions."""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS instructions')
    c.execute('''
        CREATE TABLE instructions (
            id INTEGER PRIMARY KEY,
            waste_type TEXT NOT NULL,
            disposal_instruction TEXT NOT NULL,
            recycling_tip TEXT
        )
    ''')
    c.executemany('INSERT INTO instructions (waste_type, disposal_instruction, recycling_tip) VALUES (?, ?, ?)', DISPOSAL_DATA)
    conn.commit()
    conn.close()
    print(f"Database {DATABASE_NAME} initialized.")

def get_instructions(waste_type):
    """Retrieves instructions for a given waste type."""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('SELECT disposal_instruction, recycling_tip FROM instructions WHERE waste_type = ?', (waste_type,))
    result = c.fetchone()
    conn.close()
    if result:
        return {'instruction': result[0], 'tip': result[1]}
    return {'instruction': 'Unknown type.', 'tip': ''}

if __name__ == '__main__':
    init_db()