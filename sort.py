import sqlite3
import os


def rel(*x):
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

db_con = sqlite3.connect(rel("db/course-match.db"))

f = open(rel("tmp/index"), "r")
raw = f.read()
f.close()

user_id = raw

c = db_con.cursor()

get_courses_query = "SELECT * FROM courses WHERE user_id = " + str(user_id)

c.execute(get_courses_query)

search_strings = []
courses = []

if c.fetchone():
        c.execute(get_courses_query)
        for row in c:
                courses.append(row[0])
                strings = ["%" + row[1] + row[2] + "%", "%" + row[1] + " " + row[2] + "%", "%" + row[1] + "-" + row[2] + "%"]
                search_strings.append(strings)

        course_match_query = course_match_query = "SELECT * FROM mails WHERE user_id = " + user_id + " AND ("
        for strings in search_strings:
                # course_match_query = "SELECT * FROM mails WHERE user_id = " + user_id + " AND (subject LIKE IN " + strings + " OR message LIKE IN " + strings + ")"
                course_match_query += "(subject LIKE '" + strings[0] + "' OR message LIKE '" + strings[0] + "') OR "
                course_match_query += "(subject LIKE '" + strings[1] + "' OR message LIKE '" + strings[1] + "') OR "
                course_match_query += "(subject LIKE '" + strings[2] + "' OR message LIKE '" + strings[2] + "'))"

                print(course_match_query)
                c.execute(course_match_query)

                pair = {}
                all_mail = c.fetchall()
                for mail in all_mail:
                        pair['mail_id'] = str(mail[0])
                        pair['course_id'] = str(courses[search_strings.index(strings)])

                        check_if_relation_exists_query = "SELECT * FROM sorts WHERE mail_id='" + pair['mail_id'] + "' AND course_id = '" + pair["course_id"] + "'"
                        c.execute(check_if_relation_exists_query)

                        if not c.fetchone():
                                insert_relation_query = "INSERT INTO sorts ('id', 'mail_id', 'course_id') VALUES (null, " + pair['mail_id'] + "," + pair['course_id'] + ")"
                                c.execute(insert_relation_query)
                                db_con.commit()

os.system("rm -f " + rel("tmp/holder"))
