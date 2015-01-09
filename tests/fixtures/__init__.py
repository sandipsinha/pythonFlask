"""
" Copyright:    Loggly, Inc.
" Author:       Scott Griffin
" Email:        scott@loggly.com
"
"""
import os
import pkgutil

def populate( session, model_names=None ):
    """
    Populates the database with our test fixtures.  By convention this function looks for
    all *.py files in THIS package.  Each *.py file must have two variables defined:
      1. MODEL - the model object (SQLAlchemy table) to populate data for
      2. FIXTURES - an array of dictionaries containing the data
    """
    fixtures_path = os.path.dirname( os.path.realpath( __file__ ) )
    modules = [(name, loader) for loader, name, _ in pkgutil.iter_modules([ fixtures_path ])]

    # Default to setting up all the fixtures
    if model_names is None:
        model_names = [name for name, _ in modules]

    for name, loader in modules:
        if name in model_names:
            full_mod_name = '{}.{}'.format( __name__, name )
            mod = loader.find_module( name ).load_module( full_mod_name )

            for item in mod.FIXTURES:
                session.add( mod.MODEL( **item ) )
