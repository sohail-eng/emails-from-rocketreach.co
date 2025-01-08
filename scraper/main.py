from datetime import datetime

from .rocket_reach import RocketReach
from .utils.emails import get_valid_email, write_invalid_email, write_valid_email
from .utils.profiles import get_valid_profile, write_valid_profile


def start_processing():
    current_datetime = datetime.now()
    post_fix = current_datetime.strftime('%m-%d-%Y-%H-%M-%S')
    rocket = RocketReach()

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
                return
            rocket.get_profile_data(profile=profile, post_fix=post_fix)
            if rocket.limit_end:
                write_valid_profile(profile=profile)
                break
