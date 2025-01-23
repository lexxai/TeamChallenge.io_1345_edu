@echo off
PUSHD "../project_1345"
echo .
echo Starting Django collectstatic...
poetry run python manage.py collectstatic --noinput
POPD
