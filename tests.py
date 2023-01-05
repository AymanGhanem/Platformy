import os
import io
def create_profile_for_new_user(**kwargs):
    user = 'AymanG'
    with open('text.txt', 'w') as file:
        file.write("Some dummy text!")
    file_path = os.path.dirname(__file__) + '../keys/'+'user.email'+'.pem'
    print(file_path)

create_profile_for_new_user()