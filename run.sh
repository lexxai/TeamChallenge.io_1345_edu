#!/usr/bin/env bash
# Exit on error
set -o errexit

pushd project_1345

python manage.py runserver --insecure --noreload --port 8000 --host 0.0.0.0

popd > /dev/null

#python -m gunicorn --chdir ./project_1345 project_1345.wsgi:application