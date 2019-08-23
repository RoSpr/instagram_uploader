import argparse
import os

from instabot import Bot

PATH = os.path.dirname(os.path.abspath(__file__))


def post_instagram(picture_name):
    inst_login = os.getenv("LOGIN")
    inst_password = os.getenv("PASSWORD")

    bot = Bot()
    bot.login(username=inst_login, password=inst_password)

    picture_path = f"{PATH}\images\{picture_name}"

    bot.upload_photo(picture_path)
    bot.logout()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("picture_name", help="Post picture with given picture name from the 'images' folder "
                                             "in the same directory with this script",
                        type=str)
    args = parser.parse_args()
    picture_name = args.picture_name

    post_instagram(picture_name)
