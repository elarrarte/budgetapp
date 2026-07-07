#!/bin/bash
cd /home/elarrarte/git/personal/budgetapp
exec nohup venv/bin/python manage.py runserver 0.0.0.0:8000 &>/tmp/django_budget.log &
