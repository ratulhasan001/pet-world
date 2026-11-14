# Pet World

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)

Pet World is a pet adoption web application built with Django. Users list pets for adoption, browse listings by category, and adopt a pet by paying its price from an account balance they top up with deposits. Accounts are activated by email, and only users who adopted a pet can comment on it. The project demonstrates email-based account activation with Django's token generator, password reset with Django's built-in auth views, image uploads, extending `User` with a profile model, and environment-based configuration.

## Features

- **Registration with email activation**: sign-up collects contact number, address and an optional profile image. The account stays inactive until the user clicks a token-based activation link sent by email.
- **Authentication**: login, logout, password change, and a "Forgot password" flow (Django's password reset views with email)
- **Pet listings**: logged-in users post pets with title, description, category, image and price. Users edit and delete their listings from their profile page.
- **Browsing**: the home page shows all pets with a category sidebar filter (`/category/<slug>/`) and a detail page for each pet
- **Adoption**: logged-in users can adopt a pet posted by someone else if it is still available and their balance covers the price. Adopting marks the pet unavailable, records the adopter and deducts the price. The button shows "Insufficient Balance" or "Unavailable" otherwise.
- **Deposits**: users add money to their balance. Each deposit is stored as a transaction.
- **Comments**: only users who adopted a pet can comment on it
- **Profile**: shows the user's details, the pets they adopted and the pets they listed
- **Admin**: categories (slug auto-filled from the name), pets, profiles and transactions are managed in the Django admin

## Tech stack

| | |
| --- | --- |
| Language | Python 3 |
| Framework | Django 4.2 |
| Database | Any database supported by `dj-database-url` (PostgreSQL in deployment, SQLite works locally) |
| Configuration | django-environ |
| Forms | django-crispy-forms with crispy-bootstrap5 |
| Images | Pillow (`ImageField` for pet and profile images) |
| Email | SMTP (Gmail) |
| Front end | Django templates, Bootstrap 5.3 (CDN), app-level CSS |

## Project structure

```
pet-world/
├── manage.py
├── requirements.txt
├── pet_world/       # settings and root URLconf
├── user_profile/    # registration, activation, login, password reset, Profile model
├── posts/           # pet listings (Post), comments, adoption
├── category/        # Category model used for filtering
├── transactions/    # deposits
└── core/            # home page and base template
```

## Getting started

```bash
git clone https://github.com/ratulhasan001/pet-world.git
cd pet-world

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a file `pet_world/.env` (in the same folder as `settings.py`) with these variables. You can also export them in your shell.

```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
EMAIL=your-address@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
```

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | Database connection string. Use `sqlite:///db.sqlite3` for local development. |
| `EMAIL` | SMTP username (Gmail address) used for activation and password reset emails |
| `EMAIL_PASSWORD` | SMTP password (a Gmail app password) |

Then set up the database and start the server:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/. Add categories in the admin at `/admin/`. Register normal users through the site, since adopting and depositing need a user profile. Registration sends an activation email, so it needs valid SMTP credentials. You can also activate a user in the admin by ticking **Active**.

## Author

Ratul Hasan · [ratulhasan.dev](https://ratulhasan.dev)
