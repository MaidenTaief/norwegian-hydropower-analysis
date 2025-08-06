# Makefile for LaTeX report compilation

# Main document name (without .tex extension)
MAIN = main

# PDF viewer (adjust for your system)
VIEWER = open  # macOS (use 'evince' for Linux, 'start' for Windows)

# Default target
all: pdf

# Compile PDF
pdf:
	pdflatex $(MAIN).tex
	pdflatex $(MAIN).tex  # Run twice for proper cross-references

# Compile with bibliography
full:
	pdflatex $(MAIN).tex
	bibtex $(MAIN)
	pdflatex $(MAIN).tex
	pdflatex $(MAIN).tex

# View the PDF
view: pdf
	$(VIEWER) $(MAIN).pdf

# Clean auxiliary files
clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot *.fdb_latexmk *.fls *.synctex.gz

# Clean everything including PDF
distclean: clean
	rm -f $(MAIN).pdf

# Force rebuild
rebuild: distclean pdf

# Help
help:
	@echo "Available targets:"
	@echo "  pdf      - Compile LaTeX document to PDF"
	@echo "  full     - Compile with bibliography (run after adding references)"
	@echo "  view     - Compile and open PDF viewer"
	@echo "  clean    - Remove auxiliary files"
	@echo "  distclean - Remove all generated files including PDF"
	@echo "  rebuild  - Clean and rebuild from scratch"
	@echo "  help     - Show this help message"

.PHONY: all pdf full view clean distclean rebuild help 