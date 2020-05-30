# Markdown Folding for Gedit

A simple plugin that adds code folding to Markdown files in Gedit. This plugin allows you to collapse and expand Markdown headers.

## Installation

### GNU/Linux
* Simplest: Move `markdown-folding.plugin` and `markdown-folding.py` into `~/.local/share/gedit/plugins`
* Or:
```
cd ~/.local/share/gedit/plugins
git clone https://github.com/apiquerasm/gedit-markdown-folding
```

Then:

* In Gedit, go to Edit &rarr; Preferences &rarr; Plugins to enable the plugin.

## Usage

* `Alt-Z` on a header line will collapse that section
* `Alt-Z` on a folded section will expand it
