# VFilm — Movie Catalog

VFilm is a movie catalog web application built with Python and Flask. It provides a web interface for browsing movies and exploring movie information.

## Features

- Browse recently added movies
- Explore movies by genre
- Search movies by title and other details
- View movie details
- User registration and login
- Personal watchlist
- User profile and account settings
- Contact form

## Technologies

- Python
- Flask
- SQLite
- HTML, CSS and JavaScript
- Docker and Docker Compose

## Project Structure

```text
VFilm-MovieCatalog/
├── docker-compose.yml
└── app/
    ├── app.py
    ├── Dockerfile
    ├── requirements.txt
    ├── vfilm.db
    ├── templates/
    └── static/
        ├── css/
        ├── js/
        └── img/
```

## Run with Docker

1. Install Docker Desktop.
2. Open a terminal in the project root directory, where `docker-compose.yml` is located.
3. Run:

   ```bash
   docker compose up --build
   ```

4. Open [http://localhost](http://localhost) in your browser.

To stop the application, press `Ctrl+C` in the terminal.

## Database and Security

The repository should contain only a sanitized demonstration database with sample movie data. Personal user records and contact messages should not be included.

Configure a secure Flask secret key through an environment variable before deploying the application publicly.

## Disclaimer

This project is intended for educational and portfolio purposes. Review authentication, input validation and security settings before using it in a production environment.
