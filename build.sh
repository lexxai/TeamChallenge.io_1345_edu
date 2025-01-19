#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install --upgrade pip -q  --no-input
pip install -r requirements.txt -q  --no-input
pip install gunicorn -q --no-input

#poetry install -n
#poetry install --with deploy -n

# Convert static asset files
pushd project_1345
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

#python manage.py runserver --insecure --noreload

popd > /dev/null

#python -m gunicorn --chdir ./project_1345 project_1345.wsgi:application