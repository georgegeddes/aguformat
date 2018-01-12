# aguformat
A messy script I made to flatten TeX documents to submit to AGU journals.

The script lokos for `\input`, `\include`, and `\bibliography` statements and replaces them with the file's contents.
It also strips out comments, and makes some substitutions, like changing `\vec` to `\mathbf`

Example:
```sh
python aguformat.py -i main -o output
```

This example reads main.tex and creates a flattened version as output.tex.
