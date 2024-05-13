import requests
import vk_api, PIL
from PIL import Image, ImageFilter
import random

from vk_api.longpoll import VkLongPoll, VkEventType



TOKEN="f4733aeeaafd53b832..."

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()


#функция возвращает все размеры фотографий
def get_img_size(sizes, size_type):
    for size in sizes:
        if size['type'] == size_type:
            return size

def download(fileLink):
        fp="image.jpg"
        with open(fp, 'wb') as handle:
                response = requests.get(fileLink, stream=True)
                if not response.ok:
                    print(response)
                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)
        return fp

def filterBlur(img):
    img = Image.open(img)

    img = img.filter(ImageFilter.BLUR)
    img.save("BLURimage.jpg")
    return img

#жар-птица, обитель богов - есть ли.... разрушители ...


def parse_json_format(attachments):
    print("parse_json_format")
    urls = dict()
    for attach in attachments:
        photo_id = attach['photo']['id']
        size = None
        for size_type in ['w', 'y', 'z', 'x', 'm', 's']:
            size = get_img_size(attach['photo']['sizes'], size_type)
            if size is not None:
                break
        url = size['url']
        urls[photo_id] = url
    return urls


def send_photo_to_user(user_id=None, txt_message=None, photos=[]):
    print("send_photo_to_user")
    # создание экземпляра загрузчика
    upload = vk_api.VkUpload(vk_session)

    # создание списка фотографий, который передан функции
    uploaded_photos = upload.photo_messages(photos)

    # создаем список вложений, которые будут отправлять бот в формате VK
    attachments = []
    for photo in uploaded_photos:
        # преобразуем в формат для VK с указанием идентификатора группы и идентификатора фотографии
        attachments.append('photo{}_{}'.format(photo['owner_id'], photo['id']))

    # отправляем вложения пользователю

    vk.messages.send(user_id=user_id, attachment=','.join(attachments), message=txt_message)


def main():
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            photos_id=[]
            if event.attachments != {}:
                k=list(event.attachments.keys())
                for item_type,item_value in event.attachments.items():
                    if item_value=="photo":
                        photos_id.append(event.attachments[k[k.index(item_type)+1]])

                jsonoutput = vk.messages.getHistory(user_id=event.peer_id, count=1)['items'][0]['attachments']
                print(jsonoutput)

                urls_lst = parse_json_format(jsonoutput)
                print(urls_lst)
                
                
                for photo_id in photos_id:
                    print("photo_id",photo_id)
                    pid = int(photo_id.split(str(event.user_id) + "_")[1])
                    print("pid", urls_lst[pid])

                if pid in urls_lst:
                    print("links", urls_lst[pid])
                    
                    
                    
                    vk.messages.send(user_id=event.user_id, message="links " + urls_lst[pid])
                    fp=download(urls_lst[pid])
                    fp=filterBlur(fp)
                    print(fp)
                    send_photo_to_user(event.user_id, "", ["BLURimage.jpg"])
                   
                    

        # attachments=upload_photos("photo.jpg")
        # send_message_to_user(event.user_id, event.text,attachments)
        # qr = qrcode.make(txt_message)
        # qr.save("photo1.jpg")

        # send_photo_to_user(event.user_id, """
        # Вам отправлено сообщение.
        # С описанием.""", ["photo.jpg", "photo1.jpg"])

if __name__ == '__main__':
    main()
