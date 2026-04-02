-- Static Tables
CREATE TABLE Operator (
    OperatorID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Rarity INTEGER,
    Class TEXT,
    Archetype TEXT
);

CREATE TABLE Relic (
    RelicID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Effect_Description TEXT,
    Relic_Category TEXT
);

CREATE TABLE Squad (
    SquadID INTEGER PRIMARY KEY,
    Squad_Name TEXT NOT NULL,
    Passive_Buff TEXT
);

-- Core Dynamic Table
CREATE TABLE Run (
    RunID INTEGER PRIMARY KEY AUTOINCREMENT,
    Date TEXT NOT NULL,
    Difficulty_Level INTEGER,
    Ending_Reached TEXT,
    Final_Score INTEGER,
    SquadID INTEGER,
    FOREIGN KEY (SquadID) REFERENCES Squad(SquadID)
);

-- Junction Tables for M:N Relationships
CREATE TABLE Run_Operator (
    RunID INTEGER,
    OperatorID INTEGER,
    PRIMARY KEY (RunID, OperatorID),
    FOREIGN KEY (RunID) REFERENCES Run(RunID),
    FOREIGN KEY (OperatorID) REFERENCES Operator(OperatorID)
);

CREATE TABLE Run_Relic (
    RunID INTEGER,
    RelicID INTEGER,
    PRIMARY KEY (RunID, RelicID),
    FOREIGN KEY (RunID) REFERENCES Run(RunID),
    FOREIGN KEY (RelicID) REFERENCES Relic(RelicID)
);

CREATE TABLE Squad_Synergy (
    SquadID INTEGER,
    OperatorID INTEGER,
    PRIMARY KEY (SquadID, OperatorID),
    FOREIGN KEY (SquadID) REFERENCES Squad(SquadID),
    FOREIGN KEY (OperatorID) REFERENCES Operator(OperatorID)
);
