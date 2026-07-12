import json
import os
import re
import shutil
from pathlib import Path

# If this changes, the .gitignore file must be updated accordingly
BUILD_DIR = ".build"
MODPACK_DIR = "modpack"
LINK_FIELD = "__link"
NAME_FIELD = "__name"
AUTHOR_FIELD = "__author"

SORT_MANIFEST_AFTER = NAME_FIELD

MODLIST_ENTRY_REGEX = r'<li><a href="(?P<link>[^"]+)">(?P<mod>.+?)(?: \(by (?P<author>[^)]+)\))?</a></li>'

def load_manifest() -> dict:
    """
    Load the manifest.json file from the modpack directory.
    :return: The manifest as a dictionary.
    """
    with open(f"{MODPACK_DIR}/manifest.json", "r") as f:
        return json.load(f)

def write_manifest(manifest: dict, output_path: Path = Path(f"{MODPACK_DIR}/manifest.json")):
    """
    Write the manifest dictionary to a JSON file.
    :param manifest: The manifest dictionary to write.
    :param output_path: The path to the output JSON file.
    :return: None
    """
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)

def write_modlist(modlist: list[tuple[str, str, str | None]], output_path: Path = Path(f"{MODPACK_DIR}/modlist.html"), sort_modlist: bool = False):
    """
    Write the modlist to an HTML file.
    :param modlist: A list of tuples containing (link, name, author).
    :param output_path: The path to the output HTML file.
    :return: None
    """
    with open(output_path, "w") as f:
        f.write("<ul>\n")
        if sort_modlist:
            modlist = sorted(modlist, key=lambda x: x[1])
        for link, name, author in modlist:
            if author:
                f.write(f'  <li><a href="{link}">{name} (by {author})</a></li>\n')
            else:
                f.write(f'  <li><a href="{link}">{name}</a></li>\n')
        f.write("</ul>\n")

def load_modlist() -> list[tuple[str, str, str | None]]:
    """
    Load the modlist.html file from the modpack directory.
    :return: A list of tuples containing (link, name, author).
    """
    with open(f"{MODPACK_DIR}/modlist.html", "r") as f:
        content = f.read()
        matches = re.findall(MODLIST_ENTRY_REGEX, content)
        return [(link, mod, author) for link, mod, author in matches]

def setup_modpack():
    manifest = load_manifest()
    modlist = load_modlist()
    manifest_files = manifest.get("files", [])
    ids_to_info = {manifest_files[i]["projectID"]: (modlist[i][0], modlist[i][1], modlist[i][2]) for i in range(len(modlist))}

    for mod_entry in manifest_files:
        project_id = mod_entry.get("projectID")
        if project_id in ids_to_info:
            link, name, author = ids_to_info[project_id]
            mod_entry[LINK_FIELD] = link
            mod_entry[NAME_FIELD] = name
            if author:
                mod_entry[AUTHOR_FIELD] = author
        else:
            print(f"Warning: No link found for project ID {project_id}")

    manifest["files"] = sorted(manifest_files, key=lambda x: x.get(SORT_MANIFEST_AFTER, ""))

    write_manifest(manifest)
    write_modlist(modlist, sort_modlist=True)

def get_clean_manifest() -> dict:
    """
    Load the manifest.json file and return a cleaned version without the additional fields.
    :return: The cleaned manifest as a dictionary.
    """
    manifest = load_manifest()
    for mod_entry in manifest.get("files", []):
        mod_entry.pop(LINK_FIELD, None)
        mod_entry.pop(NAME_FIELD, None)
        mod_entry.pop(AUTHOR_FIELD, None)
    return manifest

def compile_modpack():
    """
    Compile the modpack by copying the necessary files to the build directory.
    :return: None
    """
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR, exist_ok=True)

    modlist = load_modlist()
    manifest = get_clean_manifest()

    modpack_name = manifest.get("name", "modpack")
    modpack_version = manifest.get("version", "1.0.0")

    write_modlist(modlist, Path(f"{BUILD_DIR}/modlist.html"))
    write_manifest(manifest, Path(f"{BUILD_DIR}/manifest.json"))

    shutil.make_archive(f"{modpack_name}-{modpack_version}", "zip", BUILD_DIR)



def main():
    import argparse

    actions = {
        "setup": setup_modpack,
        "compile": compile_modpack,
    }

    parser = argparse.ArgumentParser(description="Modpack Builder")
    parser.add_argument(
        "action",
        choices=list(actions.keys()),
        help="Action to perform: compile or clean",
    )
    args = parser.parse_args()

    if args.action in actions:
        actions[args.action]()
    else:
        print(f"Unknown action: {args.action}")
        parser.print_help()
