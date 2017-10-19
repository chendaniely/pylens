# -*- coding: utf-8 -*-
import os
import sys
import random
from subprocess import call, PIPE, STDOUT, DEVNULL

from pandas import DataFrame

def tail(f, window):
    """
    Returns the last `window` lines of file `f` as a list.
    from: http://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
    """
    # if window == 0:
    #     return []
    # BUFSIZ = 1024
    # f.seek(0, 2)
    # bytes = f.tell()
    # size = window + 1
    # block = -1
    # data = []
    # while size > 0 and bytes > 0:
    #     if bytes - BUFSIZ > 0:
    #         # Seek back one whole BUFSIZ
    #         f.seek(block * BUFSIZ, 2)
    #         # read BUFFER
    #         data.insert(0, f.read(BUFSIZ))
    #     else:
    #         # file too small, start from begining
    #         f.seek(0,0)
    #         # only read what was not read
    #         data.insert(0, f.read(bytes))
    #     linesFound = data[0].count('\n')
    #     size -= linesFound
    #     bytes -= BUFSIZ
    #     block -= 1
    # return ''.join(data).splitlines()[-window:]
    return f.readlines()[-window:]

def flip_1_0(number):
    """Flip 1 to 0, and vice versa
    :parm number: 1 or 0 to flip
    :type number: int
    :returns flipped value
    :rtype: int
    """
    assert number in [0, 1], 'number to flip is not a 0 or 1'
    assert isinstance(number, int), 'number to flip is not int'
    if number == 0:
        return 1
    elif number == 1:
        return 0
    else:
        raise ValueError('Number to flip not 0 or 1')

def mutate(list_to_mutate, mutation_prob):
    """Mutates each element of a list by the mutation_prob
    Mutating means flipping the 1 to a 0 or vice versa
    :param list_to_mutate: list of values to mutate
    :type list_to_mutate: list
    :param mutation_prob: probability of flipping each element in list
    :type mutation_prob: float
    if the mutation_prob == 0, then the original list is returned
    else, there is a probabliy that prototype is still returned
    """
    if mutation_prob > 0.0 and mutation_prob <= 1.0:
        post_mutation_list = list_to_mutate[:]
        for idx, value in enumerate(list_to_mutate):
            prob = random.random()
            if prob <= mutation_prob:
                post_mutation_list[idx] = flip_1_0(value)
        if ((post_mutation_list is list_to_mutate) or
                (post_mutation_list == list_to_mutate)):
            warnings.warn('Mutated example is equal to prototype',
                          UserWarning)
        return post_mutation_list
    elif mutation_prob == 0.0:
        return list_to_mutate
    else:
        raise ValueError('Incorrect value for mutation probability ' +
                         'probability needs to be between ' +
                         '0 and 1 inclusive')

def write_ex_file(filepath, examples_list, example_type,
                  example_name='example'):
    """Write an example file for lens
    """
    with open(filepath, 'w') as f:
        for idx, example in enumerate(examples_list):
            ex_string = 'name: {}-{}\n{}: {};\n'.format(
                example_name,
                idx,
                example_type,
                ' '.join(str(x) for x in example))
            f.write(ex_string)

def get_new_state_from_outfile(outfile, num_lines, split_index,
                               lens_type='feedforward', logger=None):
    """Reads in the new state from a LENS outfile
    Results are returned as a Python Pandas Series
    """
    if logger is not None: logger.debug('Getting new state from: {}'.format(outfile))
    if logger is not None: logger.debug('Lens type: {}'.format(lens_type))
    with open(outfile, 'r') as f:
        if lens_type == 'feedforward':
            output_lines = tail(f, window=num_lines)

        elif lens_type == 'recurrent':
            len_bank = num_lines / 2
            output_lines = tail(f, window=num_lines + 2)
            p1 = output_lines[1:len_bank+1]
            assert(len(p1) == len_bank)

            p2 = output_lines[len_bank + 2:]
            assert(len(p1) == len_bank)

            output_lines = p1 + p2
        else:
            raise ValueError

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

def call_lens(in_file, lens_env, verbose_lens=True, logger=None):
    """Calls lens as a subprocess
    Parameters for the LENS in_file are passed as a python dictionary
    """
    if logger is not None:
        logger.info('Calling Lens (Python)')
        logger.debug('Using in file: {}'.format(in_file))
        logger.debug('Lens env: {}'.format(lens_env))

    env = os.environ  # from os

    if logger is not None: logger.debug('env: {}\n\n'.format(env))

    env.update(lens_env)

    if logger is not None:
        logger.debug('env with lens_env: {}\n\n'.format(env))
        logger.debug('Lens subprocess call')

    if verbose_lens:
        call(['lens', '-batch', in_file], env=env)  # from subprocess
    else:
        call(['lens', '-batch', in_file], env=env, stdin=PIPE, stdout=DEVNULL, stderr=STDOUT)  # from subprocess

    if logger is not None: logger.debug('Lens call finished (Python)')
