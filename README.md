# OptiCourse: University Scheduling App

OptiCourse is a web application developed using Flask for optimizing university course scheduling based on professor preferences and course requirements.

## Getting Started

These instructions will guide you to set up and run this project:

1. **Clone the repository**

    First, clone the repository from GitHub to get a local copy of the code:

    ```bash
    git clone https://github.com/Kuiper-sun/university-scheduling-app.git
    cd university-scheduling-app
    ```

2. **Set up a virtual environment**

    Create a new virtual environment named `venv` using the command:

    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment**

    Activate the virtual environment with the following commands:

    For Windows:

    ```bash
    venv\Scripts\activate
    ```

    For Unix or MacOS:

    ```bash
    source venv/bin/activate
    ```

4. **Install dependencies**

    Install the required Python packages listed in the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

5. **Launch the application**

    Run the Flask application using:

    ```bash
    python app.py
    ```

    The application will be accessible at `http://localhost:5000` in your web browser.

## Project Structure

Here's an overview of the project's file structure:

- `university-scheduling-app/`
  - `app.py`: Main application file.
  - `branch_and_bound.py`: Algorithm implementation.
  - `requirements.txt`: List of Python dependencies.
  - `static/`: Directory for static files.
    - `background.jpg`: Background image for the web app.
    - `computer.jpg`: Image asset.
    - `styles.css`: CSS styles for the web app.
  - `templates/`: Directory for HTML templates.
    - `index.html`: Main page template.
    - `results.html`: Results page template.

Enjoy using OptiCourse for efficient university scheduling!
