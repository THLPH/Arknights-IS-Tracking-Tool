DROP TABLE IF EXISTS Run_Relic;
DROP TABLE IF EXISTS Run_Operator;
DROP TABLE IF EXISTS Squad_Synergy;
DROP TABLE IF EXISTS Run;
DROP TABLE IF EXISTS Operator;
DROP TABLE IF EXISTS Relic;
DROP TABLE IF EXISTS Squad;

CREATE TABLE Squad (
    SquadID INTEGER PRIMARY KEY AUTOINCREMENT,
    Squad_Name TEXT NOT NULL,
    Passive_Buff TEXT
);

CREATE TABLE Relic (
    RelicID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Effect_Description TEXT,
    Category TEXT
);

CREATE TABLE Operator (
    OperatorID TEXT PRIMARY KEY,
    Name TEXT NOT NULL,
    Rarity INTEGER,
    Class TEXT,
    Archetype TEXT
);

CREATE TABLE Run (
    RunID INTEGER PRIMARY KEY AUTOINCREMENT,
    Date TEXT NOT NULL,
    Difficulty_Level INTEGER NOT NULL,
    Ending_Reached TEXT,
    Final_Score INTEGER,
    SquadID INTEGER,
    FOREIGN KEY (SquadID) REFERENCES Squad(SquadID)
);

CREATE TABLE Run_Relic (
    RunID INTEGER,
    RelicID INTEGER,
    PRIMARY KEY (RunID, RelicID),
    FOREIGN KEY (RunID) REFERENCES Run(RunID),
    FOREIGN KEY (RelicID) REFERENCES Relic(RelicID)
);

CREATE TABLE Run_Operator (
    RunID INTEGER,
    OperatorID TEXT,
    PRIMARY KEY (RunID, OperatorID),
    FOREIGN KEY (RunID) REFERENCES Run(RunID),
    FOREIGN KEY (OperatorID) REFERENCES Operator(OperatorID)
);

CREATE TABLE Squad_Synergy (
    SquadID INTEGER,
    OperatorID TEXT,
    PRIMARY KEY (SquadID, OperatorID),
    FOREIGN KEY (SquadID) REFERENCES Squad(SquadID),
    FOREIGN KEY (OperatorID) REFERENCES Operator(OperatorID)
);