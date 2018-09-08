import subprocess
from subprocess import call

def download_file(url, path):
    print(subprocess.check_output(['wget', '-P', path, url]).decode())


def extract_file(full_path):
    extension = full_path.split('.')[-1]

    if extension == 'bz2':
        print(subprocess.check_output(['bzip2', '-dk', full_path]).decode())
    elif extension == 'xz':
        print(subprocess.check_output(['unxz', full_path]).decode())


dataset_path = '/home/myrto/pink_dir/'
combined_file_path = dataset_path + 'combined_file'
database_path = dataset_path + 'reddit_sqlite_database.db'



urls_list = [
    'http://files.pushshift.io/reddit/comments/RC_2017-12.xz',
]

file_list = [dataset_path + url.split('/')[-1] for url in urls_list]

print('\n\n     DOWNLOAD AND EXTRACT FILES      \n\n')

for url, file in zip(urls_list, file_list):
    print('Downloading from url {}...'.format(url))
    download_file(url, dataset_path)

    print('Extracting file {}...'.format(file))
    extract_file(file)

print('\n\n     COMBINE FILES INTO ONE      \n\n')
command = ' '.join(['cat'] + [dataset_path + f.split('/')[-1].split('.')[0] for f in file_list] + ['>', combined_file_path])
call(command, shell=True)

