import os

def create_symlink(src, dest):
    try:
        if os.path.exists(dest):
            return
        rel = os.path.relpath(src, os.path.dirname(dest))
        os.symlink(rel, dest)
    except Exception as e:
        print(f"⚠️ Symlink error: {e}")
