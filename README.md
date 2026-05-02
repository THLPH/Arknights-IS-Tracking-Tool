The following sections describe the technical architecture and primary functionality of the Rhodes Island Exploration Archive. This documentation follows the structure and technical terminology established in the project development reports.

### 1. Introduction
**The Rhodes Island Exploration Archive** is a custom database application developed to track and optimize player performance in the *Integrated Strategies* game mode of the mobile game *Arknights*. While existing community tools provide static game data, they lack personalized tracking features for individual users. This application addresses that gap by logging specific operational data, including squad choices, operator drafts, relic acquisitions, and final scores. The system leverages complex SQL queries to reveal personalized winning patterns and provide mathematical strategic advice.

---

### 2. Key Features

**Strategic Advisor Engine (Synergy Delta Analysis)**
This analytical tool calculates the "Synergy Delta" by inferring optimal character pairings based on a user's actual match history. The implementation utilizes four sequential Common Table Expressions (CTEs) and window functions such as `ROW_NUMBER() OVER` to mathematically determine win-rate differences. By calculating the delta between runs with optimal class matching versus non-matching runs, the system identifies the most effective playstyles regardless of changes to the game meta [cite: 53-56, 60].

**Risk Slider (Volatility Analysis)**
The application includes a "What-If" analysis tool that determines the historical volatility of a selected squad. This functionality relies on a complex aggregate SQL query that calculates variance and average scores directly within the database. The Flask backend then processes these values into a Coefficient of Variation (CV), which is sent to the frontend via a JSON API to predict expected scores based on playstyle aggression.

**Automated Data Ingestion Pipeline**
A dedicated `setup_db.py` script was developed to parse open-source JSON game data from external repositories. The pipeline includes custom functions to filter out unobtainable entities and strip formatting artifacts from highly nested JSON files. This automated process seeds the static relational tables before any user interaction occurs.

**Dynamic User Interface**
The frontend is built with HTML, CSS, and Jinja2 templating to match the "terminal" aesthetic of the game. The user interface relies on JavaScript and the Fetch API to asynchronously request data from Flask endpoints. This architecture allows the analytical dashboards to update dynamically without requiring a full page reload.

**Comprehensive Record Management**
The system supports full CRUD operations, allowing users to insert, read, update, and delete run data. To ensure data integrity within the many-to-many relationships of the junction tables, the backend executes a cascading deletion process in Python. This logic removes dependent records in the `Run_Relic` and `Run_Operator` tables before the parent record is deleted from the central `Run` table.

---

## Database Architecture

The system is built on a custom relational schema adhering to Boyce-Codd Normal Form (BCNF), ensuring all non-key attributes are fully functionally dependent on the primary key. 

To handle the complex game mechanics, the schema resolves many-to-many relationships (such as a single run having multiple drafted operators and relics) using composite primary keys within dedicated junction tables (`Run_Operator` and `Run_Relic`).

---

## Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Database** | SQLite, Advanced SQL (CTEs, Window Functions, Aggregate Math) |
| **Backend** | Python, Flask |
| **Frontend** | HTML5, CSS3, JavaScript (Fetch API, DOM Manipulation), Jinja2 |
| **Data Pipeline** | Python `json` and `sqlite3` libraries |

---

## Setup and Installation

Follow these steps to initialize the database and run the application locally:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/THLPH/Arknights-IS-Tracking-Tool.git
    cd Arknights-IS-Tracking-Tool
    ```

2.  **Set up a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    pip install Flask
    ```

3.  **Initialize and Seed the Database:**
    Ensure `roguelike_topic_table.json` and `character_table.json` are in the root directory. Run the ingestion script to build the schema and populate static data:
    ```bash
    python setup_db.py
    ```

4.  **Launch the Application:**
    ```bash
    python app.py
    ```
    The server will start on `http://127.0.0.1:5000/`.

---

## Data Sourcing & Acknowledgements

Static game data (Operators, Relics, and Squads) is parsed directly from the community-maintained [ArknightsGameData](https://github.com/ArknightsAssets/ArknightsGamedata) GitHub repository. Dynamic operational data is generated entirely by the user.
