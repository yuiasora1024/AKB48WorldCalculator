import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, information, CreateCode, ReadCode

from itertools import combinations, product
import math
import time
from datetime import timedelta

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///akb48world.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """show the import/export to csv option """
    # ask for log in
    if not session["user_id"]:
        return redirect("/login")
    else:
        # show the import option
        # update entry if duplicate
        # show the export option
        user = db.execute(
            "select * from users where id=?", session["user_id"])
        return render_template("index.html", user=user)


@app.route("/input", methods=["GET", "POST"])
@login_required
def input():
    """enter each cards manually"""
    themes = information("themes")
    TeamA = information("TeamA")
    TeamK = information("TeamK")
    TeamB = information("TeamB")
    Team4 = information("Team4")
    Team8 = information("Team8")
    if request.method == "GET":
        # call the theme list
        return render_template("input.html", themes=themes, TeamA=TeamA, TeamK=TeamK, TeamB=TeamB, Team4=Team4, Team8=Team8)
    elif request.method == "POST":
        # check the type of data needed
        theme = request.form.get("theme")
        team = request.form.get("team")
        member = request.form.get("member")
        Singing = request.form.get("Singing", type=int)
        Dancing = request.form.get("Dancing", type=int)
        Variety = request.form.get("Variety", type=int)
        Style = request.form.get("Style", type=int)
        total = request.form.get("total", type=int)
        skill_type = request.form.get("skill_type")
        skill_target = request.form.get("skill_target")
        skill_rate = request.form.get("skill_rate", type=int)
        cheer = request.form.get("cheer")
        cheer_skill = request.form.get("cheer_skill")
        cheer_rate = request.form.get("cheer_rate", type=int)

        value = []

        value.extend([theme, team, member, Singing, Dancing, Variety, Style, total,
                      skill_type, skill_target, skill_rate, cheer, cheer_skill, cheer_rate])

        # check if everything empty
        for item in value:
            if item is None or 0:
                flash("You cannot leave any field empty!")
                return redirect(request.path)

        # write a program that translate Japanese name to English name and store in SQL
        themeCode = CreateCode("theme", theme)
        memberCode = CreateCode("member", member)
        cheerCode = CreateCode("member", cheer)

        if total != (Singing + Dancing + Variety + Style):
            flash("The attribute data does not match!")
            return redirect(request.path)

        if skill_rate > 100 or skill_rate <= 0 or cheer_rate > 100 or cheer_rate <= 0:
            flash("The rate data is problematic!")
            return redirect(request.path)

        # check duplicate
        table_name = "userID" + str(session["user_id"])
        duplicate_check = db.execute(
            "select * from ? where theme = ? and member = ?", table_name, themeCode, memberCode)
        if len(duplicate_check) > 0:
            db.execute(
                "update ? set Singing=?, Dancing=?, Variety=?, Style=?, skill_type=?, skill_target=?, skill_rate=?, cheer=?, cheer_skill=?, cheer_rate=?, total = ? where theme=? and member=?",
                table_name, Singing, Dancing, Variety, Style,
                skill_type, skill_target, skill_rate, cheerCode, cheer_skill, cheer_rate, total, themeCode, memberCode)
            flash("Your card has been updated!")
            return render_template("input2.html")
        else:
            # insert card data into table
            db.execute(
                "INSERT INTO ? (theme, team, member, Singing, Dancing , Variety, Style, skill_type, skill_target, skill_rate, cheer, cheer_skill, cheer_rate, total) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", table_name, themeCode, team, memberCode, Singing, Dancing, Variety, Style,
                skill_type, skill_target, skill_rate, cheerCode, cheer_skill, cheer_rate, total)
            flash("Your card has been saved!")
            return render_template("input2.html")


