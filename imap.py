import imaplib
import email
import os
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table
from sqlalchemy import Integer, String
from sqlalchemy.sql import select


def rel(*x):
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

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

f = open(rel("tmp/holder"), "r")
raw = f.read()
f.close()

con = raw.split("$$$")

mailbox = imaplib.IMAP4(con[0], con[1])

mailbox.login(con[2], con[3])

mailbox.select()

engine = create_engine("sqlite:///db/course-match.db", echo=False)
# Session = sqlalchemy.orm.sessionmaker(bind=engine)
metadata = MetaData(bind=engine)


mails_table = Table('mails', metadata, autoload=True)

s = select([mails_table])
result = s.execute()

user_id = con[4]

if not result.first():
                result, raw_list = mailbox.uid("search", None, "ALL")
                id_list = raw_list[0].split()
                for index in id_list:
                        result, tmp = mailbox.uid('fetch', index, "(RFC822)")
                        raw_email = tmp[0][1]
                        email_message = email.message_from_string(raw_email)
                        del(raw_email)
                        del(tmp)
                        ############################################################################
                        mail = {}
                        mail['to'] = email_message['To']
                        mail['from'] = email_message['From']
                        mail['date'] = email_message['Date']
                        mail['subject'] = email_message['Subject']
                        mail['cc'] = str(email_message['Cc'])
                        mail['bcc'] = str(email_message['Bcc'])
                        mail['message'] = unicode(str(get_first_text_block(email_message)), errors='ignore')
                        if(len(mail['message']) > 2000):
                                mail['message'] = unicode('Message too long. IMAP.IITB.AC.IN denied to fetch.')
                        mail['uid'] = index
                        mail['user_id'] = user_id
                        mail['read'] = 1

                        if(str(email_message['Content-Type']).find("multipart") != -1 or str(email_message['Content-Type']).find("Multipart") != -1 or str(email_message['Content-Type']).find("MULTIPART") != -1):
                                mail['has_attachment'] = 1
                        else:
                                mail['has_attachment'] = 0

                        print(index)
                        i = mails_table.insert()
                        new_mail = i.values(mail)
                        con = engine.connect()
                        engine.execute(new_mail)

else:
        s = select([mails_table])
        result = s.execute()

        for row in result:
                if not row:
                        print('')
        last_id = row[1]

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
                ############################################################################
                mail = {}
                mail['to'] = email_message['To']
                mail['from'] = email_message['From']
                mail['date'] = email_message['Date']
                mail['subject'] = email_message['Subject']
                mail['cc'] = str(email_message['Cc'])
                mail['bcc'] = str(email_message['Bcc'])
                mail['message'] = unicode(str(get_first_text_block(email_message)), errors='ignore')
                if(len(mail['message']) > 2000):
                        mail['message'] = unicode('Message too long. IMAP.IITB.AC.IN denied to fetch.')
                mail['uid'] = index
                mail['user_id'] = user_id
                mail['read'] = 0

                if(str(email_message['Content-Type']).find("multipart") != -1 or str(email_message['Content-Type']).find("Multipart") != -1 or str(email_message['Content-Type']).find("MULTIPART") != -1):
                        mail['has_attachment'] = 1
                else:
                        mail['has_attachment'] = 0

                print(index)
                i = mails_table.insert()
                new_mail = i.values(mail)
                con = engine.connect()
                engine.execute(new_mail)
