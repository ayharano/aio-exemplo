BASE_NAME = 20180118_grupy_sp_aio_exemplo

XELaTeX  = xelatex
BibTeX   = bibtex

pdf: $(BASE_NAME).pdf

$(BASE_NAME).pdf: $(BASE_NAME).tex 
	$(XELaTeX) $<
	$(BibTeX) $(BASE_NAME) 
	$(XELaTeX) $< 
	$(XELaTeX) $<
	$(XELaTeX) $<
	cp $(BASE_NAME).pdf _tmp.$(BASE_NAME).pdf
	make clean
	mv _tmp.$(BASE_NAME).pdf $(BASE_NAME).pdf

clean:
	rm -f $(BASE_NAME)*.{aux,bbl,blg,log,nav,out,pdf,snm,toc,vrb}
