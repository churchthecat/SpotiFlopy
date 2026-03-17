import os


def create_symlink(src, dest):
    try:
        if os.path.exists(dest):
            return

        rel_src = os.path.relpath(src, os.path.dirname(dest))
        os.symlink(rel_src, dest)

    except Exception as e:
        print(f"⚠️ Symlink failed: {dest} -> {e}")
