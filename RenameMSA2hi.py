import os, sys, re 

def f_ren(spatt, rpatt):
    ''' Searches file names in current directory
    for pattern spatt and replaces it with pattern
    rpatt.
    '''
    for old_filename in os.listdir('.'):
        new_filename = re.sub(spatt, rpatt, old_filename)
        os.rename(old_filename, new_filename)

f_ren('MSA_HEB.*', 'heb1.csv')
f_ren('MSA_HEHI.*', 'hi1.csv')
f_ren('MSA_HEICB.*', 'icb1.csv')
f_ren('Datensatz.*', 'vf1.csv')

print(os.listdir(os.getcwd()))
