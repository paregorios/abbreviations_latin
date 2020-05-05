#! /bin/bash


rsync -rav --delete --exclude 'scripts' --exclude 'requirements.txt' --exclude '*.bak' ./* paregorios.org:/var/www/html/pa/paregorios.org/resources/abbrev/
# rsync -rav ./docs/.htaccess paregorios.org:/var/www/html/pa/paregorios.org/resources/roman-emperors/
