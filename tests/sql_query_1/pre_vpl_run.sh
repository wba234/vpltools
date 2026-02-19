python3 -m vpltoolsfor file in "key_all_owners.sql"
do
if [ -f "$file" ]; then
    mv "$file" "$file.save"
    echo "Success."
fi
done
