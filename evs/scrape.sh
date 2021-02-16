#!/bin/bash

curl -s 'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_effort_value_yield_(Generation_IV)' | \
grep '\(<td align="left"> <a href="/wiki/\)\|\(<td.*[0-9]$\)' | \
sed 's/<\/a>//' | \
sed 's/<small>(//' | \
sed 's/)<\/small>//' | \
sed 's/.*> \?//' | \
tr '\n' ',' | \
sed 's/,$//' | \
sed 's/,\([A-Z]\)/\n\1/g' >ev_table.csv
