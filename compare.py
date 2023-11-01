import os
import shutil
from collections import defaultdict
from pprint import pprint

def compare_folders(folder1, folder2):
    folder1_items = get_items_info(folder1)
    folder2_items = get_items_info(folder2)

    to_sync = defaultdict(list)

    # Compare and copy files <folder1 to folder2>
    for item_name, (item_size, is_file) in folder1_items.items():
        if item_size == "Error":
            to_sync["Error"].append(item_name)
            continue
        dest_info = folder2_items.get(item_name)
    
        if dest_info is None or dest_info != (item_size, is_file):
            dest_data = (folder2, item_name, item_size, is_file)
            to_sync[folder1].append(dest_data)

    # Compare and copy files <folder2 to folder1>
    for item_name, (item_size, is_file) in folder2_items.items():
        if item_size == "Error":
            to_sync["Error"].append(item_name)
            continue
        dest_info = folder1_items.get(item_name)

        if dest_info is None or dest_info != (item_size, is_file):
            dest_data = (folder1, item_name, item_size, is_file)
            to_sync[folder2].append(dest_data)

    formatted_response = format_response(to_sync)
    to_sync.pop("Error")
    
    return to_sync, formatted_response

def copy_data(metadata):
    for source_path, to_sync in metadata.items():
        for dest_path, item_name, item_size, is_file in to_sync:

            if is_file:
                dest_file_path = os.path.join(dest_path, item_name)
                source_file_path = os.path.join(source_path, item_name)
                if not os.path.exists(dest_file_path):
                    shutil.copy2(source_file_path, dest_file_path)
                    print(f"Copied file: {item_name} of size: {item_size}")
                else:
                    print(f"{dest_file_path} already exists")

            else:
                dest_folder_path = os.path.join(dest_path, item_name)
                source_folder_path = os.path.join(source_path, item_name)
                if not os.path.exists(dest_folder_path):
                    shutil.copytree(source_folder_path, dest_folder_path, symlinks=True)
                    print(f"Copied folder: {item_name} of size: {item_size}")
                else:
                    print(f"{dest_folder_path} already exists")

            yield item_size

def format_response(to_format):
    if len(to_format) == 0:
        return "Already in Sync!"

    formatted_response_str = "Data to sync:\n\n"
    for key, value in to_format.items():
        if key == "Error":
            continue
        formatted_response_str += f"for folder\n{key}:\n"
        formatted_response_str += '\n'.join([val[1] for val in value])
        formatted_response_str += '\n\n'
    if "Error" in to_format:
        formatted_response_str += "Cannot sync the following:\n\n"
        formatted_response_str += '\n'.join(to_format["Error"])
    
    return formatted_response_str

def get_items_info(folder):
    items_info = {}
    for root, dirs, files in os.walk(folder):
        for dir_name in dirs:
            try:
                item_path = os.path.join(root, dir_name)
                relative_path = os.path.relpath(item_path, folder)
                item_size = os.path.getsize(item_path)
                items_info[relative_path] = (item_size, False)
            except:
                items_info[relative_path] = ("Error", False)
            finally:
                continue

        for file_name in files:
            try:
                item_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(item_path, folder)
                item_size = os.path.getsize(item_path)
                items_info[relative_path] = (item_size, True)
            except:
                items_info[relative_path] = ("Error", True)
            finally:
                continue

    return items_info

if __name__ == "__main__":
    folder1 = "X:\\Work\\python_scripts\\snippets\\X\\New2"
    folder2 = "X:\\Work\\python_scripts\\snippets\\X\\New"

    diff = compare_folders(folder1, folder2)
    pprint(diff)