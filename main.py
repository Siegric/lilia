from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import discord
import asyncio
from googletrans import Translator
import string

#Loading the models
#Optionally can swap out "microsoft/DialoGPT-medium" for "microsoft/DialoGPT-large" for better accuracy
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
translator = Translator()
chat_history = []
admins = ['special', 'Siegric#9286', 'lllllll#0997']


#Saves chat history as a text file in chronological order
def save_chat_history(user):
    if str(user) in admins:
        archive = True
        with open("history.txt", "w", encoding='utf-8') as file:
            for i in chat_history:
                file.write(str(i) + '\n')
        return archive
    else:
        archive = False
        return archive

#Translates arguments and returns translated argument as well as the source language
def translate(i):
    result = translator.translate(str(i))
    if result.src == 'en':
        return [i, result.src]

    else:
        i = result.text
        return [i, result.src]


def index_blank(i):
    for index, character in enumerate(i):
       if character in string.whitespace:
            yield index


def model_generate(bot_input_ids, src):
    chat_history_ids = model.generate(
        bot_input_ids,
        max_length=1000,
        do_sample=True,
        top_p=0.95,
        top_k=0,
        temperature=0.6,
        pad_token_id=tokenizer.eos_token_id
    )  #Generation method taken from https://huggingface.co/microsoft/DialoGPT-medium#:~:text=DialoGPT%20is%20a%20SOTA%20large,single%2Dturn%20conversation%20Turing%20test.
    output = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    if src == 'en':
        return output
    else:
        translated_output = translator.translate(output, dest=src)
        output = translated_output.text
        return output


class Lilia(discord.Client):
    async def on_ready(self):
        ready = ('Logged on as {0}!'.format(self.user))  #Returns a message in the console when bot is online
        print(ready)
        chat_history.append(ready)
        save_chat_history('special')
        await client.change_presence(activity=discord.Game(name="Chinese Spyware"))

    async def on_message(self, message):
        print('Message from {0.author} in {0.channel}: {0.content}'.format(message))  #Logs messages in the console
        chat_history.append('Message from {0.author} in {0.channel}: {0.content}'.format(message))  #Saves the chat history into a list
        if client.user.mentioned_in(message):
              i = (str(message.content)).lower()
              i = i.replace("<@!672319158519857152> ", "")
              print(i[:9])
              if i[:9] == "translate":
                  try:
                      index = list(index_blank(i))
                      result = translator.translate(i[index[0]:index[-1]], dest=i[index[-1]:].replace(" ", ""))
                      await message.channel.send(result.text)
                  except:
                      await message.channel.send("Usage: translate {phrase} {destination language code}")
              else:
                  result_list = translate(i)
                  i = result_list[0]
                  input_ids = tokenizer.encode(i + tokenizer.eos_token, return_tensors="pt")
                  if i == "save":  #Calls save_chat_history function to save chat history
                      archive = save_chat_history(message.author)  #takes the message author attribute from the message
                      if archive:
                        await message.channel.send("Chat history archived!")
                      else:
                          await message.channel.send("You lack permission!")
                  else:
                      async with message.channel.typing():  #Sets activity to typing so user receives some kind of feedback
                          try:
                              bot_input_ids = torch.cat([chat_history_ids, input_ids], dim=-1)  #If there are previous messages
                              output = model_generate(bot_input_ids, result_list[1])
                              await asyncio.sleep(0)  #Stops typing activity
                          except:
                              bot_input_ids = torch.cat([input_ids], dim=-1)  #If there isn't any previous message
                              output = model_generate(bot_input_ids, result_list[1])
                              await asyncio.sleep(0)  #Stops the typing activity
                          await message.channel.send(str(output))  #Returns output to user


client = Lilia()
client.run('NjcyMzE5MTU4NTE5ODU3MTUy.XjJwAg.QymGg8DZv05zEjgDJKp4-k72CSc')#Token to run bot
