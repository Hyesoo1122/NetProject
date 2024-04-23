"""
first_stage.py

Author: Evie Hyesoo Kwon [z5355075]

Date: 14 March, 2024

This file contains the code used for the first stage implementation of your
proposal. You should modify it so that it contains all the code required for
your MVP.
"""
# Import the required dependencies for making a web app
import json
from flask import Flask, redirect, render_template, url_for, request, session
import pyhtml as h

app = Flask(__name__)
app.secret_key = 'your_secret_key'

PROJECTS_FILE = 'projects.json'
USERS_FILE = 'users.json'

# Function to load projects from JSON file
def load_projects():
    try:
        with open(PROJECTS_FILE, 'r') as file:
            projects = json.load(file)
    except FileNotFoundError:
        projects = []

    for index, project in enumerate(projects):
        project['id'] = index
        project.setdefault('view_count', 0)
    return projects

# Function to save projects to JSON file
def save_projects(projects):
    with open(PROJECTS_FILE, 'w') as file:
        json.dump(projects, file)

# Function to load users from JSON file
def load_users():
    try:
        with open(USERS_FILE, 'r') as file:
            users = json.load(file)
    except FileNotFoundError:
        users = {}
    return users

# Function to save users to JSON file
def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file)

def generate_top_bar():
    if 'user_email' in session:
        # If user is logged in, display logout button
        return h.div(id='header')(
            h.a("NETPROJECT", href='/'),
            h.div(style="flex-grow: 1;"),
            h.form(method="get", action="/create_project")(
                h.button("Create", id="Create", class_="custom-button", content="Create")
            ),
            h.div(class_="dropdown")(
                h.button(class_="dropbtn")(
                    h.img(src="/static/netproject.png", alt="More Options", class_="dropbtn_icon")
                ),
                h.div(class_="dropdown-content", id="dropdown-content")(
                    h.a("Saved Post", href="/saved_post"),
                    h.a("Apply Post", href="/apply_post"),
                    h.a("Logout", href="/logout")
                )
            )
        )
    else:
        # If user is not logged in, display login button
        return h.div(id='header')(
            h.a("NETPROJECT", href='/'),
            h.div(style="flex-grow: 1;"),
            h.form(method="get", action="/create_project")(
                h.button("Create", id="Create", class_="custom-button", content="Create")
            ),
            h.form(method="get", action="/login")(
                h.button("Login", id="Login", class_="custom-button", content="Login")
            )
        )
@app.route('/saved_post', methods=['GET'])
def saved_post():
    if 'user_email' in session:
        # Load user data from JSON file
        users = load_users()
        user_email = session['user_email']
        saved_projects = users.get(user_email, {}).get('saved_projects', [])
        projects = load_projects()
        saved_project_list = [projects[project_id] for project_id in saved_projects]

        # Generate HTML for each saved project
        saved_project_cards = []
        for project in saved_project_list:
            card_link = url_for('project_detail', project_id=project['id'])
            card = h.div(class_='card')(
                h.a(href=card_link)(
                    h.h5(f"{project['recruitments_category']}"),
                    h.p(f"Deadline: {project['recruitment_deadline']}"),
                    h.h2(project['title'])
                )
            )
            saved_project_cards.append(card)

        # Combine all saved project cards into a single HTML string
        saved_project_cards_html = h.div(class_='card-container')(*saved_project_cards)

        # Generate the entire HTML response
        response = h.html(
            h.head(
                h.title("Saved Posts"),
                h.link(rel="stylesheet", href="/static/net.css")
            ),
            h.body(
                generate_top_bar(),
                h.hr(),
                h.br(),
                h.h3("Saved Posts"),
                saved_project_cards_html
            )
        )

        return str(response)
    else:
        return redirect(url_for('login'))