@app.route("/edit", methods=["POST"])
@login_required
def edit():
    id = request.form.get("id")
    theme = request.form.get("theme")
    team = request.form.get("team")
    member = request.form.get("member")
    Singing = request.form.get("Singing", type=int)
    Dancing = request.form.get("Dancing", type=int)
    Variety = request.form.get("Variety", type=int)
    Style = request.form.get("Style", type=int)
    skill_type = request.form.get("skill_type")
    skill_target = request.form.get("skill_target")
    skill_rate = request.form.get("skill_rate", type=int)
    cheer = request.form.get("cheer")
    cheer_skill = request.form.get("cheer_skill")
    cheer_rate = request.form.get("cheer_rate", type=int)

    table_name = "userID" + str(session["user_id"])

    update_check = db.execute("select * from ? where id=?", table_name, id)

    themeCode = CreateCode("theme", theme)
    memberCode = CreateCode("member", member)
    cheerCode = CreateCode("member", cheer)

    value = []

    value.extend([themeCode, team, memberCode, Singing, Dancing, Variety, Style,
                  skill_type, skill_target, skill_rate, cheerCode, cheer_skill, cheer_rate])

    value2 = ["theme", "team", "member", "Singing", "Dancing", "Variety", "Style",
              "skill_type", "skill_target", "skill_rate", "cheer", "cheer_skill", "cheer_rate"]

    for i in range(len(value)):
        if not value[i] or value[i] is None or 0:
            value[i] = update_check[0][value2[i]]

    total = value[4] + value[5] + value[6] + value[3]

    db.execute(
        "update ? set theme=?, team=?, member=?, Singing=?, Dancing=?, Variety=?, Style=?, skill_type=?, skill_target=?, skill_rate=?, cheer=?, cheer_skill=?, cheer_rate=?, total=? where id=?", table_name,
        value[0], value[1], value[2], value[3], value[4], value[5], value[6], value[7], value[8], value[9], value[10], value[11], value[12], total, id)

    flash("Your card has been updated!")
    return render_template("edit2.html")


