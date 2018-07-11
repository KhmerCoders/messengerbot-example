import os
import sys
import json
import random
from datetime import datetime

import requests
from flask import Flask, request,render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()
    print data
    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    #send_text(sender_id,"hello world")
                    handle_message(sender_id, message_text)

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    sender_id = messaging_event["sender"]["id"] 
                    payload=messaging_event["postback"]["payload"]
                    handle_postback(sender_id,payload)

    return "ok", 200

def send_text(send_id, text):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    msg={
        "text":text
    }
    
    data = json.dumps({
        "recipient": {
            "id": send_id
        },
        "message": msg
    })

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)

def handle_message(sender_id, message_text):
    if 'name' in message_text:
        send_text(sender_id, 'My name is test')
    elif 'age' in message_text:
        send_text(sender_id, 'I am ageless.')
    else:
        #send_text(sender_id, "I don't understand")
        send_menu(sender_id)

def send_menu(sender_id):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    welcomeMessage={"attachment":{
        "type":"template",
        "payload":{
            "template_type":"button",
            "text":"What do you want to do next?",
            "buttons":[
              {
                "type":"postback",
                "title":"Short Jokes",
                "payload": "textjoke"
              },
              {
                "type": "postback",
                "title": "Funny Picture",
                "payload": "picture_joke"
              }
              
            ]
        }
    }}
    
    data = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "message": welcomeMessage
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)

def handle_postback(sender_id, payload):
    if payload == 'textjoke':
        send_text(sender_id,"I am a joke")
    elif payload== 'picture_joke':
        send_image(sender_id,"https://i0.wp.com/www.webdevelopersmeme.com/wp-content/uploads/2017/02/yu81pk.jpg")
    else:
        send_text(sender_id,"not understand")

def send_image(sender_id, url):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    msg={
        "attachment": {
            "type": "image",
            "payload": {
                "url": url
            }
        }
    }
    
    data = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "message": msg
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)



