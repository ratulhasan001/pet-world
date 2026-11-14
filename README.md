# Pet World

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)

One of my early Django projects, built in 2024 while I was learning the framework.

Pet World is a small pet adoption web application. Users list pets for adoption, browse listings by category, and adopt a pet by paying its price from an account balance they top up with deposits. Accounts are activated by email, and only the user who adopted a pet can comment on it.

## What I practised

- Email-based account activation with Django's token generator
- Password reset with Django's built-in auth views
- Image uploads with `ImageField`
- Extending `User` with a profile model
- Function-based and class-based views, forms with django-crispy-forms
- Environment-based configuration

## Features

- **Registration with email activation**: sign-up collects contact number, address and an optional profile image. The account stays inactive until the user opens a token-based activation link sent by email.
- **Authentication**: login, logout, password change, and a "Forgot password" flow (Django's password reset views with email).
- **Pet listings**: logged-in users post pets with title, description, category, image and price. Owners edit and delete their own listings from their profile page.
- **Browsing**: the home page shows all pets with a category filter (`/category/<slug>/`) and a detail page for each pet.
- **Adoption**: logged-in users can adopt a pet posted by someone else if it is still available and their balance covers the price. Adopting marks the pet as adopted, records the adopter and deducts the price.
- **Deposits**: users add money to their balance. Each deposit is stored as a transaction.
- **Comments**: only the adopter of a pet can comment on it. The comment uses the adopter's name and email from their account.
- **Profile**: shows the user's details, the pets they adopted and the pets they listed.
- **Admin**: categories (slug auto-filled from the name), pets, profiles and transactions are managed in the Django admin.

## Tech stack

| | |
| --- | --- |
| Language | Python 3 |
| Framework | Django 4.2 |
| Database | Any database supported by `dj-database-url` (SQLite by default, PostgreSQL in deployment) |
| Configuration | django-environ |
| Forms | django-crispy-forms with crispy-bootstrap5 |
| Images | Pillow (`ImageField` for pet and profile images) |
| Email | Console output locally, SMTP (Gmail) when configured |
| Front end | Django templates, Bootstrap 5.3 (CDN), app-level CSS |

## Project structure

```
pet-world/
├── manage.py
├── requirements.txt
├── .env.example
├── pet_world/       # settings and root URLconf
├── user_profile/    # registration, activation, login, password reset, Profile model
├── posts/           # pet listings (Post), comments, adoption
├── category/        # Category model used for filtering
├── transactions/    # deposits
└── core/            # home page, base template and shared template snippets
```

## Getting started

```bash
git clone https://github.com/ratulhasan001/pet-world.git
cd pet-world

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/. No configuration file is needed: without one the app uses a local SQLite database (`db.sqlite3`) and prints emails to the terminal. When you register a user, the activation link appears in the terminal running `runserver`; open it to activate the account (or tick **Active** for the user in the admin). Add a few categories at `/admin/` before listing pets. Uploaded images are stored in `media/`.

### Configuration (optional)

Settings are read from environment variables or from `pet_world/.env` (next to `settings.py`). Copy `.env.example` as a starting point.

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django secret key. A development key is used when unset. |
| `DEBUG` | `True` by default. Set to `False` in production. |
| `DATABASE_URL` | Database connection string. Defaults to `sqlite:///db.sqlite3`. |
| `EMAIL`, `EMAIL_PASSWORD` | Gmail address and app password for SMTP. Without `EMAIL`, emails are printed to the console. |

## Running the tests

```bash
python manage.py test
```

The tests cover registration and email activation, login and logout, adoption (success, insufficient balance, adopting twice, adopting your own pet, login and POST requirements), comments, listing ownership, deposits and a smoke test of the main pages.

## Later improvements

After the original coursework I went back and fixed the following:

- Posting a comment no longer crashes on a redirect to a URL name that did not exist, and only the adopter can comment.
- Adopting a pet is POST-only and requires login, and the server now checks that the pet is available, that it is not your own pet and that your balance covers the price.
- Only the owner can edit or delete a listing, and deleting is POST-only.
- Deposits must be positive, and the deposit page requires login (`LoginRequiredMixin` now comes first in the class bases).
- Pages no longer crash for pets or profiles without an image.
- The activation link uses the request's scheme, so it works on `http://127.0.0.1:8000` locally.
- Logout is a POST form, which keeps it working on Django 5.
- The app runs locally with no `.env` (SQLite, console email), and the unused `django-taggit` dependency was removed.
- Small UI fixes: active navigation links, a footer, coloured messages, empty states, page titles and form error display.
- Added an automated test suite.

## Author

Ratul Hasan · [ratulhasan.dev](https://ratulhasan.dev)
