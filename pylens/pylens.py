# -*- coding: utf-8 -*-
from os import enviorn
from subprocess import call

from pandas import DataFrame

def tail(f, window):
    """
    Returns the last `window` lines of file `f` as a list.
    from: http://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
    """
    if window == 0:
        return []
    BUFSIZ = 1024
    f.seek(0, 2)
    bytes = f.tell()
    size = window + 1
    block = -1
    data = []
    while size > 0 and bytes > 0:
        if bytes - BUFSIZ > 0:
            # Seek back one whole BUFSIZ
            f.seek(block * BUFSIZ, 2)
            # read BUFFER
            data.insert(0, f.read(BUFSIZ))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            data.insert(0, f.read(bytes))
        linesFound = data[0].count('\n')
        size -= linesFound
        bytes -= BUFSIZ
        block -= 1
    return ''.join(data).splitlines()[-window:]

def get_new_state_from_outfile(self, outfile, num_lines, split_index, logger=None):
    """Reads in the new state from a LENS outfile
    Results are returned as a Python Pandas Series
    """
    if logger is not None: logger.debug('Getting new state from: {}'.format(outfile))

    with open(outfile, 'r') as f:
        output_lines = tail(f, window=num_lines)
        out_df = DataFrame({'outfile': output_lines})
        out_df['new_state'] = out_df.outfile.str.split(' ', expand=True)[split_index]
        if logger is not None: logger.debug('out_df:\n{}'.format(out_df))

    new_state = out_df['new_state']

    # pos = out_df.new_state[ :self.bank_length].reset_index(drop=True)
    # neg = out_df.new_state[self.bank_length: ].reset_index(drop=True)
    # self.logger.debug('pos:\n{}'.format(pos))
    # self.logger.debug('neg:\n{}'.format(neg))
    # new_state = DataFrame({'pos': pos, 'neg': neg})

    if logger is not None: logger.debug('new_state:\n{}'.format(new_state))
    return(new_state)

def call_lens(self, in_file, lens_env, logger=None):
    """Calls lens as a subprocess
    Parameters for the LENS in_file are passed as a python dictionary
    """
    if logger is not None:
        logger.info('Calling Lens (Python)')
        logger.debug('Using in file: {}'.format(in_file))
        logger.debug('Lens env: {}'.format(lens_env))

    env = environ  # from os

    if logger is not None: logger.debug('env: {}\n\n'.format(env))

    env.update(lens_env)

    if logger is not None:
        logger.debug('env with lens_env: {}\n\n'.format(env))
        logger.debug('Lens subprocess call')
        
    call(['lens', '-batch', in_file], env=env)  # from subprocess

    if logger is not None: logger.debug('Lens call finished (Python)')
