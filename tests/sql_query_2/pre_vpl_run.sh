python3 -m vpltoolsfor file in "key_max_developer_grades.sql"
do
if [ -f "$file" ]; then
    mv "$file" "$file.save"
    echo "Success."
fi
done