@app.route('/apply_post', methods=['GET'])
def apply_post():
    if 'user_email' in session:
        # Load user data from JSON file
        users = load_users()
        user_email = session['user_email']
        projects = load_projects()

        # Find projects that the current user has applied to
        applied_project_list = []
        for project in projects:
            if user_email in project.get('applicants', []):
                applied_project_list.append(project)

        # Generate HTML for each applied project
        applied_project_cards = []
        for project in applied_project_list:
            card_link = url_for('project_detail', project_id=project['id'])
            card = h.div(class_='card')(
                h.a(href=card_link)(
                    h.h5(f"{project['recruitments_category']}"),
                    h.p(f"Deadline: {project['recruitment_deadline']}"),
                    h.h2(project['title'])
                )
            )
            applied_project_cards.append(card)

        # Combine all applied project cards into a single HTML string
        applied_project_cards_html = h.div(class_='card-container')(*applied_project_cards)

        # Generate the entire HTML response
        response = h.html(
            h.head(
                h.title("Applied Posts"),
                h.link(rel="stylesheet", href="/static/net.css")
            ),
            h.body(
                generate_top_bar(),
                h.hr(),
                h.br(),
                h.h3("Applied Posts"),
                applied_project_cards_html
            )
        )

        return str(response)
    else:
        return redirect(url_for('login'))



@app.route('/', methods=['GET','POST'])
def homepage():
    """
    The landing page for your project. This is the first thing your users will
    see, so you should be careful to design it to be useful to new users.
    """

    projects = load_projects()
    category_filter = request.form.get('category_filter','all')

    if category_filter == "all":
        filtered_projects = projects
    else:
        filtered_projects = [project for project in projects if project['recruitments_category'] == category_filter]


    # Create a list to hold all project cards
    project_cards = []

    # Iterate through each project and create a card for it
    for project_id, project in enumerate(filtered_projects):

        card_link = url_for('increment_view_count', project_id=project['id'])
        save_link = url_for('save_project', project_id=project['id'])
        remove_save_link = url_for('remove_save_project', project_id=project['id'])

        if 'user_email' in session:
            user_email = session['user_email']
            users = load_users()
            saved_projects = users.get(user_email, {}).get('saved_projects', [])
            if project['id'] in saved_projects:
                card = h.div(class_='card')(
                    h.a(href=card_link)(
                        h.h5(f"{project['recruitments_category']}"),
                        h.p(f"Deadline| {project['recruitment_deadline']}"),
                        h.h2(project['title']),

                        h.a(href=remove_save_link)(
                            h.img(src=url_for('static', filename='heart.png' if project['id'] not in saved_projects else 'saved.png'), alt="remove save image", class_='save-icon'))
                    ),
                    h.div(class_='view-count')(
                        h.img(src=url_for('static', filename='view.png'), alt="View count image", class_='view-icon'),  # Add this line for the image
                        h.p(f"{project['view_count']}")
                    )
                )
            else:
                card = h.div(class_='card')(
                    h.a(href=card_link)(
                        h.h5(f"{project['recruitments_category']}"),
                        h.p(f"Deadline| {project['recruitment_deadline']}"),
                        h.h2(project['title']),

                        h.a(href=save_link)(
                            h.img(src=url_for('static', filename='save.png' if project['id'] in saved_projects else 'heart.png'), alt="save image", class_='save-icon'))
                    ),
                    h.div(class_='view-count')(
                        h.img(src=url_for('static', filename='view.png'), alt="View count image", class_='view-icon'),  # Add this line for the image
                        h.p(f"{project['view_count']}")
                    )
                )
        else:
            card = h.div(class_='card')(
                h.a(href=card_link)(
                h.h5(f"{project['recruitments_category']}"),
                h.p(f"Deadline| {project['recruitment_deadline']}"),
                h.h2(project['title']),
                h.a(href=url_for('login'))(
                    h.img(src=url_for('static', filename='heart.png'), alt="save image", class_='save-icon')
                )
            ),
            h.div(class_='view-count')(
                h.img(src=url_for('static', filename='view.png'), alt="View count image", class_='view-icon'),
                h.p(f"{project['view_count']}")
            )
        )

        project_cards.append(card)

    # Combine all project cards into a single HTML string
    project_cards_html = h.div(class_='card-container')(*project_cards)

    # Generate the entire HTML response
    response = h.html(
        h.head(
            h.title("NETPROJECT"),
            h.link(rel="stylesheet", href="/static/net.css")
        ),
        h.body(
            generate_top_bar(),
            h.hr(),
            h.br(),
            h.div(class_="category-buttons")(
                h.form(method="post", action=url_for('homepage'))(
                    h.input_(type="hidden", name="category_filter", value="all"),
                    h.button("ALL", type="submit", onclick="this.form.submit()", class_="category-button"))
            ,
                h.form(method="post", action=url_for('homepage'))(
                    h.input_(type="hidden", name="category_filter", value="Project"),
                    h.button("PROJECT", type="submit", onclick="this.form.submit()", class_="category-button")
                ),
                h.form(method="post", action=url_for('homepage'))(
                    h.input_(type="hidden", name="category_filter", value="Study"),
                    h.button("STUDY", type="submit", onclick="this.form.submit()", class_="category-button")
                )
            ),
            h.h3("NEW STUDY" if category_filter == "Study" else "NEW PROJECT" if category_filter == "Project" else "NEW POST"),
            project_cards_html
        ))


    return str(response)