@ app.route("/calculator", methods=["GET", "POST"])
@ login_required
def calculator():
    table_name = "userID" + str(session["user_id"])
    if request.method == "GET":
        return render_template("calculator.html")
    elif request.method == "POST":
        today_target = request.form.get("today_target")
        today_skill = request.form.get("today_skill")
        bonus_rate = (request.form.get("bonus_rate", type=int))/100
        Singing = (request.form.get("Singing", type=int))/100
        Dancing = (request.form.get("Dancing", type=int))/100
        Variety = (request.form.get("Variety", type=int))/100
        Style = (request.form.get("Style", type=int))/100
        target = request.form.get("target", type=int)
        opponent = request.form.get("opponent")
        level = request.form.get("level")
        production = request.form.get("production", type=int)

        cardbank = db.execute("select * from ?", table_name)

        # add weighting total
        # level weighting
        for i in range(len(cardbank)):
            cardbank[i]["Singing"] *= (1 + Singing)
            cardbank[i]["Dancing"] *= (1 + Dancing)
            cardbank[i]["Variety"] *= (1 + Variety)
            cardbank[i]["Style"] *= (1 + Style)

            cardbank[i]["Singing"] = int(cardbank[i]["Singing"])
            cardbank[i]["Dancing"] = int(cardbank[i]["Dancing"])
            cardbank[i]["Variety"] = int(cardbank[i]["Variety"])
            cardbank[i]["Style"] = int(cardbank[i]["Style"])

            cardbank[i]["Weighting Total"] = cardbank[i]["Singing"] + \
                cardbank[i]["Dancing"] + \
                cardbank[i]["Variety"] + \
                cardbank[i]["Style"]

            cardbank[i]["Total"] = cardbank[i]["Weighting Total"]

        # today's bonus
        for i in range(len(cardbank)):
            if level != "VS" and level != "SP":
                if cardbank[i]["team"] == today_target or today_target == "all":
                    if today_skill == "all":
                        cardbank[i]["Singing"] *= 1 + bonus_rate
                        cardbank[i]["Dancing"] *= 1 + bonus_rate
                        cardbank[i]["Variety"] *= 1 + bonus_rate
                        cardbank[i]["Style"] *= 1 + bonus_rate

                    else:
                        cardbank[i][today_skill] *= 1 + bonus_rate

                cardbank[i]["Singing"] = int(cardbank[i]["Singing"])
                cardbank[i]["Dancing"] = int(cardbank[i]["Dancing"])
                cardbank[i]["Variety"] = int(cardbank[i]["Variety"])
                cardbank[i]["Style"] = int(cardbank[i]["Style"])

                cardbank[i]["Today_Bonus"] = cardbank[i]["Singing"] + \
                    cardbank[i]["Dancing"] + \
                    cardbank[i]["Variety"] + \
                    cardbank[i]["Style"] - cardbank[i]["Weighting Total"]
                cardbank[i]["Total"] += cardbank[i]["Today_Bonus"]
            else:
                cardbank[i]["Today_Bonus"] = 0

        # add individual skill bonus
        for a in range(len(cardbank)):
            skill = cardbank[a]["skill_type"]
            rate = cardbank[a]["skill_rate"]
            if cardbank[a]["skill_target"] == "Herself":
                x = int(cardbank[a][skill]*((rate/100)))
                cardbank[a][skill] += x
                cardbank[a]["Skill_Total"] = x
            else:
                cardbank[a]["Skill_Total"] = 0
        """
        think about how to eliminate bad cards
        """

        cardlist = []

        cardbank1 = sorted(cardbank, key=lambda i: i['Total'], reverse=True)
        cardbank2 = []

        # if level != "Main" and level != "VS" and level != "SP":
        #     for a in range(len(cardbank1)):
        #         if cardbank1[a]["team"] == level:
        #             cardlist.append(a)
        #             cardbank2.append(cardbank1[a])
        # else:
        #     for a in range(len(cardbank1)):
        #         cardlist.append(a)
        #         cardbank2.append(cardbank1[a])

        x = min(15, len(cardbank1))

        if level != "Main" and level != "VS" and level != "SP":
            for a in range(len(cardbank1)):
                if cardbank1[a]["team"] == level:
                    cardlist.append(a)
                    cardbank2.append(cardbank1[a])
        else:
            for a in range(x):
                cardlist.append(a)
                cardbank2.append(cardbank1[a])

            if len(cardbank1) > 15:
                for a in range(len(cardbank1)):
                    for b in range(16, len(cardbank)):
                        if cardbank1[a]["id"] == cardbank1[b]["cheer"]:
                            if cardbank1[b]["Total"] * 2 > cardbank1[0]["Total"]:
                                cardlist.append(b)
                                cardbank2.append(cardbank1[a])

        if len(cardbank2) < 8:
            flash("You need to have at least 8 eligible cards to run the simulator!")
            return render_template("input.html")

        for i in range(len(cardbank2)):
            cardbank2[i]["theme"] = ReadCode(
                "theme", int(cardbank2[i]["theme"]))
            cardbank2[i]["member"] = ReadCode(
                "member", int(cardbank2[i]["member"]))
            cardbank2[i]["cheer"] = ReadCode(
                "member", int(cardbank2[i]["cheer"]))

        combination1 = list(combinations(cardlist, 4))
        combination2 = list(combinations(cardlist, 4))
        combination3 = list(product(combination1, combination2))
        combination = []

        for i in range(len(combination3)):
            x = combination3[i][0] + combination3[i][1]
            if len(set(x)) == len(x):
                x_member = [cardbank2[x[0]]["member"], cardbank2[x[1]]["member"], cardbank2[x[2]]["member"], cardbank2[x[3]]["member"],
                            cardbank2[x[4]]["member"], cardbank2[x[5]
                                                                 ]["member"],
                            cardbank2[x[6]]["member"], cardbank2[x[7]]["member"]]
                if len(x_member) == len(set(x_member)):
                    combination.append(x)

        # check name duplicate

        best_card = []
        best_stat = {'Weighting Total': 0, 'Total': 0, 'Unlucky Total': 0, 'team_bonus': 0,
                     'power_ranking_bonus': 0, 'theme_bonus': 0, 'leader': 0, 'support_total': 0, 'Today_Bonus': 0, 'Target': target}
        current_card = []
        current_stat = {"Weighting Total": 0, 'Total': 0, 'Unlucky Total': 0, 'team_bonus': 0,
                        'power_ranking_bonus': 0, 'theme_bonus': 0, 'leader': 0, 'support_total': 0, 'Today_Bonus': 0, 'Target': target}

        cardbank3 = []

        for i in range(len(combination)):

            cardbank3.clear()
            current_stat.clear()
            current_card.clear()

            for item in current_stat:
                current_stat[item] = 0

            for a in range(len(cardbank2)):
                d2 = cardbank2[a].copy()
                cardbank3.append(d2)

            for a in range(8):
                current_card.append(cardbank3[combination[i][a]])

            current_stat["Total"] = production
            current_stat["Weighting Total"] = 0
            current_stat["Today_Bonus"] = 0

            for a in range(4):
                current_stat["Total"] += current_card[a]["Total"]
                current_stat["Weighting Total"] += current_card[a]["Weighting Total"]
                current_stat["Today_Bonus"] += current_card[a]["Today_Bonus"]

            # same team +5% + power ranking between different teams
            power_ranking = ["TeamA", "TeamK", "TeamB", "Team4", "Team8"]
            if current_card[0]["team"] == current_card[1]["team"] == current_card[2]["team"] == current_card[3]["team"]:
                current_stat["team_bonus"] = int(current_stat["Total"] * 0.05)
                current_stat["Total"] += current_stat["team_bonus"]
                for a in range(5):
                    if (current_card[0]["team"] == power_ranking[a] and opponent == power_ranking[a+1]) or (current_card[0]["team"] == "Team8" and opponent == "TeamA"):
                        current_stat["power_ranking_bonus"] = int(
                            current_stat["Total"] * 0.2)
                    elif (current_card[0]["team"] == power_ranking[a] and opponent == power_ranking[a-1]) or (current_card[0]["team"] == "TeamA" and opponent == "Team8"):
                        current_stat["power_ranking_bonus"] = int(
                            current_stat["Total"] * -0.2)
                    else:
                        current_stat["power_ranking_bonus"] = 0
                current_stat["Total"] += current_stat["power_ranking_bonus"]
            else:
                current_stat["team_bonus"] = 0
                current_stat["power_ranking_bonus"] = 0

            current_stat["theme_bonus"] = 0
            # same theme +5%
            if current_card[0]["theme"] == current_card[1]["theme"] == current_card[2]["theme"] == current_card[3]["theme"]:
                current_stat["theme_bonus"] = int(current_stat["Total"] * 0.05)
                current_stat["Total"] += current_stat["theme_bonus"]

            # check team skill
            for a in range(4):
                skill = current_card[a]["skill_type"]
                rate = current_card[a]["skill_rate"]/100
                if current_card[a]["skill_target"] == "Her Team":
                    for b in range(4):
                        if current_card[a]["team"] == current_card[b]["team"]:
                            x = int(current_card[b][skill] * rate)
                            current_card[a]["Skill_Total"] += x
                            current_card[a]["Skill_Total"] = int(
                                current_card[a]["Skill_Total"])
                current_card[a]["Total"] += int(current_card[a]["Skill_Total"])

            # prepare for unlucky total
            current_stat["Unlucky Total"] = current_stat["Total"]

            max_value = 0
            current_stat["Skill_Total"] = 0
            for a in range(4):
                if current_card[a]["Skill_Total"] > max_value:
                    max_value = current_card[a]["Skill_Total"]
                    current_stat["leader"] = current_card[a]["member"]
                current_stat["Total"] += current_card[a]["Skill_Total"]
                current_stat["Skill_Total"] += current_card[a]["Skill_Total"]

            current_stat["Unlucky Total"] += max_value

            # support
            for a in range(4, 8):
                current_card[a]["Total"] = int(
                    current_card[a]["Weighting Total"] * 0.1)

            for b in range(4, 8):
                current_card[b]["Cheer"] = "No"
                for a in range(4):
                    if current_card[a]["member"] == current_card[b]["cheer"]:
                        skill = current_card[b]["cheer_skill"]
                        current_card[b]["Total"] += int(current_card[b][skill] *
                                                        (current_card[b]["cheer_rate"]/100))
                        current_card[b]["Cheer"] = current_card[a]["member"]

            current_stat["support_total"] = 0
            for a in range(4, 8):
                current_stat["support_total"] += current_card[a]["Total"]

            current_stat["Total"] += current_stat["support_total"]
            current_stat["Unlucky Total"] += current_stat["support_total"]

            # check highest score
            # check if the score can pass even no skill was activated

            # current_stat["Skill_score_except_leader"]
            if (best_stat["Unlucky Total"] < target and current_stat["Total"] > best_stat["Total"]) or ((current_stat["Total"] > best_stat["Total"]) and current_stat["Unlucky Total"] >= target):
                best_stat.update(current_stat)
                best_card.clear()
                for a in range(len(current_card)):
                    d2 = current_card[a].copy()
                    best_card.append(d2)

        if best_stat["Total"] < target:
            flash("Can't find any winning outcome! Here is the best possible result.")

        elif best_stat["Total"] > target and (best_stat["Unlucky Total"]) < target:
            flash(
                "You may pass the level but you will need some luck! Here is the best possible result.")

        elif (best_stat["Unlucky Total"]) >= target:
            flash(
                "You have very high chance to pass the level! Here is the best result. ")
        return render_template("calculator_result.html", best_stat=best_stat, best_card=best_card)


