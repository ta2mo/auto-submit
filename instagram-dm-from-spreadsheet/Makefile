build: clean
	pyinstaller --onefile main.py

package-mac: build
	mkdir -p instagram-dm/csv
	mkdir -p instagram-dm/driver
	cp dist/main instagram-dm/main
	cp driver/mac/chromedriver-89 instagram-dm/driver/
	cp README.md instagram-dm/
	zip -r instagram-dm-mac.zip instagram-dm
	rm -rf instagram-dm

clean:
	@rm -rf build
	@rm -rf dist
	@rm -rf main.spec
	@rm -rf instagram-dm.zip
	@rm -rf instagram-dm
