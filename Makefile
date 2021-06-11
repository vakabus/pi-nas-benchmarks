readme.pdf: results README.md
	pandoc -f markdown+smart -o readme.pdf README.md

results: $(wildcard data/*)
	poetry install
	poetry run python plot.py
	poetry run python plot_bs.py

clean:
	-rm -r results
	-rm readme.pdf