@ app.route("/card", methods=["GET", "POST"])
@ login_required
def card():
    """show the card collection and allow edit/delete"""
    table_name = "userID" + str(session["user_id"])
    if request.method == "GET":
        card1 = db.execute("select * from ?",
                           table_name)
        order = {'A': 4, 'K': 3, 'B': 2, '4': 1, '8': 0}
        cards = sorted(card1, key=lambda i: (
            order[i['team']], i['Total']), reverse=True)
        for i in range(len(cards)):
            cards[i]["theme"] = ReadCode("theme", int(cards[i]["theme"]))
            cards[i]["member"] = ReadCode("member", int(cards[i]["member"]))
            cards[i]["cheer"] = ReadCode("member", int(cards[i]["cheer"]))
        return render_template("card.html", cards=cards)
    elif request.method == "POST":
        id = request.form.get("card")
        check = db.execute("select * from ? where id = ?", table_name, id)
        if len(check) == 0:
            flash("Card ID is invalid!")
            return redirect(request.path)
        else:
            if request.form.get('edit') == 'edit':
                card = db.execute("select * from ? where id=?",
                                  table_name, id)
                for i in range(len(card)):
                    themes = information("themes")
                    TeamA = information("TeamA")
                    TeamK = information("TeamK")
                    TeamB = information("TeamB")
                    Team4 = information("Team4")
                    Team8 = information("Team8")
                    card[i]["theme"] = ReadCode("theme", int(card[i]["theme"]))
                    card[i]["member"] = ReadCode(
                        "member", int(card[i]["member"]))
                    card[i]["cheer"] = ReadCode(
                        "member", int(card[i]["cheer"]))
                    return render_template("edit.html", card=card, themes=themes, TeamA=TeamA, TeamK=TeamK, TeamB=TeamB, Team4=Team4, Team8=Team8, id=id)
            elif request.form.get('delete') == 'delete':
                db.execute("delete from ? where id=?", table_name, id)
                flash("Your card has been deleted!")
                return render_template("edit2.html")


