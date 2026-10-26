# PaPrint — Django Print Job Management

PaPrint is a Django + SQLite print-shop application with staff-only order management,
Django Admin, administrator-configured prices, live summary counts, and sales reports.

## Run locally

This repository's Pipfile targets Python 3.14. Use a compatible Python version and install
the dependencies in your virtual environment:


~~~bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
~~~

Visit http://127.0.0.1:8000/login/ and sign in with your superuser account.
The Django Admin lives at http://127.0.0.1:8000/admin/.

## What changed

- **Django Admin:** Manage print jobs and Pricing Rules; search, filter and bulk-complete jobs.
- **Staff authentication:** Only active users with the *Staff status* flag can enter
  the order dashboard and reports. Staff accounts and group permissions can be
  configured from Django Admin. Only grant the model permissions staff really need.
- **Automatic pricing:** On create/edit, Django calculates quantity × configured rate.
  Browser-submitted prices are ignored. A fresh migration seeds example prices for
  Document, Photo and Tarpaulin across six sizes and two color modes.
  **Example rates are placeholders.** Review and change them in Django Admin
  before using PaPrint for real customers.
- **Order workflow:** Pending, Processing, Ready, Completed and Cancelled. The
  dashboard shows real counts instead of a decorative progress timeline.
- **Reporting:** Last six calendar months' completed-order revenue, order counts,
  and a downloadable CSV. Revenue deliberately excludes uncompleted orders.
- **Security:** Local development is enabled by default. For deployment, set
  DJANGO_DEBUG=false, DJANGO_SECRET_KEY to a unique long random secret,
  and DJANGO_ALLOWED_HOSTS to your real hostname(s). Do not deploy using
  the development fallback key.

## Administrator and staff workflow

1. Create a superuser using the command above and open **Django Admin**.
2. Select **Pricing Rules** and edit the default example rates.
3. To create staff accounts, use **Users** → Add user, set a password and
   **Staff status**. Set limited permissions; do not grant Superuser status to
   ordinary staff.
4. Use the **Dashboard** → **+ New Job** to record an order. Its price is
   calculated by Django using the rule for type, size and color mode.
5. Use **Edit** to update a job, **Reports** to view completed revenue,
   or **Django Admin** to manage orders in bulk.

Existing orders and their previously stored totals are retained by the migration.
Changing a pricing rule affects new and edited orders, not historical totals
until an order's specifications are edited. Legacy orders with no matching
rate can still have their status updated while keeping the old total.

## Tests


~~~bash
python manage.py test IMS_App
python manage.py check
python manage.py makemigrations --check --dry-run
~~~

## Important local-data note

The repository already tracks db.sqlite3 and may contain historical local data.
Do not commit live customer data or passwords. New deployments should use their own
database and keep secrets, backups and environment files outside version control.
