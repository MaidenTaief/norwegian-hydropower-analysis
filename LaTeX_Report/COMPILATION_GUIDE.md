# LaTeX Compilation Guide

## Option 1: Overleaf (Recommended)

**Overleaf** is the easiest way to compile this LaTeX document without installing anything locally.

### Steps:
1. Go to [overleaf.com](https://www.overleaf.com)
2. Create a free account or log in
3. Click "New Project" → "Upload Project"
4. Upload all files from this `LaTeX_Report` folder as a ZIP file
5. Set the main document to `main.tex`
6. Click "Recompile" - the PDF will be generated automatically

### Overleaf Settings:
- **Compiler**: pdfLaTeX (default)
- **Main document**: `main.tex` (complete with figures)
- **TeX Live version**: 2023 or latest

## Option 2: Local Installation

If you have LaTeX installed locally, use the provided Makefile:

```bash
# Basic compilation (no figures)
make pdf

# With bibliography (when you add references)
make full

# View the PDF
make view

# Clean auxiliary files
make clean
```

### Required LaTeX Distribution:
- **macOS**: MacTeX
- **Windows**: MiKTeX or TeX Live
- **Linux**: TeX Live (usually available in package manager)

### Installation Commands:

**macOS (using Homebrew):**
```bash
brew install --cask mactex
```

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-full
```

**Windows:**
Download MiKTeX from [miktex.org](https://miktex.org)

## Document Versions

### `main.tex` - Complete Version with Figures
- Complete academic paper with integrated figures
- All 5 analysis figures included:
  - Figure 1: Indian Dam Construction Timeline
  - Figure 2: Indian Spatial Distribution  
  - Figure 3: Indian Data Completeness
  - Figure 4: Norwegian Reservoir Analysis
  - Figure 5: Norwegian Spatial Distribution
- Professional figure captions and references
- High-quality citations from recent literature
- Publication-ready format

## Troubleshooting

### Common Issues:

**1. Missing Packages**
If you get package errors, the document uses only standard LaTeX packages:
- geometry, graphicx, booktabs, longtable
- array, multirow, subcaption, float
- url, amsmath, amsfonts, hyperref
- fancyhdr, setspace, xcolor, titlesec

**2. Figure Not Found**
Ensure all PNG files are in the `figures/` directory:
- `figure_1_indian_timeline.png`
- `figure_2_indian_spatial.png`
- `figure_3_indian_completeness.png`
- `figure_4_norway_reservoir.png`
- `figure_5_norway_spatial.png`

**3. Compilation Errors**
- Use `main.tex` if you encounter figure-related errors
- Ensure LaTeX distribution is up-to-date
- Try Overleaf if local compilation fails

## File Structure

```
LaTeX_Report/
├── main.tex                   # Complete version with figures
├── bibliography.bib          # High-quality references
├── README.md                  # Documentation
├── COMPILATION_GUIDE.md       # This file
├── Makefile                   # Compilation automation
├── figures/                   # Analysis figures
│   ├── figure_1_indian_timeline.png
│   ├── figure_2_indian_spatial.png
│   ├── figure_3_indian_completeness.png
│   ├── figure_4_norway_reservoir.png
│   └── figure_5_norway_spatial.png
└── sections/                  # Optional modular sections
```

## Next Steps

1. **Complete Literature Review**: Add references to `bibliography.bib`
2. **Customize**: Replace `[Your Name]` and `[Your Institution]` in the document
3. **Review**: Proofread the content and adjust as needed
4. **Submit**: Format according to target journal requirements

## Support

For LaTeX-specific questions:
- [Overleaf Documentation](https://www.overleaf.com/learn)
- [LaTeX Wikibook](https://en.wikibooks.org/wiki/LaTeX)
- [TeX Stack Exchange](https://tex.stackexchange.com)

The document is designed to be publication-ready and follows academic formatting standards. 