"""
@ app.route("/weakness", methods=["GET"])
@ login_required
def weakness():
    table_name = "userID" + str(session["user_id"])
    cardbank = db.execute("select * from ?", table_name)
"""

# show the four card with highest singing, dancing, variety, style
# show the four card with highest(singing+dancing), etc.


@ app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username")
            return redirect(request.path)

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password")
            return redirect(request.path)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get(
                "username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("invalid username and/or password")
            return redirect(request.path)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@ app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@ app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # -check birthdays -
    # when requested via GET, display registration form
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")

        # When form is submitted via post, check for possible errors and insert the new user into users table. If error, return 400
        # any field left back
        if not username or not password or not confirm_password:
            flash("You cannot leave any blank empty!")
            return redirect(request.path)
        # password and confirmation didn't match
        elif not (password == confirm_password):
            flash("Please confirm your password.")
            return redirect(request.path)
        # username being taken
        elif len(db.execute("SELECT * FROM users WHERE username=?", username)) != 0:
            flash("The username has been taken.")
            return redirect(request.path)
        # only store the hashed password
        # log user in
        else:
            hash = generate_password_hash(password)
            db.execute(
                "INSERT INTO users (username, hash) VALUES(?, ?)", username, hash
            )
            # create SQL table for the user
            user_id = db.execute(
                "SELECT * FROM users WHERE username=?", username)

            name = "userID" + str(user_id[0]["id"])
            # edit the line according to the data we needed
            db.execute(
                "CREATE TABLE ? (id INTEGER, theme TEXT NOT NULL, team CHAR NOT NULL, member TEXT, Singing INT , Dancing INT, Variety INT, Style INT, skill_type TEXT, skill_target TEXT, skill_rate FLOAT, cheer TEXT, cheer_skill TEXT, cheer_rate FLOAT, total NUMERIC, PRIMARY KEY(id))",
                name
            )
            return render_template("index.html")
