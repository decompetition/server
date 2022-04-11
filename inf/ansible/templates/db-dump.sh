#! /bin/bash

dir="/var/dbdump"
now="$(date +\%Y\%m\%d-\%H\%M)"

# Dump the current database:
pg_dump "{{sql_database}}" | gzip > "$dir/$now.sql.gz"

# Delete hourly backups older than one day:
find "$dir" -mtime +1 ! -name '*-0000.sql.gz' -delete

# Delete daily backups older than one month:
find "$dir" -mtime +31 ! -name '*01-0000.sql.gz' -delete

# Delete all backups older than one year:
find "$dir" -mtime +366 -delete