@app.route('/increment_view_count<int:project_id>', methods=['GET'])
def increment_view_count(project_id):
    projects = load_projects()
    if 0 <= project_id < len(projects):
        projects[project_id]['view_count'] += 1
        save_projects(projects)

    return redirect(url_for('project_detail', project_id=project_id))

def generate_project_details(project, project_id):
    """
    Generate HTML elements for project details.
    """
    return h.div(class_='project-details')(
        h.h2(project['title']),
        h.p(f"Project Owner Email: {project['user_email']}"),
        h.p(f"Description: {project['description']}"),
        h.p(f"Recruitment Category: {project['recruitments_category']}"),
        h.p(f"Number of Members: {project['number_of_members']}"),
        h.p(f"How it Works: {project['how_it_works']}"),
        h.p(f"Duration: {project['duration']}"),
        h.p(f"Recruitment Deadline: {project['recruitment_deadline']}"),
        h.p(f"Recruitment Position: {project['recruitment_position']}"),
        h.p(f"How to Contact: {project['how_to_contact']}"),
        h.hr(),
        # Add apply button
        h.form(method="post", action=f"/project_detail/{project_id}")(
            h.input_(type="submit", name='apply', value="Apply", class_="custom-button")
        )
    )


@app.route('/project_detail/<int:project_id>', methods=['GET', 'POST'])
def project_detail(project_id):
    # Retrieve the project information based on the project_id
    projects = load_projects()

    # Ensure project_id is within the valid range
    if 0 <= project_id < len(projects):
        project = projects[project_id]

        if request.method == 'POST':
            if 'user_email' in session:
                user_email = session['user_email']
                # Check if the form submission is for applying
                if 'apply' in request.form:
                    # Append the user's email to the project's applicants list
                    project.setdefault('applicants', []).append(user_email)
                    save_projects(projects)

                elif 'cancel' in request.form:
                    # Check if the user has applied to the project
                    if user_email in project.get('applicants', []):
                        # Remove the user's email from the project's applicants list
                        project['applicants'].remove(user_email)
                        save_projects(projects)
                return redirect(url_for('homepage'))
            else:
                return redirect(url_for('login'))

        # Generate the HTML response
        response = str(h.html(
            h.head(
                h.title("Project Detail"),
                h.link(rel="stylesheet", href="/static/net.css")
            ),
            h.body(
                generate_top_bar(),
                h.hr(),
                h.br(),
                generate_project_details(project, project_id),

                # Display the list of applicants in a table format
                h.div(style="text-align: center;")(
                    h.table(style="margin: auto;")(
                        h.tr(
                            h.th("Applicants"),
                            h.th("Cancel Availability")
                        ),
                        *[h.tr(
                            h.td(applicant),
                            h.td(
                                # Cancel form
                                h.form(method="post", action=f"/project_detail/{project_id}")(
                                    h.input_(type="hidden", name="cancel", value="Cancel"),
                                    h.input_(type="hidden", name="applicant_email", value=applicant),
                                    h.input_(type="submit", id="Cancel", content="Cancel", value="Cancel", class_="custom-button")
                                )
                            )
                        ) for applicant in project.get('applicants', [])]
                    )
                )
            )
        ))
        return response
    else:
        return redirect(url_for('homepage'))


