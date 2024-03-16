import os

from do_space import upload_files_to_digital_ocean_spaces

bucket_name = 'vlandivir'
do_folder = 'srpski'
current_dir = os.path.dirname(os.path.abspath(__file__))
cards_path = os.path.join(current_dir, 'release-cards')

upload_files_to_digital_ocean_spaces(bucket_name, do_folder, cards_path)
