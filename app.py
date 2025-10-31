from flask import Flask, render_template, request, redirect, url_for, session
import random, time, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")

leaderboard = []  # in-memory

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        session.clear()
        name = request.form.get("name")
        difficulty = request.form.get("difficulty")

        ranges = {"easy": 50, "medium": 100, "hard": 500}
        max_num = ranges.get(difficulty, 100)

        session["name"] = name
        session["difficulty"] = difficulty
        session["number"] = random.randint(1, max_num)
        session["attempts"] = 0
        session["start_time"] = time.time()
        session["max_num"] = max_num

        return redirect(url_for("play"))
    return render_template("index.html")

@app.route("/play", methods=["GET", "POST"])
def play():
    if "number" not in session:
        return redirect(url_for("home"))

    message, hint, emoji = "", "", ""
    number = session["number"]
    max_num = session["max_num"]

    if request.method == "POST":
        try:
            guess = int(request.form["guess"])
        except ValueError:
            message = "⚠️ Please enter a valid number."
            return render_template("play.html", message=message)

        session["attempts"] += 1
        attempts = session["attempts"]

        if guess < 1 or guess > max_num:
            message = f"❗Number must be between 1 and {max_num}."
        elif guess == number:
            end_time = time.time()
            time_taken = round(end_time - session["start_time"], 2)
            score = max(1000 - (attempts * 10 + int(time_taken)), 0)
            leaderboard.append({
                "name": session["name"],
                "difficulty": session["difficulty"],
                "attempts": attempts,
                "time": time_taken,
                "score": score
            })
            leaderboard.sort(key=lambda x: x["score"], reverse=True)

            message = f"🎉 Correct! You guessed {number} in {attempts} tries and {time_taken}s."
            emoji = "🏆"
            return render_template("play.html", message=message, win=True, score=score, emoji=emoji)

        elif guess < number:
            message = "⬇️ Too low! Try again."
            emoji = "😅"
        else:
            message = "⬆️ Too high! Try again."
            emoji = "🤔"

        # Hints
        if attempts >= 3:
            hint = "💡 Hint: The number is even." if number % 2 == 0 else "💡 Hint: The number is odd."
        if attempts >= 5:
            lower = max(1, number - 10)
            upper = min(max_num, number + 10)
            hint = f"💬 Hint: It’s between {lower} and {upper}."

    return render_template(
        "play.html",
        message=message,
        hint=hint,
        emoji=emoji,
        attempts=session["attempts"],
        max_num=session["max_num"]
    )

@app.route("/leaderboard")
def leaderboard_page():
    # Read filters from query params
    top = request.args.get("top")
    min_score = request.args.get("min_score")
    difficulty = request.args.get("difficulty")
    name = request.args.get("name")

    try:
        top = int(top) if top else None
    except ValueError:
        top = None
    try:
        min_score = int(min_score) if min_score else None
    except ValueError:
        min_score = None

    # Apply filters
    filtered = leaderboard
    if difficulty:
        filtered = [e for e in filtered if e.get("difficulty") == difficulty]
    if name:
        filtered = [e for e in filtered if name.lower() in e.get("name", "").lower()]
    if min_score is not None:
        filtered = [e for e in filtered if e.get("score", 0) >= min_score]

    # Sort by score desc
    sorted_entries = sorted(filtered, key=lambda x: x.get("score", 0), reverse=True)

    # Assign ranks (ties get same rank)
    ranked = []
    last_score = None
    rank = 0
    position = 0
    for e in sorted_entries:
        position += 1
        if last_score is None or e.get("score") != last_score:
            rank = position
            last_score = e.get("score")
        entry = e.copy()
        entry["rank"] = rank
        ranked.append(entry)

    if top is not None:
        ranked = ranked[:top]

    filters = {"top": top, "min_score": min_score, "difficulty": difficulty, "name": name}
    return render_template("leaderboard.html", leaderboard=ranked, filters=filters)


@app.route('/leaderboard/clear', methods=["POST"])
def leaderboard_clear():
    """Clear the in-memory leaderboard. Simple POST endpoint used by the UI."""
    global leaderboard
    leaderboard.clear()
    return redirect(url_for("leaderboard_page"))

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
