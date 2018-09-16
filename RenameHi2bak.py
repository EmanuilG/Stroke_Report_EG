import os, sys, re 
import datetime as dt 
import locale

locale.setlocale(locale.LC_ALL, 'german_Germany')

now = dt.datetime.now()

t = now.strftime('%Y%m%dT%H%M%S')


def f_ren(spatt, rpatt):
    ''' Searches file names in current directory
    for pattern spatt and replaces it with pattern
    rpatt.
    '''
    for old_filename in os.listdir('.'):
        new_filename = re.sub(spatt, rpatt, old_filename)
        os.rename(old_filename, new_filename)

f_ren('hi.?\.csv', '''./csv_backup/hi{}.csv'''.format(t))
f_ren('icb.?\.csv', '''./csv_backup/icb{}.csv'''.format(t))
f_ren('heb.?\.csv', '''./csv_backup/heb{}.csv'''.format(t))
f_ren('vf.?\.csv', '''./csv_backup/vf{}.csv'''.format(t))

# print(os.listdir(os.getcwd()))
