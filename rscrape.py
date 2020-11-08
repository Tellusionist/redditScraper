import praw
import os
import sqlite3
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase


def scrape_new_posts(subreddit_name='lfg', post_limit=5):
    reddit = praw.Reddit(client_id=os.environ['CLIENT_ID'], 
                        client_secret=os.environ['CLIENT_SECRET'], 
                        user_agent='custom_notify'
                        )

    sreddit = reddit.subreddit(subreddit_name)

    return sreddit.new(limit=post_limit)

def create_sql_connection(SQL_DB='reddit.db'):
    return sqlite3.connect(SQL_DB)

def import_posts(new_posts, conn):
    try:
        c = conn.cursor()
        for post in new_posts:
            subr = post.subreddit_name_prefixed
            pid = post.id
            created = post.created_utc
            flair = post.link_flair_text
            title = post.title.replace("'","''")
            #content = post.selftext.replace("'","''") # Should I limit or even store this?
            url = post.url
            
            if flair == 'Player(s) wanted':
                flg_flair = 1
            else:
                flg_flair = 0
            
            if '5e' in title.lower():
                flg_5e = 1
            else:
                flg_5e = 0

            if 'pbp' in title.lower():
                flg_pbp = 1
            else:
                flg_pbp = 0

            sql = f"INSERT INTO posts_stg VALUES ('{subr}','{pid}',{created},'{flair}','{title}',{flg_flair},{flg_5e},{flg_pbp},'{url}')"
            c.execute(sql)
            conn.commit()

    except sqlite3.Error as e:
        print("Insertion error:", e)
        
def delete_dupe_posts(conn):
    try:
        c = conn.cursor()
        sql = 'Delete from posts_stg where post_id in (select post_id from posts);'
        c.execute(sql)
        conn.commit()
    except sqlite3.Error as e:
        print("Dedupe error:", e)

def check_for_desired_posts(conn):
    c = conn.cursor()
    sql = 'select title, url, created from posts_stg where flg_player = 1 and flg_5e = 1 and flg_pbp = 1;'
    c.execute(sql)
    results = c.fetchall()

    if len(results) > 0:
        return results

def archive_new_posts(conn):
    c = conn.cursor()
    sql = 'Insert into posts select * from posts_stg;'
    c.execute(sql)
    conn.commit()
    sql = 'Delete from posts_stg'
    c.execute(sql)
    conn.commit()

def build_email_content(posts):
    body = ''
    for row in posts:
        title = row[0]
        url = row[1]
        created = time.strftime('%h %d %H:%M', time.localtime(row[2]))
        body += f'<p><strong>Title:</strong> {title}<br /><strong>Posted:</strong> {created}<br />{url}<br /></p>'
    return body

def send_email(subject, body):
    from_addr = 'Reddit_Scrape@Tellusion.ai'
    to_addr = 'timothy.b.lee21@gmail.com'
    
    msg = MIMEMultipart() 
    msg['From'] = from_addr 
    msg['To'] = to_addr 
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html')) 
    
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls() 
    s.login('timothy.b.lee21@gmail.com', os.environ['GMAIL_PASS']) 
    text = msg.as_string() 
    s.sendmail(from_addr, to_addr, text)
    s.quit()


if __name__ == '__main__':
    print('Scraping new reddit posts')
    new_posts = scrape_new_posts('lfg',5)
    conn = create_sql_connection()
    import_posts(new_posts, conn)
    delete_dupe_posts(conn)
    good_posts = check_for_desired_posts(conn)
    archive_new_posts(conn)
    if not good_posts is None:
        body = build_email_content(good_posts)
        send_email('New LFG Posts', body)
        print('New posts found')

