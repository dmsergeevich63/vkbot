import urequests as rq
import utime as t
class VKAPI(object):
    def __init__(self):
        self.token = "f4733aeeaa....."
    def _sendRequest(self, method, prm):
        prm["access_token"] = self.token
        prm["v"] = "5.101"
        par = self._q(prm)
        qu = "https://api.vk.com/method/"+method+"/?"+par
        res = rq.get(qu).json()
        gc.collect()
        return res

    def get(self, method, params = {}):
        res = self._sendRequest(method, params)
        while "error" in res and res["error"]["error_code"] == 6:
            machine.lightsleep(0.5)
            res = self._sendRequest(method, params)
        return res
    def _q(self,d):
      query = ""
      for key in d.keys():
        query += str(key) + "=" + str(d[key]) + "&"
      return query
 
api = VKAPI()
mc = 0

def checkmsg():
  msgs = api.get("messages.getConversations",{"filter":"unread","count":"1"})["response"];
  msg = False
  for i in msgs["items"]:
    msg = i["last_message"]
  return msg  

#def bot(t):
#  msg = checkmsg()
#  if not msg:
#    return
#  answer(msg["from_id"],msg["text"])
#  gc.collect()

def bot(t):
  #import machine 
  #pin = machine.Pin(4)
  #pin.value(0)
  msg = checkmsg()
  print("123")
  send("74270955","sec")
  if not msg:
    return
  answer(msg["from_id"],msg["text"])
  gc.collect()

def send(uid,txt):
  global mc
  api.get("messages.send",{"user_id": uid, "message":txt,"random_id":mc})
  mc+=1
  
def mark(id):
  api.get("messages.markAsRead",{"peer_id":id}) 

def answer(usr,txt):
#основная часть, отвечающая за поведение бота
  if txt == "/device":
    return send(usr,"ESP8266")
  if txt == "/uptime":
    return send(usr,str(t.time())+"sec")
  return  mark(usr)

from machine import Timer
bt = Timer(-1)
bt.init(period=5000, mode=Timer.PERIODIC, callback=bot)

#74270955 мой id
#5000 - время между проверками сообщений. Бот обрабатывает 1 сообщение за запрос. Бот испольует апи, вместо LongPoll, т.к. у ESP8266 наблюдаются проблемы с подключением к LP-серверу
#Для запуска бота в фоновом режиме, добавьте в main.py exec(open("vk.py").read(),globals()) , для остановки бота используйте bt.deinit()
#Текст отправляемых сообщений должен быть предварительно кодирован через urlencode, либо должен содержать только англ. буквы и цифры. В моей сборке прошивки отсутствовал urllib.
#Бот протестирован на Lolin (Wemos) D1 с версией micropython 1.11 с токеном сообщества. 