import requests
import os
import argparse
import urllib

from PIL import Image
from instabot import Bot
from os import listdir

PATH = os.path.realpath('main.py')
PATH = PATH.replace("main.py", "")


def load_picture(pic_url, pic_name):
    filepath = "images\{}".format(pic_name)

    filename = PATH + filepath

    directory = os.path.dirname(filename)
    os.makedirs(directory, exist_ok=True)

    response = requests.get(pic_url, verify=False)
    response.raise_for_status()

    with open(filename, 'wb') as file:
        file.write(response.content)


def fetch_spacex_links(launch_number):
    spacex_url = "https://api.spacexdata.com/v3/launches"

    response = requests.get(spacex_url)
    response.raise_for_status()

    links = response.json()[launch_number]['links']['flickr_images']

    return links


def get_extension(link):
    link_parts = link.split('.')
    extension = link_parts[-1]
    return extension


def fetch_hubble_collection(collection_name):

    url = "http://hubblesite.org/api/v3/images"
    params = urllib.parse.urlencode({'page': "all&collection_name={}".format(collection_name)})

    collection_response = requests.get(url, params=params)
    collection_response.raise_for_status()

    collection_response = collection_response.json()

    return collection_response


def resize_img(filename, new_filename, max_size):
    img = Image.open(PATH + "images\{}".format(filename))
    if img.size[1] > img.size[0]:
        height = max_size
        ratio = (height / float(img.size[1]))
        width = int((float(img.size[0]) * float(ratio)))
        img = img.resize((width, height), Image.ANTIALIAS)
        img.save(PATH + "images\{}".format(new_filename))
    else:
        width = max_size
        ratio = (width / float(img.size[0]))
        height = int((float(img.size[1]) * float(ratio)))
        img = img.resize((width, height), Image.ANTIALIAS)
        img.save(PATH + "images\{}".format(new_filename))


def make_black_background(filename, new_filename):
    img = Image.open(PATH + "images\{}".format(filename))
    black_img = Image.open(PATH + "black.jpg")

    x = int((black_img.size[0] - img.size[0]) / 2)
    y = int((black_img.size[1] - img.size[1]) / 2)

    black_img.paste(img, (x, y))
    black_img.save(PATH + "images\{}".format(new_filename))


def post_instagram():
    inst_login = os.getenv("LOGIN")
    inst_password = os.getenv("PASSWORD")

    bot = Bot()
    bot.login(username=inst_login, password=inst_password)

    for image in listdir("images"):
        bot.upload_photo(image)
        print("Photo is uploaded to Instagram")

    bot.logout


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("hubble_collection_name", help="downloads photos from Hubble collection given (e.g.: wallpaper, "
                                                       "holiday_cards, spacecraft, news, printshop, stsci_gallery)",
                        type=str)
    args = parser.parse_args()
    collection_name = args.hubble_collection_name

    try:
        collection_response = fetch_hubble_collection(collection_name)

        for pic_info in collection_response:
            pic_id = pic_info['id']

            hubble_url = "http://hubblesite.org/api/v3/image/{}".format(pic_id)

            response = requests.get(hubble_url)

            links_data = response.json()['image_files']

            links = [link_data['file_url'] for link_data in links_data]

            pic_url = links[-1]
            pic_url = pic_url.replace("//", "https://")

            pic_extension = get_extension(links[-1])
            pic_name = "hubble_{}.{}".format(pic_id, pic_extension)

            load_picture(pic_url, pic_name)

            print("Picture hubble_{}.{} is downloaded".format(pic_id, pic_extension))

            resize_img(pic_name, pic_name, 900)
            make_black_background(pic_name, pic_name)

        print("All Hubble pictures from {} collection are downloaded".format(collection_name))

    except requests.exceptions.HTTPError as error:
        print("Error: {}".format(error))

    try:
        launch_number = 81 #real launch number is 82 as elements in the list start with 0
        links = fetch_spacex_links(launch_number)

        for link_number, link in enumerate(links):
            pic_name = "spacex_{}.jpg".format(link_number)
            load_picture(link, pic_name)

            resize_img(pic_name, pic_name, 900)
            make_black_background(pic_name, pic_name)

            print("{} is downloaded".format(pic_name))

        print("All SpaceX images are downloaded")

    except requests.exceptions.HTTPError as error:
        print("Error: {}".format(error))

post_instagram()
