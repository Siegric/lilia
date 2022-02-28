from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import discord
import asyncio
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
chat_history = []

def save_chat_history():
    with open("history.txt", "w") as file:
        for i in chat_history:
            file.write(str(i) + '\n')

class Lilia(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        await client.change_presence(activity=discord.Game(name="Chinese Spyware"))

    async def on_message(self, message):
        print('Message from {0.author} in {0.channel}: {0.content}'.format(message))
        chat_history.append('Message from {0.author} in {0.channel}: {0.content}'.format(message))
        if client.user.mentioned_in(message):
              i = (str(message.content)).lower()
              i = str(i).replace("<@!672319158519857152> ", "")
              input_ids = tokenizer.encode(i + tokenizer.eos_token, return_tensors="pt")
              if i == "save":
                  save_chat_history()
                  await message.channel.send("Chat history archived!")
              else:
                  async with message.channel.typing():
                      try:
                          bot_input_ids = torch.cat([chat_history_ids, input_ids], dim=-1)
                          chat_history_ids = model.generate(
                              bot_input_ids,
                              max_length=1000,
                              do_sample=True,
                              top_p=0.95,
                              top_k=0,
                              temperature=0.6,
                              pad_token_id=tokenizer.eos_token_id
                          )
                          output = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
                          await asyncio.sleep(0)
                      except:
                          bot_input_ids = torch.cat([input_ids], dim=-1)
                          chat_history_ids = model.generate(
                              bot_input_ids,
                              max_length=1000,
                              do_sample=True,
                              top_p=0.95,
                              top_k=0,
                              temperature=0.6,
                              pad_token_id=tokenizer.eos_token_id
                          )
                          output = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
                          await asyncio.sleep(0)
                      await message.channel.send(str(output))


client = Lilia()
client.run(token)
