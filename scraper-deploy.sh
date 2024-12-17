#!/bin/bash

# Define variables
SOURCE_DIR="/Users/cmdnotfound/Development/ji/tools/webscrub/"
DEST_DIR="ji@192.168.1.200:/mnt/user/websites/swfl.io/scripts/webscrub"

# Copy contents using scp
scp -r "$SOURCE_DIR"/* "$DEST_DIR"

# Optional: Verify the transfer
if [ $? -eq 0 ]; then
    echo "Transfer completed successfully."
else
    echo "Transfer failed."
fi


# To run use: ./scraper-deploy.sh