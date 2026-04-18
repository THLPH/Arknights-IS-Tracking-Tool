from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import math

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('rhodes.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log', methods=('GET', 'POST'))
def log_run():
    conn = get_db_connection()
    squads = conn.execute('SELECT SquadID, Squad_Name FROM Squad').fetchall()
    relics = conn.execute('SELECT RelicID, Name FROM Relic ORDER BY Name').fetchall()
    operators = conn.execute('SELECT OperatorID, Name FROM Operator ORDER BY Name').fetchall()
    
    if request.method == 'POST':
        date = request.form['date']
        difficulty = request.form['difficulty']
        squad = request.form['squad']
        ending = request.form['ending']
        score = request.form['score']
        selected_relics = request.form.getlist('relics')
        selected_operators = request.form.getlist('operators')
        
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Run (Date, Difficulty_Level, Ending_Reached, Final_Score, SquadID)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, difficulty, ending, score, squad))
        run_id = cursor.lastrowid
        
        for relic_id in selected_relics:
            cursor.execute('INSERT INTO Run_Relic (RunID, RelicID) VALUES (?, ?)', (run_id, relic_id))
        for op_id in selected_operators:
            cursor.execute('INSERT INTO Run_Operator (RunID, OperatorID) VALUES (?, ?)', (run_id, op_id))
        conn.commit()
        conn.close()
        return redirect(url_for('history'))
    
    conn.close()
    return render_template('log_run.html', squads=squads, relics=relics, operators=operators)

@app.route('/history')
def history():
    conn = get_db_connection()
    runs = conn.execute('''
        SELECT r.RunID, r.Date, s.Squad_Name, r.Difficulty_Level, r.Ending_Reached, r.Final_Score
        FROM Run r
        JOIN Squad s ON r.SquadID = s.SquadID
        ORDER BY r.RunID DESC
    ''').fetchall()
    
    runs_with_details = []
    for run in runs:
        relics = conn.execute('''
            SELECT Relic.Name FROM Relic
            JOIN Run_Relic ON Relic.RelicID = Run_Relic.RelicID
            WHERE Run_Relic.RunID = ?
        ''', (run['RunID'],)).fetchall()
        operators = conn.execute('''
            SELECT Operator.Name FROM Operator
            JOIN Run_Operator ON Operator.OperatorID = Run_Operator.OperatorID
            WHERE Run_Operator.RunID = ?
        ''', (run['RunID'],)).fetchall()
        runs_with_details.append(dict(run, 
                                      relics=[r['Name'] for r in relics],
                                      operators=[o['Name'] for o in operators]))
    conn.close()
    return render_template('history.html', runs=runs_with_details)

@app.route('/edit/<int:run_id>', methods=('GET', 'POST'))
def edit_run(run_id):
    conn = get_db_connection()
    run = conn.execute('SELECT * FROM Run WHERE RunID = ?', (run_id,)).fetchone()
    if not run:
        conn.close()
        return redirect(url_for('history'))
    
    if request.method == 'POST':
        date = request.form['date']
        difficulty = request.form['difficulty']
        ending = request.form['ending']
        score = request.form['score']
        squad = request.form['squad']
        selected_relics = request.form.getlist('relics')
        selected_operators = request.form.getlist('operators')
        
        conn.execute('''
            UPDATE Run SET Date=?, Difficulty_Level=?, Ending_Reached=?, Final_Score=?, SquadID=?
            WHERE RunID=?
        ''', (date, difficulty, ending, score, squad, run_id))
        conn.execute('DELETE FROM Run_Relic WHERE RunID = ?', (run_id,))
        conn.execute('DELETE FROM Run_Operator WHERE RunID = ?', (run_id,))
        for relic_id in selected_relics:
            conn.execute('INSERT INTO Run_Relic (RunID, RelicID) VALUES (?, ?)', (run_id, relic_id))
        for op_id in selected_operators:
            conn.execute('INSERT INTO Run_Operator (RunID, OperatorID) VALUES (?, ?)', (run_id, op_id))
        conn.commit()
        conn.close()
        return redirect(url_for('history'))
    
    squads = conn.execute('SELECT SquadID, Squad_Name FROM Squad').fetchall()
    relics = conn.execute('SELECT RelicID, Name FROM Relic ORDER BY Name').fetchall()
    operators = conn.execute('SELECT OperatorID, Name FROM Operator ORDER BY Name').fetchall()
    current_relics = conn.execute('SELECT RelicID FROM Run_Relic WHERE RunID = ?', (run_id,)).fetchall()
    current_operators = conn.execute('SELECT OperatorID FROM Run_Operator WHERE RunID = ?', (run_id,)).fetchall()
    current_relic_ids = [r['RelicID'] for r in current_relics]
    current_op_ids = [o['OperatorID'] for o in current_operators]
    conn.close()
    return render_template('edit_run.html', run=run, squads=squads, relics=relics, operators=operators,
                           current_relic_ids=current_relic_ids, current_op_ids=current_op_ids)