@app.route('/signup', methods=['GET','POST'])
def signup():
    error_message= ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        users = load_users()

        # Check if the email already exists in the users data
        if email in users:
            error_message = "User email already exists. Please choose another email."
        else:
            # Save user data to users.json
            users[email] = {'username': username, 'password': password, 'email': email}
            save_users(users)
            session['user_email'] = email
            return redirect('/login')

    if error_message:
        error_span = h.span(str(error_message), style="color: red; ")
    else:
        error_span = h.span("")

    response =  h.html(
        h.head(
            h.title("NETPROJECT - Sign Up"),
            h.link(rel="stylesheet", href="/static/net.css")
        ),
        h.body(
            generate_top_bar(),
            h.hr(),
            h.br(),
            h.div(id='SignUp')(
                h.form(method="post", action='/signup')(
                    h.h1("Sign Up for NETPROJECT"),
                    h.label("Username: "),
                    h.input_(type="text", name="username", required=True),
                    h.br(),
                    h.label("Email: "),
                    h.input_(type="email", name="email", required=True),
                    h.br(),
                    h.label("Password: "),
                    h.input_(type="password", name="password", required=True),
                    h.br(),
                    h.input_(type='submit', value='Sign Up'),
                    h.br(),
                    h.a("Already have an account? Login here", href='/login'),
                    h.br(),
                    error_span
                )
            )
        )
    )
    return str(response)

# TODO: Add your code here to define other routes that your page will use
@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message= ""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        users = load_users()

        # Check if the email exists in users data
        if email in users:
            # Check if the provided password matches the stored password
            if password == users[email]['password']:
                session['user_email'] = email
                return redirect(url_for('homepage'))
            else:
                error_message = "Incorrect password. Please try again."
        else:
            error_message = "User not found. Please sign up first."

    if error_message:
        error_span = h.span(str(error_message), style="color: red; ")
    else:
        error_span = h.span("")

    # If request method is GET, render the login page
    response =  h.html(
        h.head(
            h.title("NETPROJECT - Login"),
            h.link(rel="stylesheet", href="/static/net.css")
        ),
        h.body(
            generate_top_bar(),
            h.hr(),
            h.br(),
            h.div(id='SignUp')(
                h.form(method="post", action='/login')(
                    h.h1("Login to NETPROJECT"),
                    h.label("Email: "),
                    h.input_(type="email", name="email", required=True),  # Ensure the 'email' field is included
                    h.br(),
                    h.label("Password: "),
                    h.input_(type="password", name="password", required=True),
                    h.br(),
                    h.input_(type='submit', value='Login'),
                    h.br(),
                    h.a("Don't have an account? Sign up here", href='/signup'),
                    h.br(),
                    error_span
                )
            )
        )
    )
    return str(response)


@app.route('/logout')
def logout():
    """
    Handle the logout action.
    """
    session.pop('user_email', None)  # Clear the user_data from the session
    return redirect(url_for('homepage'))

@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        if 'user_email' in session:
            user_email = session['user_email']
            projects = load_projects()

            project_id = len(projects)

            project_data = {
                'id': project_id,
                'title': request.form.get('project_title'),
                'recruitments_category': request.form.get('recruitments_category'),
                'description': request.form.get('project_description'),
                'number_of_members': request.form.get('number_of_members'),
                'how_it_works': request.form.get('how_it_works'),
                'duration': request.form.get('duration'),
                'recruitment_deadline': request.form.get('recruitment_deadline'),
                'recruitment_position': request.form.get('recruitment_position'),
                'technology stack': request.form.get('technology_stack'),
                'how_to_contact': request.form.get('how_to_contact'),
                'user_email': user_email
            }


            projects.append(project_data)
            save_projects(projects)
        else:
            return redirect(url_for('login'))

        return redirect(url_for('homepage'))
    else:
        return create_project_form()

