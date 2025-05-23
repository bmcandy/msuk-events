#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define directories & variables
DATA_DIR="./data"
HUGO_DIR="./hugo_site"
OUTPUT_DIR="./public"
HUGO_VERSION="0.147.0"  # Specify the Hugo version you want to install

# delete the content and public directories if they exist
if [ -d "$HUGO_DIR/content" ]; then
    echo "Deleting existing content directory..."
    rm -rf "$HUGO_DIR/content"
fi
if [ -d "$HUGO_DIR/$OUTPUT_DIR" ]; then
    echo "Deleting existing public directory..."
    rm -rf "$HUGO_DIR/$OUTPUT_DIR"
fi
# mkdir command to create directories if they do not exist
mkdir -p "$DATA_DIR"
mkdir -p "$HUGO_DIR"
mkdir -p "$HUGO_DIR"/content
mkdir -p "$HUGO_DIR"/content/info

# copy info to content directory
cp -r ./info/* "$HUGO_DIR/content/info"

# Check if Hugo is installed
if ! command -v hugo &> /dev/null
then
    echo "Hugo could not be found. Installing Hugo."
    wget -O ./hugo.deb https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-arm64.deb
    sudo dpkg -i ./hugo.deb
    rm ./hugo.deb
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 could not be found. Please install Python 3 to proceed."
    exit 1
fi

echo "Scraping Motorsport UK events database..."
python3 scrape_events.py --output "$DATA_DIR/events.json"
if [ $? -ne 0 ]; then
    echo "Error: Scraping failed. Please check the scrape_events.py script."
    exit 1
fi

# Process the scraped data
echo "Processing scraped data..."
python3 process_events.py --input "$DATA_DIR/events.json" --output "$HUGO_DIR/content"

# check if hextra theme is installed by looking for hextra in hugo mod graph output
cd $HUGO_DIR
if ! hugo mod graph | grep -q "github.com/imfing/hextra"; then
    echo "Hugo theme not found. Checking repo already cloned..."
    # Check if the theme repository already exists
    if [ -d "hextra-starter-template" ]; then
        echo "Deleting hextra theme..."
        rm -rf "./hextra-starter-template"
    fi
    # Install the hextra theme
    git clone https://github.com/imfing/hextra-starter-template.git
    cp ./hextra-starter-template/go.mod "./go.mod"
    cp ./hextra-starter-template/go.sum "./go.sum"
    hugo mod tidy
    rm -rf "./hextra-starter-template"
    if ! hugo mod graph | grep -q "github.com/imfing/hextra"; then
        echo "Error: Hextra theme installation failed. Please check the installation process."
        exit 1
    fi
    echo "Hextra theme installed successfully."
fi
cd ..

# Generate the static website using Hugo
echo "Generating static website with Hugo..."
hugo -s "$HUGO_DIR" -d "$OUTPUT_DIR"

# Notify the user
echo "Static website generated successfully in $OUTPUT_DIR."
