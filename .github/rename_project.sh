#!/usr/bin/env bash
while getopts a:n:u:d: flag
do
    case "${flag}" in
        a) author=${OPTARG};;
        n) name=${OPTARG};;
        u) urlname=${OPTARG};;
        d) description=${OPTARG};;
    esac
done

echo "Author: $author";
echo "Project Name: $name";
echo "Project URL name: $urlname";
echo "Description: $description";

echo "Renaming project..."

original_author="sm4rtm4art"
original_name="fast_api_template"
original_urlname="FAST_API_TEMPLATE"
original_description="Awesome fast_api_template created by sm4rtm4art"
# for filename in $(find . -name "*.*")
for filename in $(git ls-files)
do
    sed -i "s/$original_author/$author/gI" $filename
    sed -i "s/$original_name/$name/gI" $filename
    sed -i "s/$original_urlname/$urlname/gI" $filename
    sed -i "s/$original_description/$description/gI" $filename
    echo "Renamed $filename"
done

mv fast_api_template $name

# This command runs only once on GHA!
rm -rf .github/template.yml
