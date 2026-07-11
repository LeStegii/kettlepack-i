# KettlePack I

### How to work with this repository
1. Clone the repository.
2. Install Python and [uv](https://github.com/astral-sh/uv).
3. Run `uv sync --all-extras` to create a virtual environment and setup the workspace.
4. Run `uv run build compile` to generate a modpack zip file.

## How to make changes
The [`modpack`](modpack) directory is a 1:1 mapping of the content of the modpack zip file exported by launchers like CurseForge or ATLauncher. 
You can make changes to the modpack by editing the files in this directory.

Make sure that the `modlist.html` and `manifest.json` files are in sync (same order and same number of entries).

You can also copy the exported file from the modpack zip file into the [`modpack`](modpack) directory and run `uv run build setup` to add additional information to the `manifest.json` file.

When using `uv run build compile`, the `modlist.html` and `manifest.json` files will be cleaned up and exported.
