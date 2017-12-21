# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 10:03:14 2017

@author: Cassandra
"""
from twiggy import * # import * is also ok
def twiggy_setup():
    alice_output = outputs.FileOutput("alice.log", format=formats.line_format)
    bob_output = outputs.FileOutput("bob.log", format=formats.line_format)

    add_emitters(
        # (name, min_level, filter, output),
        ("alice", levels.DEBUG, None, alice_output),
        ("betty", levels.INFO, filters.names("betty"), bob_output),
        ("brian.*", levels.DEBUG, filters.glob_names("brian.*"), bob_output),
        )

# near the top of your __main__
twiggy_setup()