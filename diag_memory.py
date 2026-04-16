from memory import Memory
import os

db = "diag.db"
mem = Memory(db)
print("Memory class imported.")
if hasattr(mem, "get_multimodal_pairs"):
    print("Found get_multimodal_pairs method.")
    pairs = mem.get_multimodal_pairs()
    print(f"Pairs found: {len(pairs)}")
else:
    print("Method NOT found!")

mem.conn.close()
if os.path.exists(db):
    os.remove(db)
