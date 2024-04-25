# lolz verif

## Project Description

**lolz verif** is a Telegram bot that allows users to save information about their books and retrieve it from a database. This project utilizes Python with libraries such as SQLAlchemy for database interactions and Aiogram for handling Telegram bot interactions.

## Features

- **Save Book Information:** Users can save detailed information about their books, including title, author, genre and description of book.
- **Retrieve Book Information:** Users can easily retrieve their saved books from the database through simple Telegram bot commands.

## Getting Started

### Prerequisites

Before you begin, ensure you have Python installed on your system. You can download Python from [here](https://www.python.org/downloads/).

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/lolz-verif.git
   cd lolz-verif
   ```

2. Make the virtual environment and activate it:
   ```bash
   python -m venv venv
   ```
   For Windows
   ```bash
   venv\Scripts\activate.bat
   ```
   For MacOS/Linux
   ```bash
   source venv/bin/activate
   ```
   
3. Install the required packages:
   ```bash
   pip install -r requirments.txt
   ```

4. Setup your database and make the `.env` file with your database URL and Telegram bot token.

5. Start the PostgresSQL server. You can see how to do it on [Linux server](https://www.youtube.com/watch?v=wWJAE3gZIvM) or [Windows](https://www.youtube.com/watch?v=oEi5IUgxaU0)

### Usage

Run the bot:
```bash
python bot.py
```

---

This README provides a basic outline and can be extended with more sections like "Configuration," "Examples," and "Support" depending on the complexity and needs of your project. If you have any specific details or sections you want to add, let me know!
