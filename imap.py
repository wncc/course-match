import imaplib
import email
import sqlite3

#############################
#############################


def get_first_text_block(email_message_instance):
        maintype = email_message_instance.get_content_maintype()
        if maintype == 'multipart':
                for part in email_message_instance.get_payload():
                        if part.get_content_maintype() == 'text':
                                return part.get_payload()
        elif maintype == 'text':
                return email_message_instance.get_payload()

f = open("tmp/holder", "r")
raw = f.read()
f.close()

con = raw.split("$$$")

mailbox = imaplib.IMAP4(con[0], con[1])

mailbox.login(con[2], con[3])

db_con = sqlite3.connect("db/course-match.db")

user_id = con[4]

c = db_con.cursor()		# c is the DATABASE CURSOR

check_for_previous_mails_query = "SELECT  *  FROM mails WHERE user_id=?"
c.execute(check_for_previous_mails_query, (user_id,))

if not c.row_count:
                result, raw_list = mailbox.uid("search", None, "ALL")
                id_list = raw_list[0].split()
                for index in id_list:
                        result, tmp = mailbox.uid('fetch', index, "(RFC822)")
                        raw_email = tmp[0][1]
                        email_message = email.message_from_string(raw_email)
                        del(raw_email)
                        del(tmp)
                        mail = []
                        mail['to'] = email_message['To']
                        mail['from'] = email_message['From']
                        mail['received'] = email_message['Date']
                        mail['subject'] = email_message['Subject']
                        mail['cc'] = email_message['Cc']
                        mail['bcc'] = email_message['Bcc']
                        mail['message'] = get_first_text_block(email_message)
                        mail['uid'] = index
                        mail['user_id'] = user_id
                        mail['read'] = True

                        if(email_message['Content-Type'].find("multipart") or email_message['Content-Type'].find("multipart") or email_message['Content-Type'].find("multipart")):
                                mail['has_attachment'] = False
                        else:
                                mail['has_attachment'] = True

                        #Inserting into mails
                        mail_insert_query = 'INSERT INTO mails VALUES(%s)' % ','.join(['?'] * len(mail))
                        c.execute(mail_insert_query, mail)
                        db_con.commit()

else:
        last_mail_id_query = 'SELECT * FROM `mails` ORDER BY id DESC LIMIT 1'
        c.execute(last_mail_id_query)

        for row in c:
                last_id = int(row[1])

        result, raw_list = mailbox.uid("search", None, "ALL")
        id_list = raw_list[0].split()
        for index in id_list:
                if int(index) < int(last_id):
                        continue

                result, tmp = mailbox.uid('fetch', index, "(RFC822)")
                raw_email = tmp[0][1]
                email_message = email.message_from_string(raw_email)
                del(raw_email)
                del(tmp)
                mail = []
                mail['to'] = email_message['To']
                mail['from'] = email_message['From']
                mail['received'] = email_message['Date']
                mail['subject'] = email_message['Subject']
                mail['cc'] = email_message['Cc']
                mail['bcc'] = email_message['Bcc']
                mail['message'] = get_first_text_block(email_message)
                mail['uid'] = index
                mail['course'] = ''
                mail['user_id'] = user_id
                mail['read'] = True

                if(email_message['Content-Type'].find("multipart") or email_message['Content-Type'].find("multipart") or email_message['Content-Type'].find("multipart")):
                        mail['has_attachment'] = False
                else:
                        mail['has_attachment'] = True

                #Inserting into mails
                mail_insert_query = 'INSERT INTO mails VALUES(%s)' % ','.join(['?'] * len(mail))
                c.execute(mail_insert_query, mail)
                con.commit()

