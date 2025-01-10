from scraper.constants import FINAL_PROFILE_FILE, INVALID_PROFILE_FILE, PROFILE_FILE


def get_valid_profile():
    try:
        with open(PROFILE_FILE, 'r') as file:
            profiles_data = file.read()
    except FileNotFoundError:
        profiles_data = ''
    profiles_data = profiles_data.split('\n')
    profile_data = profiles_data[0] if profiles_data else ''
    profiles_data = profiles_data[1:]
    profiles_data = '\n'.join(profiles_data)
    with open(PROFILE_FILE, 'w') as file:
        file.write(profiles_data)
    return profile_data


def __write_profile(profile: str, file_path: str, seperator: str = '\n'):
    try:
        with open(file_path, 'r') as file:
            profiles_data = file.read()
    except FileNotFoundError:
        profiles_data = ''
    profiles_data = profiles_data.split(seperator)
    profiles_data.append(profile)
    profiles_data = seperator.join(profiles_data)
    with open(file_path, 'w') as file:
        file.write(profiles_data)


def write_final_profile(profile: str, post_fix: str):
    __write_profile(
        profile=profile,
        file_path=FINAL_PROFILE_FILE + '-' + post_fix + '.txt',
        seperator='\n\n\n',
    )


def write_invalid_profile(profile: str):
    __write_profile(profile=profile, file_path=INVALID_PROFILE_FILE)


def write_valid_profile(profile: str):
    __write_profile(profile=profile, file_path=PROFILE_FILE)
