all:
	@$(MAKE) install
	@$(MAKE) build
	@echo "Build successful."

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

build:
	@echo "Building the app..."
	python setup.py py2app