@app.route('/delete/<int:run_id>', methods=('POST',))
def delete_run(run_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Run_Relic WHERE RunID = ?', (run_id,))
    conn.execute('DELETE FROM Run_Operator WHERE RunID = ?', (run_id,))
    conn.execute('DELETE FROM Run WHERE RunID = ?', (run_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('history'))

# ------------------ ADVANCED FUNCTION 1: Risk Slider (What-If) ------------------
@app.route('/advisor')
def advisor():
    conn = get_db_connection()
    squads = conn.execute('SELECT SquadID, Squad_Name FROM Squad').fetchall()
    conn.close()
    return render_template('advisor.html', squads=squads)

@app.route('/api/squad_stats/<int:squad_id>')
def squad_stats(squad_id):
    """Returns average score and coefficient of variation for a squad."""
    conn = get_db_connection()
    stats = conn.execute('''
        SELECT AVG(Final_Score) as avg_score, 
               AVG((Final_Score - (SELECT AVG(Final_Score) FROM Run WHERE SquadID = ?)) * 
                   (Final_Score - (SELECT AVG(Final_Score) FROM Run WHERE SquadID = ?))) as variance
        FROM Run
        WHERE SquadID = ?
    ''', (squad_id, squad_id, squad_id)).fetchone()
    
    count = conn.execute('SELECT COUNT(*) as cnt FROM Run WHERE SquadID = ?', (squad_id,)).fetchone()['cnt']
    conn.close()
    
    if count < 2 or not stats['avg_score']:
        return jsonify({'avg_score': 0, 'cv': 0, 'count': count})
    
    avg = stats['avg_score']
    variance = stats['variance'] if stats['variance'] else 0
    std_dev = math.sqrt(variance) if variance > 0 else 0
    cv = std_dev / avg if avg > 0 else 0
    return jsonify({'avg_score': round(avg, 2), 'cv': round(cv, 4), 'count': count})

# ------------------ ADVANCED FUNCTION 2: Synergy Delta ------------------
@app.route('/api/synergy_delta')
def synergy_delta():
    """Calculate win rate difference between matching and non-matching operator picks."""
    conn = get_db_connection()
    
    data = conn.execute('''
        WITH RunOutcomes AS (
            SELECT 
                r.RunID,
                r.SquadID,
                s.Squad_Name,
                CASE WHEN r.Ending_Reached != 'Failed' THEN 1 ELSE 0 END as is_win,
                r.Final_Score
            FROM Run r
            JOIN Squad s ON r.SquadID = s.SquadID
        ),
        OperatorClasses AS (
            SELECT 
                ro.RunID,
                o.Class
            FROM Run_Operator ro
            JOIN Operator o ON ro.OperatorID = o.OperatorID
        ),
        SquadClassPreference AS (
            SELECT 
                ro.SquadID,
                oc.Class,
                COUNT(*) as class_count
            FROM RunOutcomes ro
            JOIN OperatorClasses oc ON ro.RunID = oc.RunID
            WHERE ro.is_win = 1
            GROUP BY ro.SquadID, oc.Class
        ),
        BestClass AS (
            SELECT 
                SquadID,
                Class as best_class,
                ROW_NUMBER() OVER (PARTITION BY SquadID ORDER BY class_count DESC) as rn
            FROM SquadClassPreference
        )
        SELECT 
            ro.Squad_Name,
            COUNT(DISTINCT ro.RunID) as total_runs,
            ROUND(100.0 * SUM(CASE WHEN oc.Class = bc.best_class THEN ro.is_win ELSE 0 END) / 
                  NULLIF(COUNT(CASE WHEN oc.Class = bc.best_class THEN 1 END), 0), 2) as win_rate_matching,
            ROUND(100.0 * SUM(CASE WHEN oc.Class != bc.best_class OR oc.Class IS NULL THEN ro.is_win ELSE 0 END) / 
                  NULLIF(COUNT(CASE WHEN oc.Class != bc.best_class OR oc.Class IS NULL THEN 1 END), 0), 2) as win_rate_non_matching,
            ROUND(
                (100.0 * SUM(CASE WHEN oc.Class = bc.best_class THEN ro.is_win ELSE 0 END) / NULLIF(COUNT(CASE WHEN oc.Class = bc.best_class THEN 1 END), 0))
                - 
                (100.0 * SUM(CASE WHEN oc.Class != bc.best_class OR oc.Class IS NULL THEN ro.is_win ELSE 0 END) / NULLIF(COUNT(CASE WHEN oc.Class != bc.best_class OR oc.Class IS NULL THEN 1 END), 0))
            , 2) as synergy_delta
        FROM RunOutcomes ro
        LEFT JOIN OperatorClasses oc ON ro.RunID = oc.RunID
        LEFT JOIN BestClass bc ON ro.SquadID = bc.SquadID AND bc.rn = 1
        GROUP BY ro.Squad_Name
        HAVING total_runs >= 2
        ORDER BY synergy_delta DESC
    ''').fetchall()
    
    conn.close()
    return jsonify([dict(row) for row in data])

if __name__ == '__main__':
    app.run(debug=True)