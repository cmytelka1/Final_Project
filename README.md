# Flask-Submit
### Video Demo:  <[YouTube](https://www.youtube.com/watch?v=sWkgqlztY9s)>
### Description:

This Flask-based web application allows prospective authors of a peer-review journal to submit their manuscript(s) for publication consideration. The system supports user authentication, manuscript submission, and database management for manuscripts and their associated decisions.

The project requires Python to be installed, along with the following dependencies:
* `flask`
* `flask-session`
* `flask-alembic`
* `flask_sqlalchemy`
* `sqlalchemy`

The inspiration for this project came from my previous job, where I worked on a similar (although much more complex) version of a manuscript tracking SaaS product. In that role I worked with developers and clients to enhance the software, fix bugs, and make configuration changes, so after taking CS50 I wanted to try my hand at creating a full-stack version of the product. My project has the following directory structure:

- `app.py` --------------------- # Main Flask application
- `templates/` ---------------- # HTML templates with Jinja logic, Bootstrap, and JS
- `static/` -------------------- # Static files (CSS, favicons)
- `tmp/user_files/` ----------- # Uploaded manuscript files
- `migrations/` ---------------- # Record of Alembic migrations
- `tables.py` ----------------- # SQLAlchemy database models
- `helpers.py`  ---------------- # Utility functions
- `database.db` --------------- # SQLite database (generated after running `create-db`)

### `app.py` 
Contains the main logic for the web app, with configuration settings, view functions, and setup instructions. The configurations connect the app to a SQLite database, allow for the creation of user sessions, set the upload path for user files, and ensure responses are not cached. After initializing the app Alembic is incorporated for database migrations, and commands are listed to create and drop all tables in the database.

When a user lands on the site's main page, they are instructed to enter their login information or Register for a new account. Clicking the "Register" link in the navbar takes them to the '/register' route, where they can input user information. Clicking the "Register" button sends a request to the database to insert a new row into the Person table, with the user's role auto-assigned as "Author".

The user can now login by sending a GET request to the '/login' route. Any open Flask session is cleared, and when the user sends a POST request when clicking the "Log In" button, server-side validation is executed to ensure that the username and password fields were filled in and match exactly one record in the Person table. A Flask session is then created, storing a user-specific encrypted cookie consisting of login status that persists as the user navigates through the website. Finally, the user is redirected to their home dashboard.

If the user's role is "Author", they land on an author-specific version of the dashboad, with two available links. "Submit Manuscript" sends a GET request to the '/submit' route, and the submission form template is generated. The author must complete all required fields, which include Title, Abstract, Keywords, Email Address, and Manuscript Text file. The author's name is auto-pulled from the Person table and is uneditable. The form is structured in an accordian-style layout using Bootstrap JS and CSS and a JS function I wrote. When the form is submitted, client-side validation occurs, a POST request is sent, and successful server-side validation results in database insertions into the Manuscript and Keywords tables. A manuscript name is generated according to a utility function, and the manuscript file is uploaded and stored in the `tmp/user_files` directory under the generated folder for that manuscript. The author can check the status of any manuscripts they have submitted by clicking the "Check Manuscript Status" link, where they will find a list of manuscript names and associated statuses.

If the user's role is "Editor" (assigned manually through the database), their task is to "Review Manuscripts". On clicking this link, the Editor is taken to the "/review" route that lists anchors for any and all manuscripts awaiting decision. Clicking an anchor calls the `show_ms` function, and the mansucript title, abstract, and keywords are displayed. There is also a button that downloads the associated manuscript file. The Editor can make their decision by clicking "Accept Manuscript" or "Reject Manuscript", which results in the appropriate values being inserted into the Decisions table, and the status updated in the Manuscript table. This update is visible to the author upon checking the manuscript status.

When the user logs out, their session is cleared.

### `tables.py` 
Contains SQLAlchemy Core database models for 4 tables: Person, Manuscript, Keywords, and Decision. Column names are specified, along with their datatype, primary key status (if applicable), and foreign key status (if applicable). The Manuscript.submission_date column defaults to the current DateTime on submission.

### `helpers.py`
Contains Python functions that are called in `app.py`. `login_required` is a decorator used on view functions to require user login in order to access the respective URL routes. `db_execute` makes the connection to the database when a SQLAlchemy statement is processed, returning a dictionary result if the SQL is a Select statement and not returning anything if an Insert or Update statement. `name_sequence` keeps track of the next number used for the Manuscript.ms_name that is auto-assigned to each submission. Because SQLite is not compatible with SQLAlchemy's Sequence object, I needed to do this manually, via file creation so that the current value would be saved in disk memory and not refreshed.

### Final Points
I chose to use SQLAlchemy Core instead of CS50's built-in SQL functionality because I wanted to challenge myself by learning new software and syntax. However, I did run into some compatability issues, not just with the aforementioned Sequence object but also with Flask-Alembic. SQLite can handle some Alembic operations, but it cannot handle certain ALTER statements. For this reason, whenever I made changes to `tables.py` I ran the `drop-db` and `create-db` commands to update the database. It would be wise to move over to MySQL or PostgreSQL if development is to continue. Also, a production-ready app would require more security features, including password hashing and file validation.