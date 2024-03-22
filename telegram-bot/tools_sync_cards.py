import os

from do_space import sync_missing_cards

current_dir = os.path.dirname(os.path.abspath(__file__))

sync_missing_cards('vlandivir', 'srpski-sources/', 'srpski/')
