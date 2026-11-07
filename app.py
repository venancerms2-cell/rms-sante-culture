from flask import Flask, request, redirect, url_for, render_template
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

def get_db():
    db_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_url, sslmode='require', connect_timeout=30)
    return conn

@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Création de la table des articles
        cur.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id SERIAL PRIMARY KEY,
                titre TEXT,
                categorie TEXT,
                contenu TEXT,
                date TEXT
            )
        ''')
        conn.commit()

        # Si on soumet un nouvel article
        if request.method == 'POST':
            titre = request.form.get('titre')
            categorie = request.form.get('categorie')
            contenu = request.form.get('contenu')
            if titre and categorie and contenu:
                date_actuelle = datetime.now().strftime("%d/%m/%Y à %H:%M")
                cur.execute('INSERT INTO articles (titre, categorie, contenu, date) VALUES (%s, %s, %s, %s)', (titre, categorie, contenu, date_actuelle))
                conn.commit()
                return redirect(url_for('home'))

        # Filtre par catégorie (Santé ou Culture)
        filtre = request.args.get('categorie', '')
        if filtre:
            cur.execute('SELECT id, titre, categorie, contenu, date FROM articles WHERE categorie = %s ORDER BY id DESC', (filtre,))
        else:
            cur.execute('SELECT id, titre, categorie, contenu, date FROM articles ORDER BY id DESC')

        articles = cur.fetchall()
        cur.close()
        conn.close()
        
        return render_template('index.html', articles=articles, filtre=filtre)
        
    except Exception as e:
        return f"<div style='background:#000; color:red; padding:20px; font-family:sans-serif;'><h1>Erreur de connexion :</h1><p style='background:#333; padding:10px;'>{e}</p></div>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
