import sqlite3
import os


def rel(*x):
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

db_con = sqlite3.connect(rel("db/course-match.db"))

f = open(rel("tmp/holder"), "r")
raw = f.read()
f.close()

con = raw.split("$$$")
user_id = con[4]

c = db_con.cursor()

get_courses_query = "SELECT * FROM courses WHERE user_id = " + con[4]

c.execute(get_courses_query)

search_strings = []
courses = []

if c.rowcount:
        for row in c:
                courses.append(row[0])
                strings = "(%" + row[1] + row[2] + "%, %" + row[1] + " " + row[2] + "%, %" + row[1] + "-" + row[2] + "%)"
                search_strings.append(strings)

        for strings in search_strings:
                course_match_query = "SELECT * FROM mails WHERE user_id = " + con[4] + " AND (subject LIKE IN values " + strings + "OR message LIKE IN values " + strings + ")"
                c.execute(course_match_query)

                pair = {}
                for mail in c:
                        pair['mail_id'] = mail[0]
                        pair['course_id'] = search_strings.index(strings)

                        check_if_relation_exists_query = "SELECT * FROM sorts WHERE mail_id = " + pair['mail_id'] + "AND course_id = " + pair["course_id"]
                        c.execute(check_if_relation_exists_query)

                        if c.rowcount == -1:
                                insert_relation_query = 'INSERT INTO sorts VALUES(%s)' % ','.join(['?'] * len(pair))
                                c.execute(insert_relation_query, pair.values())
                                db_con.commit()

os.system("rm -f " + rel("tmp/holder"))