def create_project_form():
    response = h.html(
    h.head(
        h.title("Create Project"),
        h.link(rel="stylesheet", href="/static/net.css")),
    h.body(
        generate_top_bar(),
        h.hr(),
        h.div(class_='title')(
            h.h2("Enter the basic information about your project")
        ),
        h.div(id='forms-container')(
            h.form(method="post", action='/create_project')(
                h.div(class_='form-row')(
                    h.div(class_='form-container')(
                        h.label("Recruitments category"),
                        h.select(name='recruitments_category', class_='select',required=True)(
                            h.option("Study", value="Study"),
                            h.option("Project", value="Project")
                        )
                    ),
                    h.div(class_='form-container')(
                        h.label("Number of members"),
                        h.input_(type='text', placeholder='Number of members', name='number_of_members',required=True)
                    )
                ),
                h.div(class_='form-row')(
                    h.div(class_='form-container')(
                        h.label("How it works"),
                        h.select(name='how_it_works', class_='select',required=True)(
                            h.option("Online", value="online"),
                            h.option("Offline", value="offline")
                        )
                    ),
                    h.div(class_='form-container')(
                        h.label("Duration of the project/study"),
                        h.input_(type='text', placeholder='Duration', name='duration',required=True)
                    )
                ),
                h.div(class_='form-row')(
                    h.div(class_='form-container')(
                        h.label("Technology stack"),
                        h.input_(type='text', placeholder='Technology stack', name='technology_stack',required=True)
                    ),
                    h.div(class_='form-container')(
                        h.label("Recruitment deadline"),
                        h.input_(type='text', placeholder='Recruitment deadline', name='recruitment_deadline',required=True)
                    )
                ),
                h.div(class_='form-row')(
                    h.div(class_='form-container')(
                        h.label("Recruitment position"),
                        h.input_(type='text', placeholder='Recruitment position', name='recruitment_position',required=True)
                    ),
                    h.div(class_='form-container')(
                        h.label("How to contract"),
                        h.select(name='how_to_contract', class_='select',required=True)(
                            h.option("Email", value="email"),
                            h.option("NETPROJECT Chat", value="netproject_chat")
                        )
                    )
                ),
                h.div(class_='title')(
                    h.hr(),
                    h.h2("Tell us about your project")),

                    h.div(id='centered-container')(
                        h.div(class_='description')(
                            h.textarea(name='project_title', rows='1', cols='155', style="margin-bottom: 10px; text-align: left;", placeholder='Enter project title',required=True),
                            h.textarea(name='project_description', rows='15', cols='155', style="margin-bottom: 10px; text-align: left;", placeholder='Enter project description',required=True),
                            h.input_(type='submit', class_='custom-button', content='Create', style="display: block; margin-top: 10px;",required=True)
                        )
                    )
                )
            )
        )
    )
    return str(response)

@app.route('/save_project/<int:project_id>', methods=['GET'])
def save_project(project_id):
    # Check if the user is logged in
    if 'user_email' in session:
        user_email = session['user_email']
        # Load user data from users.json
        users = load_users()
        if user_email in users:
            saved_projects = users[user_email].setdefault('saved_projects', [])
            # Check if the project index is not already saved
            if project_id not in saved_projects:
                saved_projects.append(project_id)
                # Save updated user data to users.json
                save_users(users)

        return redirect(url_for('homepage'))
    else:
        return redirect(url_for('login'))


@app.route('/remove_save_project/<int:project_id>', methods=['GET'])
def remove_save_project(project_id):
    # Check if the user is logged in
    if 'user_email' in session:
        user_email = session['user_email']
        # Load user data from users.json
        users = load_users()
        if user_email in users:
            saved_projects = users[user_email].setdefault('saved_projects', [])
            # Check if the project index is not already saved
            if project_id in saved_projects:
                saved_projects.remove(project_id)
                # Save updated user data to users.json
                save_users(users)

        return redirect(url_for('homepage'))
    else:
        return redirect(url_for('login'))


# Start our app
if __name__ == "__main__":
    app.run(port=5003, debug=True)
