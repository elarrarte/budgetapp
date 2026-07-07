#!/bin/bash
cd /home/elarrarte/git/personal/budgetapp
exec venv/bin/python manage.py runserver 0.0.0.0:8000
