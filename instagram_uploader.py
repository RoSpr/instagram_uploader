import requests
import os

from PIL import Image
from instabot import Bot
from os import listdir

PATH = os.path.realpath('main.py')
PATH = PATH.replace("main.py", "")


def load_picture(pic_url, pic_name):
    filepath = "images\{}".format(pic_name)

    filename = PATH + filepath

    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    response = requests.get(pic_url, verify=False)

    with open(filename, 'wb') as file:
        file.write(response.content)


def fetch_spacex():
    spacex_url = "https://api.spacexdata.com/v3/launches"

    response = requests.get(spacex_url)
    links = response.json()[81]['links']['flickr_images']

    for link_number, link in enumerate(links):
        pic_name = "spacex_{}.jpg".format(link_number)
        load_picture(link, pic_name)

        resize_img(pic_name, pic_name, 900)
        make_black_background(pic_name, pic_name)

        print("{} is downloaded".format(pic_name))


def get_extension(link):
    str = link.split('.')
    extension = str[-1]
    return extension


def fetch_hubble(collection_name):
    collection_url = "http://hubblesite.org/api/v3/images?page=all&collection_name={}".format(collection_name)
    collection_response = requests.get(collection_url)
    collection_response = collection_response.json()

    for pic_info in collection_response:
        pic_id = pic_info['id']

        hubble_url = "http://hubblesite.org/api/v3/image/{}".format(pic_id)

        response = requests.get(hubble_url)
        links_data = response.json()['image_files']

        links = []
        for link_data in links_data:
            link = link_data['file_url']
            links.append(link)

        pic_url = links[-1]
        pic_url = pic_url.replace("//", "https://")

        pic_extension = get_extension(links[-1])
        pic_name = "hubble_{}.{}".format(pic_id, pic_extension)

        load_picture(pic_url, pic_name)

        print("Picture with id {} is downloaded".format(pic_id))

        resize_img(pic_name, pic_name, 900)
        make_black_background(pic_name, pic_name)


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

    x = int((black_img.size[0] - img.size[0])/2)
    y = int((black_img.size[1] - img.size[1])/2)

    black_img.paste(img,(x,y))
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
    print("Enter Hubble picture collection (e.g.: wallpaper, holiday_cards, "
          "spacecraft, news, printshop, stsci_gallery)\n")
    pic_collection = input()
    fetch_hubble(pic_collection)

    fetch_spacex()
