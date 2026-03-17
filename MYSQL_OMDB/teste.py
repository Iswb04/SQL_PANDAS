from flask import Flask, request, jsonify
import mysql.connector
import requests

app = Flask(__name__)

# 🔌 CONEXÃO MYSQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sql654**",
    database="mysql_omdb"
)

cursor = conn.cursor()

# 🏠 HOME
@app.route("/")
def home():
    return """
    <h1>🎬 Movie System</h1>
    <a href="/register">Register</a><br>
    <a href="/login">Login</a><br>
    <a href="/movies">Ver Filmes</a>
    """

# 🔐 REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return """
        <h2>Register</h2>
        <form method="post">
            <input name="username" placeholder="Username"><br>
            <input name="password" type="password" placeholder="Password"><br>
            <button type="submit">Register</button>
        </form>
        """

    username = request.form["username"]
    password = request.form["password"]

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        return "User already exists"

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, password)
    )
    conn.commit()

    return "User created!"

# 🔑 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return """
        <h2>Login</h2>
        <form method="post">
            <input name="username" placeholder="Username"><br>
            <input name="password" type="password" placeholder="Password"><br>
            <button type="submit">Login</button>
        </form>
        """

    username = request.form["username"]
    password = request.form["password"]

    cursor.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s",
        (username, password)
    )

    user = cursor.fetchone()

    if user:
        return f"Login successful! User ID: {user[0]}"
    else:
        return "Invalid login"

# 🎬 LISTAR FILMES
@app.route("/movies")
def list_movies():
    cursor.execute("SELECT * FROM movies")
    movies = cursor.fetchall()

    html = "<h2>Filmes</h2><ul>"
    for m in movies:
        html += f"<li>{m[1]} ({m[2]})</li>"
    html += "</ul>"

    html += """
    <h3>Adicionar Filme</h3>
    <form method="post" action="/add_movie">
        <input name="title" placeholder="Nome do filme">
        <button type="submit">Adicionar</button>
    </form>
    """

    return html

# ➕ ADICIONAR FILME
@app.route("/add_movie", methods=["POST"])
def add_movie():
    movie_name = request.form["title"]

    url = f"https://www.omdbapi.com/?apikey=9a51a7ae&t={movie_name}"
    data = requests.get(url).json()

    if data["Response"] == "True":

        title = data["Title"]

        cursor.execute("SELECT * FROM movies WHERE title = %s", (title,))
        if cursor.fetchone():
            return "Movie already exists"

        cursor.execute("""
            INSERT INTO movies (title, year, runtime, genre, director)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            title,
            data["Year"],
            data["Runtime"],
            data["Genre"],
            data["Director"]
        ))

        conn.commit()

        return "Movie added! <br><a href='/movies'>Voltar</a>"

    return "Movie not found"

# ⭐ AVALIAR
@app.route("/rate", methods=["POST"])
def rate():
    data = request.json

    cursor.execute("""
        INSERT INTO ratings (user_id, movie_id, rating)
        VALUES (%s, %s, %s)
    """, (data["user_id"], data["movie_id"], data["rating"]))

    conn.commit()

    return jsonify({"message": "Rating added!"})

# 💬 COMENTAR
@app.route("/comment", methods=["POST"])
def comment():
    data = request.json

    if len(data["comment"]) > 500:
        return jsonify({"error": "Comment too long"}), 400

    cursor.execute("""
        INSERT INTO comments (user_id, movie_id, comment)
        VALUES (%s, %s, %s)
    """, (data["user_id"], data["movie_id"], data["comment"]))

    conn.commit()

    return jsonify({"message": "Comment added!"})

# 🚀 RUN
if __name__ == "__main__":
    app.run(debug=True)