import praw
import os
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

SQL_DB = 'reddit.db'

def pull_new_posts(subreddit_name='lfg', post_limit=5):
    reddit = praw.Reddit(client_id=os.environ['CLIENT_ID'], 
                        client_secret=os.environ['CLIENT_SECRET'], 
                        user_agent='custom_notify'
                        )

    sreddit = reddit.subreddit(subreddit_name)

    return sreddit.new(limit=post_limit)

def stage_posts(new_posts):
    try:
        conn = sqlite3.connect(SQL_DB)
        c = conn.cursor()
        for post in new_posts:
            pid = post.id
            created = post.created_utc
            flair = post.link_flair_text
            title = post.title.replace("'","''")
            content = post.selftext.replace("'","''") # Should I limit or even store this?
            
            if flair == 'Player(s) wanted':
                flg_flair = 1
            else:
                flg_flair = 0
            
            if '[5e]' in title.lower():
                flg_5e = 1
            else:
                flg_5e = 0

            if '[5e]' in title.lower():
                flg_pbp = 1
            else:
                flg_pbp = 0

            sql = f"INSERT INTO posts_stg VALUES ('{pid}',{created},'{flair}','{title}',{flg_flair},{flg_5e},{flg_pbp},'{content}')"
            c.execute(sql)
            conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print("Staging Insertion error:", e)
        
def check_for_new_posts():
    pass

def build_email_content(posts):
    pass

def send_email(subject, body):
    from_addr = 'timothy.b.lee21@gmail.com'
    to_addr = 'timothy.b.lee21@gmail.com'
    
    msg = MIMEMultipart() 
    msg['From'] = from_addr 
    msg['To'] = to_addr 
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html')) 
    
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls() 
    s.login(fromaddr, os.environ['GMAIL_PASS']) 
    text = msg.as_string() 
    s.sendmail(fromaddr, toaddr, text)
    s.quit()


if __name__ == '__main__':
    new_posts = pull_new_posts()
    stage_posts(new_posts)
    check_for_new_posts()
    #build_email_content(posts)
    #send_email()