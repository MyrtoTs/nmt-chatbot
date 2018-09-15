import sqlite3  
import string

LDA_corpus_path = '/home/myrto/pink_dir/github/myrto-tsokanaridou-chatbot/new_data/'
database_path = '/home/myrto/pink_dir/github/decem_17_db.db'

# work with sql transactions to speed up processing
sql_t = []
# set up a connection
conn = sqlite3.connect(database_path)
# create a cursor object
cursor = conn.cursor()

cursor.execute("""SELECT * FROM parents""")
pr = cursor.fetchall()

parents_file = open(LDA_corpus_path + 'parents.train', 'w', buffering=10000)
replies_file = open(LDA_corpus_path + 'replies.train', 'w', buffering=10000)

# count = 0

for parent_id, reply_id, parent_body, parent_subreddit, parent_utc_time, parent_score, parent_length in pr:
#     count += 1
#     if count % 10000 == 0:
#         print('Working on pair {}'.format(count))
    cursor.execute("""SELECT * FROM replies WHERE id='{}'""".format(reply_id))
    reply = cursor.fetchone()
    if reply:
        reply_id, reply_body, reply_subreddit, reply_utc_time, reply_score, reply_length = reply
        parents_file.write(parent_body + '\n')
        replies_file.write(reply_body + '\n')

parents_file.close()
replies_file.close()


### Cleaning comments (foreigh chars, urls) ###

a = string.printable + '’‘“”'
eng_char = set(a)

parents = open(LDA_corpus_path + 'parents.train')
replies = open(LDA_corpus_path + 'replies.train')

clean_parents = open(LDA_corpus_path + 'clean_parents.train', 'w')
clean_replies = open(LDA_corpus_path + 'clean_replies.train', 'w')

count = 0
count_clear = 0

for p, r in zip(parents, replies):
    count += 1
    if count % 10000 == 0:
        print('Working on {}'.format(count))
    if ('http' not in p) and ('http' not in r):
        comment_p = set(p)
        comment_r = set(r)
        if comment_p.issubset(eng_char) and comment_r.issubset(eng_char):
            count_clear +=1
            
            while '....' in (p):
                p=p.replace('....','...')            
            while '....' in (r):
                r=r.replace('....','...')
                
            clean_parents.write(p)
            clean_replies.write(r)

print("Comment pairs before cleaning{}".format(count)) 
print("Clean Comment pairs{}".format(count_clear)) 

parents.close()
replies.close()

clean_parents.close()
clean_replies.close()

### Create dataset for nmt - chatbot ###

par = open(LDA_corpus_path + 'clean_parents.train', 'r')

parents = par.readlines()
N = len(parents)

rep = open(LDA_corpus_path + 'clean_replies.train', 'r')
replies = rep.readlines()

par.close()
rep.close()

print(N)

dev_size = 10000
tst_size = 10000
trn_size = (N-dev_size-tst_size)

print("Size of training set:" , trn_size,"\n""Size of development set:" , dev_size,"\n""Size of test set:",  tst_size,)

train_parents = open(LDA_corpus_path + 'train.from','w')
train_replies = open(LDA_corpus_path + 'train.to', 'w')
dev_parents = open(LDA_corpus_path + 'dev.from','w')
dev_replies = open(LDA_corpus_path + 'dev.to', 'w')
test_parents = open(LDA_corpus_path + 'tst.from','w')
test_replies = open(LDA_corpus_path + 'tst.to', 'w')

for x in range(0, trn_size):
    train_parents.write(parents[x])
    train_replies.write(replies[x])

print(x)
    
for x in range(trn_size,trn_size+dev_size):
    dev_parents.write(parents[x])
    dev_replies.write(replies[x])

print(x)    
    
for x in range(trn_size+dev_size  ,N):
    test_parents.write(parents[x])
    test_replies.write(replies[x])

print(x)

train_parents.close()
train_replies.close()
dev_parents.close()
dev_replies.close()
test_parents.close()
test_replies.close()
