from scraper.constants import (
    EMAIL_FILE,
    INVALID_EMAIL_FILE,
    USED_EMAIL_FILE,
)


def get_valid_email():
    try:
        with open(EMAIL_FILE, 'r') as file:
            emails_data = file.read()
    except FileNotFoundError:
        emails_data = ''
    emails_data = emails_data.split('\n')
    email_data = emails_data[0] if emails_data else ''
    emails_data = emails_data[1:]
    temp_data = emails_data
    emails_data = []
    for item in temp_data:
        if item.strip():
            emails_data.append(item)
    emails_data = '\n'.join(emails_data)
    with open(EMAIL_FILE, 'w') as file:
        file.write(emails_data)
    return email_data


def remove_valid_email(email: str):
    try:
        with open(EMAIL_FILE, 'r') as file:
            emails_data = file.read()
    except FileNotFoundError:
        emails_data = ''
    emails_data = emails_data.split('\n')
    emails_data.remove(email)
    temp_data = emails_data
    emails_data = []
    for item in temp_data:
        if item.strip():
            emails_data.append(item)
    emails_data = '\n'.join(emails_data)
    with open(EMAIL_FILE, 'w') as file:
        file.write(emails_data)


def __write_email(email: str, file_path: str):
    try:
        with open(file_path, 'r') as file:
            emails_data = file.read()
    except FileNotFoundError:
        emails_data = ''
    emails_data = emails_data.split('\n')
    emails_data.append(email)
    temp_data = emails_data
    emails_data = []
    for item in temp_data:
        if item.strip():
            emails_data.append(item)
    emails_data = '\n'.join(emails_data)
    with open(file_path, 'w') as file:
        file.write(emails_data)


def write_used_email(email: str, post_fix: str):
    __write_email(email=email, file_path=USED_EMAIL_FILE + '-' + post_fix + '.txt')


def write_invalid_email(email: str):
    __write_email(email=email, file_path=INVALID_EMAIL_FILE)


def write_valid_email(email: str):
    __write_email(email=email, file_path=EMAIL_FILE)
