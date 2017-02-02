# import pylens
from pylens import pylens

# we need to create examples for the agent to learn
# note that the examples_list is a 2d list
# this example has 2 examples for the agent to train on
pylens.write_ex_file('./lens_output/example_train_3.ex',
                     [[0.962093, 0.835833, 0.874307, 0.954139, 0.885376,
                       0.933471, 0.893499, 0.880757, 0.940357, 0.873547,
                       0.871031, 0.879365, 0.938522, 0.864605, 0.926971,
                       0.879439, 0.942822, 0.94532, 0.898834, 0.892513],
                      [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                       1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                     ],
                     'B',
                     'agent_3_train')

# train agent 3
# you will get an output file called wgt3.wt for the agent 3 weight file
pylens.call_lens('01-global_cascades_train.in', {'agent_id': '3'})

# now that agent 3 is trained
# you can give it a set of inputs

pylens.write_ex_file('./lens_output/input_3.ex',
                     [[1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
                       1, 0, 1, 0, 1, 0, 1, 0, 1, 0]],
                     'B',
                     'agent_3_input')

# with the examples you can now have lens return an output
# given the wgt3.wt file
# Note you call lens with a different in file
pylens.call_lens('02-global_cascades_update.in', {'agent_id': '3'})

# the new results are saved to an out file
# we now need to extract the new values from the outfile
# pass in the outfile
# num_lines refer to how many neural net nodes you have for the output
# the split_index refers to which column of values in the outfile is the new state values
# 0 for the first column
# 1 for the second column, etc
new_state = pylens.get_new_state_from_outfile('./lens_output/input_3.out',
                                              num_lines=20,
                                              split_index=0)

# making sure the length of the new state is correct
assert len(new_state == 20)

# now you have the new state values you can use to assign back to your agent
print(new_state)
