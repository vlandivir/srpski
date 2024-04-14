import os

from do_space import upload_files_to_digital_ocean_spaces

current_dir = os.path.dirname(os.path.abspath(__file__))

bucket_name = 'vlandivir'
do_folder = 'srpski'
cards_path = os.path.join(current_dir, '..', 'release-cards')

# upload_files_to_digital_ocean_spaces(bucket_name, do_folder, cards_path)

do_folder = 'srpski-sources'

cards_path = os.path.join(current_dir, '..', 'chat-gpt', 'language-cards', 'source-images')
upload_files_to_digital_ocean_spaces(bucket_name, do_folder, cards_path)

cards_path = os.path.join(current_dir, '..', 'chat-gpt', 'language-cards', 'release-images')
upload_files_to_digital_ocean_spaces(bucket_name, do_folder, cards_path)

