# pip3 install vk-api

import vk_api
import vk as api_vk
import random
import os
import requests
import datetime
import time

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import *

from icecream import ic

class vk_requests:
    def __init__(self, user_token: str):
        """
        :param bot_token: token your community,
        :param user_token: token your vk account,
        :param bot_group_id: if of your community

        If you need more info reed documentation: https://vk.com/dev/access_token
        """

        self.user_token = user_token

        self.user_VK = vk_api.VkApi(token=user_token)
        self.user_api = self.user_VK.get_api()

    def get_group_posts(self, group_id: int, count: int, postponed=False, only_time=False, last_post=False):
        """
        :param group_id: id of the group which posts you want to receive,
        :param count: how many post do you want to receive,
        :param postponed: True if you want to receive only postponed posts,
        :param only_time: True if you want ti receive only time

        Function return list of group posts
        """

        params = {"owner_id": f'-{group_id}', "count": f'{count}'}
        if postponed:
            params["filter"] = 'postponed'
        post = self.user_api.wall.get(**params)
        if post['count'] == 0:
            if only_time:
                return time.mktime(datetime.datetime.now().timetuple()) + 60
            return {'count': 0, 'items': []}
        if only_time:
            if last_post:
                return max([i['date'] for i in post['items']])
            else:
                return ([i['date'] for i in post['items']])
        elif last_post:
            # here I use bubble sort
            items = post['items']
            for i in range(len(items) - 1):
                for j in range(len(items) - i - 1):
                    if items[j]['date'] <= items[j+1]['date']:
                        items[j], items[j+1] = items[j+1], items[j]
            return {"count": post['count'], "items": [items[0]]}
        else:
            return post

    def new_post(self, group_id, date, text='', image=False):
        """
        :param group_id: id of the group where to post
        :param date: date of the post
        :param text: text of the post
        :param image: image witch attach to post
        :return: id of post or error
        """

        params = {"owner_id": f'-{group_id}', "message": text, "publish_date": date}

        if type(image) is str and os.path.exists(image):
            file = {'file1': open(f'{image}', 'rb')}

            user_session_api = api_vk.API(api_vk.Session(access_token=self.user_token))
            upload = user_session_api.photos.getWallUploadServer(group_id=group_id, v=5.131)
            upload = requests.post(upload['upload_url'], files=file).json()

            photo = (user_session_api.photos.saveWallPhoto(
                group_id=group_id,
                photo=upload['photo'],
                server=upload['server'],
                hash=upload['hash'],
                v=5.131))

            owner_id = photo[0]['owner_id']
            photo_id = photo[0]['id']
            access_key = photo[0]['access_key']
            attachments = f"""photo{owner_id}_{photo_id}&access_key={access_key}"""
            params["attachments"] = attachments

        elif type(image) is list and all([os.path.exists(img) for img in image]):
            attachments = []
            for img in image:
                file = {'file1': open(f'{img}', 'rb')}

                user_session_api = api_vk.API(api_vk.Session(access_token=self.user_token))
                upload = user_session_api.photos.getWallUploadServer(group_id=group_id, v=5.131)
                upload = requests.post(upload['upload_url'], files=file).json()

                photo = (user_session_api.photos.saveWallPhoto(
                    group_id=group_id,
                    photo=upload['photo'],
                    server=upload['server'],
                    hash=upload['hash'],
                    v=5.131))

                owner_id = photo[0]['owner_id']
                photo_id = photo[0]['id']
                access_key = photo[0]['access_key']
                attachments.append(f"""photo{owner_id}_{photo_id}&access_key={access_key}""")
            params["attachments"] = attachments
        return self.user_api.wall.post(**params)

    def post_timetable(self, time: list, table: list):
        """
        Function return next time in time table
        :param time: must be list with structure [0 <= Hour: int <= 24, 0 <= Minute: int <= 60]
        :param table: must be matrix(list of list) with structure [[0 <= Hour: int <= 24, 0 <= Minute: int <= 60], ....]
        :return: return list with structure [bool - True if next day, False if same day, [Hour: int, Minute: int]]
        """
        # timing = [7, 20]
        # table = [[7, 30], [7, 50], [11, 0]]

        if not all([True if 0 <= time[0] <= 24 and 0 <= time[1] <= 60 else False]):
            pass
        if all((True if 0 <= tab[0] <= 24 and 0 <= tab[1] <= 60 else False) for tab in table):
            pass
        # bubble sort time table
        for i in range(len(table) - 1):
            for j in range(len(table) - i - 1):
                if table[j][0] >= table[j + 1][0]:
                    table[j], table[j + 1] = table[j + 1], table[j]
                if table[j][0] == table[j + 1][0] and table[j][1] >= table[j + 1][1]:
                    table[j], table[j + 1] = table[j + 1], table[j]
        for i in range(len(table) - 1):
            # check the time, if it is less than minimum time in table
            if time[0] == table[0][0]:
                # check minute
                if time[1] < table[0][1]:
                    return [False, table[0]]
            # check hour
            if time[0] < table[0][0]:
                return [False, table[0]]
            # check the time, if it is bigger than maximum time
            if time[0] == table[-1][0]:
                # check minute
                if time[1] > table[-1][1]:
                    return [True, [table[0]]]
            # check hour
            if time[0] >= table[-1][0]:
                return [True, table[0]]
            # -
            # here go to the list and check next post time
            if table[i][0] == table[i + 1][0]:
                if table[i][1] <= time[1] < table[i + 1][1]:
                    return [False, table[i + 1]]
            if table[i][0] <= time[0] < table[i + 1][0]:
                return [False, table[i + 1]]



class bot_vk:
    def __init__(self, bot_token: str, bot_group_id: int):
        """
        :param bot_token: token your community,
        :param user_token: token your vk account,
        :param bot_group_id: if of your community

        If you need more info reed documentation: https://vk.com/dev/access_token
        """

        self.bot_token = bot_token
        self.bot_group_id = bot_group_id

        self.bot_vk = vk_api.VkApi(token=bot_token)
        self.bot_api = self.bot_vk.get_api()

        self.bot_longpool = VkBotLongPoll(self.bot_vk, bot_group_id)

    def send_message(self, user_id: int, message: str):
        """
        :param user_id: id of the user who receive the message,
        :param message: message text
        """

        return self.bot_api.messages.send(user_id=user_id, message=message, random_id=random.randrange(999999999999))

    def send_message_with_photo(self, user_id: int, message: str, image, images=False):
        """
        :param user_id: id of the user who receive message,
        :param message: message text, image - path of the image/images
        :param image: if one image string if images list,
        :param images: True if you need send 2 and more photo
        """

        if not images and type(image) == str:
            if os.path.exists(image):
                img = vk_api.VkUpload(self.bot_vk).photo_messages(str(image))
                attachment = f'photo{img[0]["owner_id"]}_{img[0]["id"]}_{img[0]["access_key"]}'
                return self.bot_api.messages.send(user_id=user_id, message=str(message),
                                                  random_id=random.randrange(999999999), attachment=attachment)

        if images and type(image) == list:
            if all([os.path.exists(i) for i in image]):
                attachment = []
                for img in image:
                    img = vk_api.VkUpload(self.bot_vk).photo_messages(str(img))
                    attachment.append(f'photo{img[0]["owner_id"]}_{img[0]["id"]}_{img[0]["access_key"]}')
                return self.bot_api.messages.send(user_id=user_id, message=str(message),
                                                  random_id=random.randrange(999999999),
                                                  attachment=attachment)


if __name__ == '__main__':
    time = vk_requests('')
    print(time.post_timetable([19, 0], [[2, 0], [12, 0], [17, 0]]))

