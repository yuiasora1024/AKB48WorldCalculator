import os
from cs50 import SQL
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

from itertools import combinations

db = SQL("sqlite:///akb48world.db")


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def CreateCode(type, name):
    # if update, please update def information as well
    # new item added to the last since the index is purely based to list order
    themes = ["", "海へ行こう！", "#今日のコーデ", "公演は続く", "Trick or Treat!", "初公演の衣装", "I want you!",
              "Please！私も見て", "夢にもっと近く", "静かな公園で", "桜並木の花", "思い出の一枚", "あなたとクリスマス", "幸せのサプライズ", "楽しい夜のひと時", "Sweet Valentine"]
    member = ["", "鈴木くるみ", "道枝咲", "田口愛佳", "千葉恵里", "西川怜", "篠崎彩奈", "山根涼羽", "佐藤美波", "向井地美音", "宮崎美穂", "加藤玲奈", "横山由依", "市川愛美", "込山榛香", "長友彩海", "武藤小麟", "武藤十夢", "茂木忍", "安田叶", "湯本亜美", "岩立沙穂", "大盛真歩", "大家志津香", "柏木由紀",
              "久保怜音", "佐々木優佳里",  "谷口めぐ",  "中西智代梨", "福岡聖菜", "浅井七海", "稲垣香織", "岡田奈々", "佐藤妃星", "馬嘉伶", "村山彩希", "山内瑞葵", "坂口渚沙", "横山結衣", "岡部麟", "髙橋彩音", "吉川七瀬",  "小栗有以", "小田えりな", "大西桃香", "濵咲友菜", "下尾みう", "行天優莉奈", "倉野尾成美"]

    if type == "theme":
        index = themes.index(name)
        if not themes.index(name):
            return None
        return index
    elif type == "member":
        index = member.index(name)
        if not member.index(name):
            return None
        return index
    else:
        return None


def ReadCode(type, index):
    # if update, please update def information and def CreateCode as well
    # new item added to the last since the index is purely based to list order
    themes = ["", "海へ行こう！", "#今日のコーデ", "公演は続く", "Trick or Treat!", "初公演の衣装", "I want you!",
              "Please！私も見て", "夢にもっと近く", "静かな公園で", "桜並木の花", "思い出の一枚", "あなたとクリスマス", "幸せのサプライズ", "楽しい夜のひと時", "Sweet Valentine"]
    member = ["", "鈴木くるみ", "道枝咲", "田口愛佳", "千葉恵里", "西川怜", "篠崎彩奈", "山根涼羽", "佐藤美波", "向井地美音", "宮崎美穂", "加藤玲奈", "横山由依", "市川愛美", "込山榛香", "長友彩海", "武藤小麟", "武藤十夢", "茂木忍", "安田叶", "湯本亜美", "岩立沙穂", "大盛真歩", "大家志津香", "柏木由紀",
              "久保怜音", "佐々木優佳里",  "谷口めぐ",  "中西智代梨", "福岡聖菜", "浅井七海", "稲垣香織", "岡田奈々", "佐藤妃星", "馬嘉伶", "村山彩希", "山内瑞葵", "坂口渚沙", "横山結衣", "岡部麟", "髙橋彩音", "吉川七瀬",  "小栗有以", "小田えりな", "大西桃香", "濵咲友菜", "下尾みう", "行天優莉奈", "倉野尾成美"]
    if type == "theme":
        return themes[index]
    elif type == "member":
        return member[index]


def information(s):
    themes = ["海へ行こう！", "#今日のコーデ",
              "公演は続く", "Trick or Treat!", "初公演の衣装", "I want you!", "Please！私も見て", "夢にもっと近く", "静かな公園で", "桜並木の花", "思い出の一枚", "あなたとクリスマス", "幸せのサプライズ", "楽しい夜のひと時", "Sweet Valentine"]

    TeamA = ["鈴木くるみ", "道枝咲", "田口愛佳", "千葉恵里", "西川怜", "篠崎彩奈",
             "山根涼羽", "佐藤美波", "向井地美音", "宮崎美穂", "加藤玲奈", "横山由依"]

    TeamK = ["市川愛美", "込山榛香", "長友彩海",
             "武藤小麟", "武藤十夢", "茂木忍", "安田叶", "湯本亜美"]

    TeamB = ["岩立沙穂", "大盛真歩", "大家志津香", "柏木由紀",  "久保怜音",
             "佐々木優佳里",  "谷口めぐ",  "中西智代梨", "福岡聖菜"]

    Team4 = ["浅井七海", "稲垣香織", "岡田奈々",
             "佐藤妃星", "馬嘉伶", "村山彩希", "山内瑞葵"]

    Team8 = ["坂口渚沙", "横山結衣", "岡部麟", "髙橋彩音", "吉川七瀬",  "小栗有以",
             "小田えりな", "大西桃香", "濵咲友菜", "下尾みう", "行天優莉奈", "倉野尾成美"]

    if s == "themes":
        return themes
    elif s == "TeamA":
        return TeamA
    elif s == "TeamK":
        return TeamK
    elif s == "TeamB":
        return TeamB
    elif s == "Team4":
        return Team4
    elif s == "Team8":
        return Team8
    else:
        return None
