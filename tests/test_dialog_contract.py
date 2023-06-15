from pathlib import Path

def test_source_reader_uses_reusable_keyboard_dialog():
 s=Path("frontend/src/SearchDesk.tsx").read_text()
 assert "<SourceDialog" in s and "modal-backdrop" not in s
