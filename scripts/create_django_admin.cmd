@echo off
echo Starting Django createsuperuser...
PUSHD "../project_1345"
poetry run python manage.py createsuperuser --username admin
POPD