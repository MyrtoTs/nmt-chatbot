import json
import sqlite3
import string
from langdetect import detect
from urlextract import URLExtract

database_path = '/home/myrto/pink_dir/github/DataFiles/december_17_db.db'
combined_file_path = '/home/myrto/pink_dir/RC_2017-12'

print('\n\n     CREATING SQLITE DATABASE      \n\n')

sql_t = []
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS parents(id TEXT PRIMARY KEY,
                                                          reply_id TEXT,
                                                          post_body TEXT,
                                                          subreddit TEXT,
                                                          created_utc INT,
                                                          score INT,
                                                          length INT)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS replies(id TEXT PRIMARY KEY,
                                                          post_body TEXT,
                                                          subreddit TEXT,
                                                          created_utc INT,
                                                          score INT,
                                                          length INT)""")

# go through the data

row_counter = 0  # counter for the rows
paired_rows = 0  # counter for rows that are paired, as in question-answer

a = string.printable + '’‘“”'
eng_char = set(a)

extractor = URLExtract()

def acceptable_comment(body):
    """basic test to see if comment is not too short or too long"""
    if (len(body.split(' ')) > 100) or (len(body) < 4):
        return False
    elif len(body) > 3000:
        return False
    elif (body == '[deleted]' or body == '[removed]' or body.isspace()==True):
        return False
    elif len(extractor.find_urls(body))>0:
        return False
    elif not(set(body).issubset(eng_char)):
#         print('not only english characters')
        return False
    else:
        try:
            language = detect(body)
        except:
            return False
        if language != 'en':
            return False
    return True

def clear_comment(body):
    """basic test if a comment is insulting"""
    if (('fuck' or 'shit' or 'ass' or 'bitch' or 'nigga' or 'hell' or 'whore' or 'dick' or 'piss' or 'pussy') in body.lower()):
        return False
    return True
        
def sanitize_body(body):
    """sanitize body of reddit posts"""
    body = body.replace('\n', ' newlinechar ')
    body = body.replace('\r', ' newlinechar ')
    body = body.replace('"', "'")
    while '....' in body:
        body=body.replace('....','...') 
    while '  ' in body:
        body = body.replace('  ',' ')
    while 'newlinechar newlinechar' in body:
        body=body.replace('newlinechar newlinechar', 'newlinechar ') 
    return body


def transaction_bldr(sql):
    global sql_t
    sql_t.append(sql)
    if len(sql_t) > 10000:
        cursor.execute('BEGIN TRANSACTION')
        for s in sql_t:
            cursor.execute(s)
        conn.commit()
        sql_t = []


def sql_insert_parent(id, reply_id, post_body, subreddit, created_utc, score,length):
    sql = """INSERT INTO parents (id, reply_id, post_body, subreddit, created_utc, score, length) VALUES ("{}","{}","{}","{}",{},{},{});""".format(
        id, reply_id, post_body, subreddit, created_utc, score,length)
    transaction_bldr(sql)


def sql_insert_reply(id, post_body, subreddit, created_utc, score,length):
    sql = """INSERT INTO replies (id, post_body, subreddit, created_utc, score,length) VALUES ("{}","{}","{}",{},{},{});""".format(
        id, post_body, subreddit, created_utc, score,length)
    transaction_bldr(sql)


# dictionary that matches each post to its highest score response
post_pairs = {}
rejected_ids = []

print('\n\n Accept and reject comments \n\n')

with open(combined_file_path, buffering=1000000) as f:
    for row in f:
        row_counter += 1
        if row_counter % 1000000 == 0:
            print('Working on row {}'.format(row_counter))
        row = json.loads(row)
        id = row['id']
        comment_body = sanitize_body(row['body'])
        score = row['score']

        ### check comments ###
                
        if not(score>2 and acceptable_comment(comment_body) and clear_comment(comment_body)):
            rejected_ids.append(id)

print('\n Create comment pairs \n\n')

row_counter = 0

with open(combined_file_path, buffering=1000000) as f:
    for row in f:
        row_counter += 1
        if row_counter % 1000000 == 0:
            print('Working on row {}'.format(row_counter))
        row = json.loads(row)
        id = row['id']
        parent_id = row['parent_id'].split('_')[1]
        comment_body = sanitize_body(row['body'])
        score = row['score']

        ### check comments ###
            
        if parent_id not in rejected_ids:
            if parent_id not in post_pairs:
                post_pairs[parent_id] = (id, score)
            else:
                other_id, other_score = post_pairs[parent_id]
                if score > other_score:
                    post_pairs[parent_id] = (id, score)

                        
print('\n\nWe have {} post pairs\n\n'.format(len(post_pairs)))

print('\n\n     DATABASE INSERTION      \n\n')

parent_ids = set(post_pairs.keys())
reply_ids = set(x[0] for x in post_pairs.values())

row_counter = 0

with open(combined_file_path, buffering=1000000) as f:
    for row in f:
        row_counter += 1
        if row_counter % 1000000 == 0:
            print('Working on row {}'.format(row_counter))
        row = json.loads(row)
        id = row['id']
        post_body = sanitize_body(row['body'])
        subreddit = row['subreddit']
        created_utc = row['created_utc']
        score = row['score']
        length = len(post_body.split(' '))
        
        if id in parent_ids:
            # it's a parent
            sql_insert_parent(id, post_pairs[id][0], post_body, subreddit,
                              created_utc, score, length)
        if id in reply_ids:
            # it's a reply
            sql_insert_reply(id, post_body, subreddit, created_utc, score,length)
        

cursor.close()
