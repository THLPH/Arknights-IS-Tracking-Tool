# Rhodes Island Exploration Archive

## Overview
The **Rhodes Island Exploration Archive** is a performance tracking and strategy optimization database for the *Integrated Strategies* (Roguelike) game modes in the mobile game **Arknights**. 

This application allows players to log their gameplay runs, including operators drafted, relics collected, and starting squads. The goal is to provide a centralized hub for performance analysis to help players identify their personal winning patterns and refine their strategies.

---

## Features

* **Log Runs:** Record new gameplay sessions via a dedicated web form. Users can specify difficulty, starting squads, drafted operators, and relics.
* **Run History Dashboard:** Query the database to filter past runs by specific criteria, such as the ending reached or difficulty level.
* **Manage Records:** Full CRUD functionality to update runs currently in progress or delete mis-logged entries.
* **Strategic Advisor Panel:** An advanced analytical tool that calculates a **"Synergy Delta"**.
  
    > **Note:** The Synergy Delta measures the win rate difference between runs where recruited operators match the class-specific buffs of the chosen squad versus runs where those buffs were ignored.

---

## Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Database** | SQLite |
| **Backend** | Python, Flask |
| **Frontend** | HTML, CSS, Jinja2 |
| **Data Processing** | Python `json` and `sqlite3` libraries |

---

## Data Sourcing

1.  **Static Data:** Base game data for Operators, Relics, and Squads is sourced in JSON format from the open-source [Kengxxiao/ArknightsGameData](https://github.com/Kengxxiao/ArknightsGameData) repository.
2.  **Dynamic Data:** Personal run data is generated and maintained by the user through the web interface.

---

## Setup and Installation

Follow these steps to get the archive running locally:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/THLPH/Arknights-IS-Tracking-Tool.git
    ```
2.  To be updated
