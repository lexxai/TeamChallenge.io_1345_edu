@echo off
echo ""
echo  "Starting Django makemigrations..."
PUSHD "../project_1345"
poetry run python manage.py makemigrations
POPD