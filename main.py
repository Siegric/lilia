from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import discord
import asyncio
from googletrans import Translator
import string
from quote import quote
from random_word import RandomWords

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
        with open("history.txt", "a", encoding='utf-8') as file:
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


def qotd(*key):
    try:
        output = quote(str(key), limit=1)
        for i in range(len(output)):
            final_output = (output[i]['quote'])
            author = (output[i]['author'])
            print(final_output)
            return [final_output, author]
    except:
        key = RandomWords().get_random_word(hasDictionaryDef=True)
        output = quote(key, limit=1,)
        for i in range(len(output)):
            final_output = (output[i]['quote'])
            author = (output[i]['author'])
            return [final_output, author]


#Generation method taken and modified from https://huggingface.co/microsoft/DialoGPT-medium#:~:text=DialoGPT%20is%20a%20SOTA%20large,single%2Dturn%20conversation%20Turing%20test.
def model_generate(message, src):
    new_user_input_ids = tokenizer.encode(message + tokenizer.eos_token, return_tensors='pt')
    bot_input_ids = torch.cat([new_user_input_ids], dim=-1)
    chat_ids = model.generate(
        bot_input_ids,
        max_length=100,
        do_sample=True,
        top_p=0.75,
        top_k=0,
        temperature=0.75,
        pad_token_id=tokenizer.eos_token_id
    )
    output = tokenizer.decode(chat_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
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
            i = i.replace("<@!950270628739579904> ", "")
            if i[:4] == "qotd":
                key = i[5:]
                output = qotd(key)
                await message.channel.send(output[0])
                await message.channel.send(f"-by {output[-1]}")
            elif i[:9] == "translate":
                try:
                    index = list(index_blank(i))
                    result = translator.translate(i[index[0]:index[-1]], dest=i[index[-1]:].replace(" ", ""))
                    await message.channel.send(result.text)
                except ValueError:
                    await message.channel.send("Usage: translate {phrase} {destination language code}")
            else:
                result_list = translate(i)
                i = result_list[0]
                if i == "save":  #Calls save_chat_history function to save chat history
                    archive = save_chat_history(message.author)  #takes the message author attribute from the message
                    if archive:
                        await message.channel.send("Chat history archived!")
                    else:
                        await message.channel.send("You lack permission!")
                else:
                    async with message.channel.typing():  #Sets activity to typing so user receives some kind of feedback
                        output = model_generate(i, result_list[-1])
                        await asyncio.sleep(0)  #Stops the typing activity
                        await message.channel.send(str(output))  #Returns output to user


client = Lilia()
client.run('OTUwMjcwNjI4NzM5NTc5OTA0.YiWefQ.NYPnNLE7YvoOJQSKuSDL_6lCj_w')#Token to run bot