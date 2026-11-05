# Personal Workspace

A shared Django platform with one account system and an app launcher. Finance Manager is the first available app, with household spending and budgeting. Habit Tracker and Daily Planner are listed as planned apps. All apps share the authenticated workspace; each app keeps its own routes, data models, and features. The launcher is the natural entry point for adding future apps.

Finance Manager supports flexible groups with any number of members, and attributes each transaction to the member who entered it.

## Requirements

- Python 3.10 or newer
- Django 4.2 or newer (`requirements.txt` pins the supported major range)

## Setup

```sh
cd finance_manager
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # optional, for the Django admin
python manage.py runserver
```

Open <http://127.0.0.1:8000/> to sign in or create an account. After authentication, users land on the shared app launcher and choose Finance Manager. The first visit to Finance Manager lets a user create a household or join with an invite code. The creator can share that code from the Finance overview screen. Habit Tracker and Daily Planner are currently launcher placeholders. The default database is local SQLite at `db.sqlite3`.

## Usage

- **Household Groups:** view every household you belong to, see all member names and invite codes, and switch the active group. You can create a new household or join another one without losing access to your existing groups.
- **Transactions:** add an amount, category, description, date, debit source (UPI, credit card, debit account, or cash/other), bank (SBI, Axis, HSBC, HDFC, ICICI, Kotak, or other), necessity response, and optional comment. Bank is optional for cash or other entries. Household members can view, edit, and delete household transactions.
- **Categories:** add, rename, recolor, or remove categories. Categories containing transactions are protected from deletion until the linked transactions are removed.
- **Goals:** set one monthly amount per category. Dates are normalized to the first day of the month.
- **Overview:** review current-month group spending, category progress, member count, and recent transactions/comments.
- **Analytics:** compare spending with monthly goals across the last six months.

All household data is scoped to the currently selected household, and the active selection is checked against the signed-in user’s memberships. Finance Manager routes are under `/finance/`. The shared launcher is `/`; Django’s built-in login/logout pages are `/accounts/login/` and `/accounts/logout/`, and account creation is at `/signup/`. A future app should be added as its own Django app, route namespace, and launcher card, while using the existing Django user and authentication system.

## Configuration and deployment

Set `DJANGO_SECRET_KEY` to a strong random value, `DJANGO_DEBUG=false`, and `DJANGO_ALLOWED_HOSTS` to a comma-separated host list in production. Use a production database and HTTPS. Configure secure cookies, logging, static file collection/storage, backups, and a production WSGI/ASGI server as appropriate. Never commit secrets or production database files. Run `python manage.py check --deploy` against deployment settings before release.

## Tests and maintenance

The app includes model and request-level tests for transaction attribution, goal setup, authentication, app launcher access, member creation, and household data isolation. Run them with:

```sh
python manage.py test finance
```

Generate and apply schema migrations after model changes:

```sh
python manage.py makemigrations finance
python manage.py migrate
```

Back up the database before upgrades. Review Django release notes and dependency updates regularly.
