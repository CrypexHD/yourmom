import discord
import mysql.connector
from discord.ext import commands
import re
import json


min_loot_value = 100000

def find_text_with_only_numbers_within_parentheses(text):

    cleaned_text = re.findall(r'\(([\d.,]+(?:K|M|B)?)\)', text)
    print(cleaned_text)
    my_list = list()
    for i in cleaned_text:
        if i[-1].lower() == 'k':
            my_list.append(float(i[:-1]) * 1000)
        elif i[-1].lower() == 'm':
            my_list.append(float(i[:-1]) * 1000000)
        elif i[-1].lower() == 'b':
            my_list.append(float(i[:-1]) * 1000000000)
        else:
            my_list.append(float(re.sub(',', '', i)))
    return my_list


# MySQL setup
config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': '123',
    'raise_on_warnings': True
}
connection = mysql.connector.connect(**config)
cursor = connection.cursor()

# Bot setup
TOKEN = '123'
CHANNEL_ID = 123  # Replace with your specific channel's ID
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')


@bot.event
async def on_message(message):
    # If the message is from the specific channel
    if message.channel.id == CHANNEL_ID:
        content = message.content
        username = ''
        title = ''
        field = ''
        mob = ''
        json_all_items = ''
        accepted = False


        # Check for embeds and append their content to the message content
        for embed in message.embeds:
            content += "\n\n--- EMBED ---\n\n"
            if embed.title:
                title += f"{embed.title}"
                print(title)
            if embed.description:
                username += f"{str(embed.description).split('has looted:')[0]}"
                print(username)
            if embed.description:
                mob += f"{str(embed.description).split('From: ')[1]}"
                print(mob)
            if embed.description:
                loot = str(embed.description).split('has looted:')[1].split('From')[0]
                list_loot = loot.split('\n')
                for i in list_loot:
                    if i == '' or i == ' ':
                        list_loot.remove(i)
                print(list_loot)
                # print(loot)
                loot_value = find_text_with_only_numbers_within_parentheses(loot)
                print(loot_value)
                list_append = []
                for i,x in enumerate(loot_value):
                    if float(x) >= min_loot_value:
                        accepted = True
                        list_append.append(i)

                list_all_items = dict()
                for i in list_append:
                    list_all_items[list_loot[i]] = loot_value[i]
                json_all_items = json.dumps(list_all_items)

                print(json_all_items)

            for fields in embed.fields:
                # print(fields)
                field = str(fields.value).split('\n')[1].split(' gp')[0]
                if field[-1].lower() == 'k':
                    field = float(re.sub("K", "", field)) * 1000
                elif field[-1].lower() == 'm':
                    field = float(re.sub("M", "", field)) * 1000000
                elif field[-1].lower() == 'b':
                    field = float(re.sub("B", "", field)) * 1000000000
                print(field)

        if float(field) >= min_loot_value and accepted:
            try:
                cursor.execute('''
                INSERT INTO messages (id, channel_id, author_id, content, title, username, mob, field, loot, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (message.id, message.channel.id, message.author.id, content, title, username, mob, field,
                      json_all_items, message.created_at))
                connection.commit()
                print("Successfully added to db")
            except mysql.connector.Error as err:
                print(f"Error: {err}")
                return

    # Continue to process other bot commands, if any
    await bot.process_commands(message)


bot.run(TOKEN)
