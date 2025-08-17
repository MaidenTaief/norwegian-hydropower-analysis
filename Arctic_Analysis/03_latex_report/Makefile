# Makefile for Arctic Dam Risk Assessment Report
# Professional LaTeX compilation with bibliography

MAIN = arctic_dam_risk_report
TEX = $(MAIN).tex
PDF = $(MAIN).pdf
BIB = bibliography.bib

# Default target
all: $(PDF)

# Main compilation target
$(PDF): $(TEX) 
	@echo "Compiling Arctic Dam Risk Assessment Report..."
	@echo "Step 1: Initial LaTeX compilation"
	pdflatex -interaction=nonstopmode $(TEX)
	@echo "Step 2: Bibliography processing"
	bibtex $(MAIN) || true
	@echo "Step 3: Second LaTeX compilation"
	pdflatex -interaction=nonstopmode $(TEX)
	@echo "Step 4: Final LaTeX compilation"
	pdflatex -interaction=nonstopmode $(TEX)
	@echo "✅ Report compilation complete: $(PDF)"

# Quick compile (no bibliography)
quick: $(TEX)
	@echo "Quick LaTeX compilation..."
	pdflatex -interaction=nonstopmode $(TEX)
	@echo "✅ Quick compilation complete"

# Clean auxiliary files
clean:
	@echo "Cleaning auxiliary files..."
	rm -f *.aux *.log *.bbl *.blg *.toc *.out *.nav *.snm *.fls *.fdb_latexmk *.synctex.gz
	@echo "✅ Cleanup complete"

# Clean everything including PDF
cleanall: clean
	@echo "Removing PDF output..."
	rm -f $(PDF)
	@echo "✅ Full cleanup complete"

# Check LaTeX installation
check:
	@echo "Checking LaTeX installation..."
	@which pdflatex || echo "❌ pdflatex not found"
	@which bibtex || echo "❌ bibtex not found"
	@echo "✅ LaTeX check complete"

# View PDF (macOS)
view: $(PDF)
	@echo "Opening PDF..."
	open $(PDF)

# Help target
help:
	@echo "Arctic Dam Risk Assessment Report - Makefile"
	@echo "Usage:"
	@echo "  make all      - Full compilation with bibliography"
	@echo "  make quick    - Quick compilation without bibliography"
	@echo "  make clean    - Remove auxiliary files"
	@echo "  make cleanall - Remove all generated files"
	@echo "  make view     - Open PDF (macOS)"
	@echo "  make check    - Check LaTeX installation"
	@echo "  make help     - Show this help"

.PHONY: all quick clean cleanall check view help 