import sqlite3

db_con = sqlite3.connect("db/course-match.db")

c = db_con.cursor()

get_courses_query = "SELECT * FROM courses"

c.execute(get_courses_query)

search_strings = []

if c.row_count:
        search_strings = []
