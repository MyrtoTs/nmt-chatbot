import sqlite3
import random

LDA_corpus_path = '/home/myrto/pink_dir/github/'
database_path = '/home/myrto/pink_dir/github/decem_17_db.db'

conn = sqlite3.connect(database_path)
cursor = conn.cursor()

cursor.execute("""SELECT subreddit FROM parents GROUP BY subreddit HAVING SUM(length)>1000""")
ps = cursor.fetchall()

cursor.execute("""SELECT * FROM parents""")
ps2 = cursor.fetchall()

with open(LDA_corpus_path +'LDA_pseudodocuments.txt' ,'w') as f:
    for k in ps:
        count_words = 0
        doc = 0
        text = ""
        for parent_id, reply_id, parent_body, parent_subreddit, parent_utc_time, parent_score, parent_length in ps2:
            if parent_subreddit == (str(k)[2:-3]) :
                cursor.execute("""SELECT * FROM replies WHERE id='{}'""".format(reply_id))
                reply = cursor.fetchone()
                if reply:
                    reply_id, reply_body, reply_subreddit, reply_utc_time, reply_score, reply_length = reply
                    count_words = count_words + parent_length + reply_length
                    text = text + parent_body + reply_body
                if(count_words > 2000):
                    f.write(str(text) + '\n')
                    doc += 1
                    text = ""
                    count_words = 0
f.close()

f = open(LDA_corpus_path + 'LDA_pseudodocuments.txt', 'r')
lines = file.readlines()
random.shuffle(lines)
f.close()

f_10000 = open(LDA_corpus_path + 'LDA_pseudodocuments_10000.txt', 'w')
f_10000.write(lines[0:10000])

f_10000.close()
