# Comparative Analysis of Dam Infrastructure - LaTeX Report

This folder contains the complete LaTeX document for the academic paper analyzing dam infrastructure patterns in Norway and India.

## Files Overview

- `main.tex` - Main LaTeX document containing the complete paper
- `bibliography.bib` - Bibliography file with references (template)
- `figures/` - Directory for figures and images
- `sections/` - Directory for modular sections (if needed)

## Document Structure

The report includes the following sections:

1. **Title Page** - Professional academic formatting
2. **Abstract** - Comprehensive summary of findings
3. **Introduction** - Background and research objectives
4. **Literature Review** - [To be completed by author]
5. **Methodology** - Data sources and analytical methods
6. **Results** - Detailed findings for both Norway and India
7. **Discussion** - Analysis and interpretation of results
8. **Conclusions** - Key findings and implications
9. **References** - [To be completed by author]

## Key Findings Included

### Norwegian Infrastructure (NVE Database)
- 12,763 total infrastructure elements
- 4,953 dam points, 4,813 dam lines, 2,997 reservoirs
- Construction span: 1660-2025 (365 years)
- Post-WWII boom: 2,831 dams (1945-1980)
- Total capacity: 61,880 million m³

### Indian Infrastructure (GDW Database)
- 7,097 total dams identified
- 307 high-quality dams in clean dataset
- Total power capacity: 28,624 MW
- Post-independence boom: 180 dams (1947-1980)
- Total reservoir area: 10,762 km²

## Compilation Instructions

### Requirements
- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
- Required packages (all standard):
  - geometry, graphicx, booktabs, longtable
  - array, multirow, subcaption, float
  - url, amsmath, amsfonts, hyperref
  - fancyhdr, setspace, xcolor, titlesec

### Compilation Commands

```bash
# Basic compilation
pdflatex main.tex
pdflatex main.tex  # Run twice for proper cross-references

# With bibliography (when references are added)
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Overleaf Usage

1. Upload all files to Overleaf
2. Set compiler to pdfLaTeX
3. Main document: `main.tex`
4. Compile (should work out-of-the-box)

## Adding Figures

To add the generated figures from your analyses:

1. Copy PNG files to `figures/` directory
2. Add figure references in the main document:

```latex
\begin{figure}[H]
\centering
\includegraphics[width=0.8\textwidth]{figures/your_figure.png}
\caption{Your figure caption}
\label{fig:your_label}
\end{figure}
```

## Customization

### Adding Your Information
- Replace `[Your Name]` and `[Your Institution]` on the title page
- Complete the Literature Review section
- Add specific references to `bibliography.bib`

### Document Formatting
- Adjust spacing: Change `\onehalfspacing` to `\doublespacing` if needed
- Modify margins: Edit `\geometry{}` parameters
- Change colors: Modify `\definecolor{}` commands

## Data Sources

- **Norwegian Data**: NVE (Norwegian Water Resources and Energy Directorate)
- **Indian Data**: Global Dam Watch (GDW) Database v1.0
- **Analysis Period**: 1660-2025 (365 years for Norway), 1800-2025 (225 years for India)

## Academic Quality

The document is formatted for academic submission with:
- Professional title page and formatting
- Comprehensive abstract and keywords
- Detailed methodology section
- Statistical tables with proper formatting
- Academic citation structure
- Publication-quality presentation

## Next Steps

1. **Literature Review**: Add relevant academic references
2. **Figures**: Include your generated charts and maps
3. **References**: Complete the bibliography with actual sources
4. **Review**: Proofread and adjust content as needed
5. **Submission**: Format according to target journal/conference requirements

## Contact

For questions about the LaTeX formatting or content, refer to the main project documentation or contact the project team. 