# AskTA · Teaching Assistant Support System

A Django system where students open questions about their subjects and monitors (teaching assistants) answer them. Answered questions feed a knowledge base that every user can search.

Built for the extra-credit activity of **Rapid Application Development (RAD)**, *Tecnólogo em Sistemas para Internet*, IFPB.

## Team

| Name | GitHub |
|---|---|
| Suetone Carneiro de Andrade Neto | [@SuetoneCarneiro](https://github.com/SuetoneCarneiro) |
| Pedro Lucas Silva Batista | [@pedrolucasi](https://github.com/pedrolucasi) |

## Test accounts

**All accounts use the same password: `Monitoria@2026`**

| # | Username | Role | Use it to check |
|---|---|---|---|
| 1 | `admin` | Superuser | The Admin panel (`/admin/`) only. It passes every permission check, so it proves nothing about authorization |
| 2 | `student_ana` | Student | Opening questions and closing her answered ones |
| 3 | `student_bruno` | Student | He does **not** see Ana's questions |
| 4 | `monitor_carla` | Student + monitor of **RAD101 only** | She sees RAD101 questions and does **not** see WEB201 ones |
| 5 | `professor_diego` | Professor | He sees every question |
| — | `monitor_extra` | Student + monitor of WEB201 | Helper account: gives WEB201 its own monitor and an answered question |

## Subjects and monitors

| Code | Name | Active | Monitors |
|---|---|---|---|
| `RAD101` | Rapid Application Development | Yes | `monitor_carla` |
| `WEB201` | Web Programming | Yes | `monitor_extra` |
| `DB301` | Databases | **No** (used to check that inactive subjects reject new questions) | — |

The database ships with questions in every status, so each requirement can be checked right away:

| Question | Subject | Author | Status | Monitor |
|---|---|---|---|---|
| How do I use related_name? | RAD101 | ana | Open | — |
| Why does my migration fail? | RAD101 | bruno | In progress | carla |
| LoginRequiredMixin vs @login_required | RAD101 | ana | Answered | carla |
| What is a QuerySet? | RAD101 | bruno | Closed | carla |
| Flexbox vs Grid? | WEB201 | ana | Open | — |
| What does CSRF protect? | WEB201 | bruno | Answered | monitor_extra |

## Requirements status

| Requirement | Status |
|---|---|
| RF1: Models, migrations and Admin | Done |
| RF2: Login, logout and public signup | Done |
| RF3: Open a question | Done |
| RF4: The three list views | Done |
| RF5: Claim a question | Done |
| RF6: Answer | Done |
| RF7: Close | Done |
| RF8: Knowledge base | Done |
| RF9: The interface reflects the role | Done |
| Optional challenge: office hours | Done |

**Unfinished requirements:** none.

## How to run

The repository includes `db.sqlite3` with all test data, so there's no need to run `migrate`.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

Open <http://127.0.0.1:8000> and log in with one of the accounts above.

To rebuild the database from scratch:

```bash
rm db.sqlite3
python manage.py migrate
python manage.py seed_demo
```

## Main pages

| URL | Page | Who can access |
|---|---|---|
| `/questions/` | Question list (RF4) | Any logged-in user. The result set depends on the role |
| `/questions/new/` | Open a question (RF3) | Any logged-in user |
| `/questions/<id>/` | Question detail with the actions (RF5–RF7, RF9) | Author, monitors of the subject, professors. Answered/closed questions are readable by everyone |
| `/questions/knowledge/` | Knowledge base with search (RF8) | Any logged-in user |
| `/schedules/` | My office hours: list and add slots (optional challenge) | Monitors only. Everyone else gets 403 |
| `/accounts/signup/` | Public signup (RF2) | Anyone |
| `/admin/` | Django Admin (RF1) | Staff |

## Design decisions

### Roles

- **Student:** Django group `Students`. The signup view adds every new account to it, and gives it no other permission. `is_staff` stays `False`.
- **Professor:** Django group `Professors`, which holds the custom permission `questions.view_all_questions`. The list checks this permission, not the group name.
- **Monitor:** not a group. A user is a monitor **of a subject** when they appear in `Subject.monitors` (a many-to-many field, editable in the Admin). Monitoring is per subject, so the role comes straight from the data and can never get out of sync.

`is_superuser` is never used as an authorization criterion.

### The three list views (RF4)

All three come from the same page and the same method, `Question.objects.visible_to(user)`:

| Role | Query |
|---|---|
| Professor | `Question.objects.all()` |
| Student / Monitor | `Question.objects.filter(Q(author=user) \| Q(subject__monitors=user)).distinct()` |

For a monitor, `subject__monitors=user` crosses the relationship Question → Subject → monitors inside **one SQL query** (an `INNER JOIN` with the subject and a `LEFT JOIN` with the subject–monitor table). No subject names or ids are written in the code. `distinct()` removes the duplicate rows the many-to-many join creates when a subject has more than one monitor.

**Decision:** a monitor also sees the questions they opened themselves. A monitor is usually a student too, and any logged-in user can open a question (RF3). Without `Q(author=user)`, a monitor's own questions in other subjects would disappear from their list. It's still a single query, and a student's view is unchanged.

### HTTP method for claim, answer and close (RF5 report)

The three actions **only accept POST**, because they change the state of the system:

- GET must be *safe* and *idempotent*. Browsers prefetch links, crawlers follow them, and a GET link can be triggered from another site (for example inside an `<img>`). A state change behind a GET could happen without the user meaning it.
- POST requests go through Django's **CSRF protection**, so another site can't forge the action with the user's session.

Every action checks **who** is asking before it checks the method. Someone without permission gets **403 Access denied** even when they just type the URL. The right person using GET gets **405 Method Not Allowed**.

### Server-side protection (hiding a button is not protecting a route)

The rules live in the `Question` model (`can_be_claimed_by`, `can_be_answered_by`, `can_be_closed_by`). The views use them to protect the routes, and the detail template uses them to show or hide the buttons (RF9), so the interface and the server can never disagree.

| Action | Wrong person | Wrong state |
|---|---|---|
| Claim | Not a monitor of the subject → 403 | Not Open, or already claimed → error message |
| Answer | Not the assigned monitor → 403 | Closed, or blank answer → error message |
| Close | Not the author → 403 | No answer yet, or already closed → error message |

- **Decorator protection:** `@login_required` on `claim_question`, `close_question` and `knowledge_base`.
- **Mixin protection:** `LoginRequiredMixin` on the list, create and detail views, plus `UserPassesTestMixin` on `AnswerView`.
- **Status is never a form field.** It only changes inside the claim, answer and close views. The author is never a form field either: the create view sets it to the logged-in user.
- **Two monitors can't claim the same question.** The claim is a conditional update (`UPDATE ... WHERE status = 'open' AND assigned_monitor IS NULL`). The database applies it atomically, so the second monitor updates zero rows and gets an error message.
- **Inactive subjects:** the subject field's queryset only contains active subjects. A forged POST with an inactive subject's id fails validation on the server, not just in the dropdown.
- **A closed question accepts no changes:** every `can_*` rule returns `False` for it.

### Models

- `Question` has **two foreign keys to `User`** (`author` and `assigned_monitor`), so each one has its own `related_name` (`questions_asked`, `questions_assigned`). Otherwise both reverse accessors would be called `question_set` and clash.
- `on_delete` choices:
  - `subject` → `PROTECT`: a subject with questions is deactivated (`is_active = False`), never deleted, so the question history survives.
  - `author` → `CASCADE`: a question belongs to the person who asked it.
  - `assigned_monitor` → `SET_NULL`: if a monitor account is removed, the question stays.
- `created_at` (`auto_now_add`) and `updated_at` (`auto_now`) record when a question was opened and last changed.

### Passwords

No password is ever assigned to the model field. Users are created with `create_user` / `create_superuser` (in `seed_demo`) or with Django's `UserCreationForm` (signup), which all hash the password with `set_password`. Signup keeps Django's default password validators, so weak passwords are rejected with a message.

### Test data

The `seed_demo` management command builds the groups, permissions, accounts, subjects, monitor links and questions above. It's safe to run more than once. We used it so both of us had identical local databases while developing, and so `db.sqlite3` only had to be committed once, at the end. All of this data can also be viewed and edited in the Admin.

### Optional challenge: office hours

Monitors register weekly slots when they are available (`schedules` app, model `OfficeHour`: monitor, subject, weekday, start and end time). It lives in its own app, with its own migrations.

- **Where:** `/schedules/` (link "Office hours" in the menu, shown only to monitors). The page lists the monitor's slots and has a form to add one. `LoginRequiredMixin` + `UserPassesTestMixin` (`user.monitored_subjects.exists()`): anyone who isn't a monitor gets 403.
- **Rules, in `OfficeHour.clean()`** (so the form and the Admin both enforce them):
  1. The end time must be after the start time.
  2. A monitor can only add slots for subjects they monitor. The form's dropdown already lists only those subjects, and `clean()` checks again, so a forged POST fails too.
  3. **No overlapping slots** for the same monitor on the same day. This is a database query: two slots overlap when each one starts before the other ends,
     `OfficeHour.objects.filter(monitor=..., weekday=..., start_time__lt=new_end, end_time__gt=new_start).exclude(pk=self.pk).exists()`.
     Touching slots (09:00–10:00 and 10:00–11:00) are allowed. The view sets `monitor = request.user` **before** validation, so `clean()` can run this query.
- **Question page:** when a student picks a subject on `/questions/new/`, a card shows that subject's office hours. A few lines of plain JavaScript switch the card when the dropdown changes, without reloading (so nothing typed is lost). Without JavaScript, `?subject=<id>` shows the same card.
- **Test data:** `monitor_carla` has two slots in RAD101 (Monday 09:00–10:00, Wednesday 14:00–16:00).
- **Automated tests:** `python manage.py test schedules` covers overlap, adjacent slots, own subjects only, the 403 for non-monitors and the card on the question page.

### Why `db.sqlite3` is in the repository

Only for this delivery: without the subjects, the monitor links and questions in different statuses, the requirements can't be checked. In a real project the database stays out of version control. The `.venv` folder is never committed.

### No third-party libraries

`requirements.txt` only contains Django and its own dependencies. The interface is a hand-written CSS design system (`static/css/app.css`) with light and dark mode, and uses no CSS framework, CDN or web font.

## Project structure

```
config/            project settings and root URLs
accounts/          signup view and role (group) names
questions/
  models.py        Subject, Question, visibility queries and business rules
  admin.py         Admin configuration (RF1)
  forms.py         QuestionForm (RF3), AnswerForm (RF6)
  views/           one module per feature: listing, create, detail, actions, knowledge
  management/      seed_demo command
schedules/         optional challenge: OfficeHour model, rules, page and tests
templates/         base layout, auth pages and question pages
static/css/app.css design system
```
