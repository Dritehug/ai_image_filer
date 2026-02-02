import os
import shutil

# You will fill this in manually
APP_ROOT = "C:/Projects/TagC/app"   # <-- your choice

def move_image_to_category(path, category):
    # Base directory for sorted images
    base_dir = os.path.join(APP_ROOT, "sorted_images")
    os.makedirs(base_dir, exist_ok=True)

    # Category folder
    category_dir = os.path.join(base_dir, category)
    os.makedirs(category_dir, exist_ok=True)

    # Extract filename only
    filename = os.path.basename(path)

    # Build destination path
    new_path = os.path.join(category_dir, filename)

    # Copy file (preserves metadata)
    shutil.copy2(path, new_path)

    return new_path