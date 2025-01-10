from datetime import datetime
import os

from .constants import TEMP_DIR
from .rocket_reach import RocketReach
from .utils.emails import (
    get_valid_email,
    remove_valid_email,
    write_invalid_email,
    write_used_email,
    write_valid_email,
)
from .utils.profiles import get_valid_profile, write_valid_profile


if not os.path.exists(TEMP_DIR):
    os.mkdir(TEMP_DIR)


def start_processing():
    current_datetime = datetime.now()
    post_fix = current_datetime.strftime('%m-%d-%Y-%H-%M-%S')
    rocket = RocketReach()
    counter = 0

    while True:
        email = get_valid_email()
        response = rocket.login(
            email=email,
            password=email,
        )
        if not response:
            if rocket.no_browser:
                write_valid_email(email=email)
                return
            else:
                write_invalid_email(email=email)
                continue
        write_valid_email(email=email)
        while True:
            profile = get_valid_profile()
            if not profile:
                print('No Profile Found')
                exit()
            rocket.get_profile_data(email=email, profile=profile, post_fix=post_fix)
            if not rocket.find_profile:
                counter = counter + 1
            else:
                counter = 0
            if counter > 20:
                print(
                    "System tried a lot, but didn't able to find any profile's emails"
                )
                exit()
            if rocket.limit_end:
                write_used_email(email=email, post_fix=post_fix)
                remove_valid_email(email=email)
                write_valid_profile(profile=profile)
                break
