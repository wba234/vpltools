#!/usr/bin/env bash

# Get the directory in which the present script is located.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Source - https://stackoverflow.com/a/246128
# Posted by dogbane, modified by community. See post 'Timeline' for change history
# Retrieved 2026-02-24, License - CC BY-SA 4.0

echo "$SCRIPT_DIR"
python3 -m vpltools "$SCRIPT_DIR" &> /dev/null
for file in "key_all_owners.sql"
do
if [ -f "$file" ]; then
    mv "$file" "$file.save"
    echo "Success."
fi
done
