# Import necessary libraries
import discord
import pygsheets
from datetime import datetime
import matplotlib.pyplot as plt
import requests
import numpy as np

# Define the intents
intents = discord.Intents.default()
intents.message_content = True

# Create a client instance for Discord
client = discord.Client(intents=intents)

# Define the name of the Google Sheet we're working with
sheet_name = ""

# Function to get the row of a user in the Google Sheet based on their ID
def get_user_row(id, sh):
    """
    This function takes in a user ID and a Google Sheet object, and returns the row index of the user in the sheet.
    If the user ID is not found in the sheet, it returns False.
    """
    # Get all values in the 4th column (where the user IDs are stored)
    sh_id_col = sh.get_col(4, include_tailing_empty=False)

    # Convert the user ID to lowercase and strip leading/trailing whitespace
    id = id.lower().strip()

    # Convert all IDs in sh_id_col to lowercase and strip leading/trailing whitespace
    sh_id_col = [id.lower().strip() for id in sh_id_col]

    try:
        # Try to find the row index of the user ID
        row_index = sh_id_col.index(id) + 1
    except ValueError:
        # If the user ID is not found, return False
        return False

    # If the user ID is found, return the row index
    return row_index

# Function to get the in-game name (IGN) of a user based on their ID
def get_user_ign(id, sh):
    """
    This function takes in a user ID and a Google Sheet object, and returns the in-game name (IGN) of the user.
    If the user ID is not found in the sheet, it returns False.
    """
    # Get the row of the user
    row = get_user_row(id, sh)
    if row:
        # If the row exists, get the IGN from the 2nd column of that row
        ign = sh.get_value((row, 2))
        # Return the IGN
        return ign
    # If the row doesn't exist, return False
    return False


def grab_last_scores(row=[], number=1, dates=[]):
    """
    This function takes in a list of scores (row), a number of scores to return (number), and a list of dates (dates).
    It returns the last 'number' of scores and their corresponding dates, excluding any empty or '0' scores.
    If there are 1 or less scores, it returns a list with a single False element for both scores and dates.
    """
    # Remove the first 8 elements from the row and dates lists and reverse them
    row = row[8:][::-1]
    dates = dates[8:][::-1]

    # Combine row and dates into a list of tuples and filter out empty or '0' scores
    combined = [(score.replace(',', ''), date) for score, date in zip(row, dates) if score ]

    # Separate scores and dates back into two lists
    fin_scores, fin_dates = zip(*combined)
    # If the final scores list has 1 or less elements
    if len(fin_scores) <= 1:
        # Return a list with a single False element for both scores and dates
        return ([False], [False])

    # Return the first 'number' elements from the final scores and dates lists
    return (list(fin_scores[:number]), list(fin_dates[:number]))

# Function to get the score of a user based on their ID
def get_score(id):
    # Authorize Google Sheets API
    gh = pygsheets.authorize(service_file='service_account_credentials.json')
    
    # Open the Google Sheet
    sh = gh.open(sheet_name)
    
    # Select the 'Culvert' worksheet
    sh = sh.worksheet_by_title('Culvert')
    
    # Get the user's in-game name (ign)
    ign = get_user_ign(id, sh)
    
    # If the user's in-game name exists
    if ign:
        # Get the user's row
        row = get_user_row(id, sh)
        
        # Get the user's full row
        full_row = sh.get_row(row, include_tailing_empty=False)
        
        # If the user's total average score is not 'N/A'
        if full_row[4] != 'N/A':
            # Get the user's total average score, max score, count, and total
            total_avg = full_row[4]
            score_max = full_row[5]
            count = full_row[6]
            #Get percentage change:
            first = full_row[-1].replace(',', '')
            second = full_row[-2].replace(',', '')
            change = str(int(first) - int(second))
            
            # Get the user's scores from the 9th column onwards
            full_row = full_row[8:]
            
            # Get the user's last score
            score = full_row[-1]
            
            # Remove empty and 0 scores and get the last 4 scores
            avg = [x for x in full_row if x != '' and x != '0' ][-4:]
            
            # Initialize the month average and counter
            month_average = 0
            counter = 0
            
            # Iterate over the average scores
            for i in range(len(avg)):
                # If the score is not empty
                if avg[i] != '':
                    # Add the score to the month average and increment the counter
                    month_average += int(avg[i].replace(',', ''))
                    counter += 1
            
            # Calculate the month average
            month_average = format(round(month_average / counter), ',d')
            # Return the user's last score, max score, month average, total average score, count, total, and in-game name
            return (score, score_max, month_average, total_avg, count, change, ign)
        else:
            # If the user's total average score is 'N/A', return False and a message
            return (False, 'No GPQ data available. Please wait until next week when scores are updated.')
    
    # If the user's in-game name does not exist, return False and a message
    return (False, 'IGN not found.')


def embed_profile(id):
    """
    Creates a Discord embed for a guild profile.

    Args:
        id (str): The ID of the guild member.

    Returns:
        tuple: A tuple containing a boolean indicating success, the Discord embed, and the guild member's name.
               If the guild member's score could not be retrieved, the first element of the tuple is False.
    """
    profile = get_score(id)
    if not profile[0]:
        return False, None, profile[1]

    now = datetime.utcnow()
    dt_string = now.strftime("%m/%d/%Y")
    current_embed = discord.Embed(title=f'{profile[6]} Guild Profile - {dt_string}', color= 0x9AECB2)
    current_embed.add_field(name='Personal Best', value=str(profile[1]), inline=True)
    current_embed.add_field(name='Monthly Average', value=str(profile[2]), inline=True)
    current_embed.add_field(name='Last Week\'s GPQ Score', value=str(profile[0]), inline=True)
    current_embed.add_field(name='\u200b', value='```fix\n| All-Time Statistics | Updates Sunday |```', inline=False)
    current_embed.add_field(name='Change', value=str(profile[5]), inline=True)
    current_embed.add_field(name='Total Average', value=str(profile[3]), inline=True)
    current_embed.add_field(name='Participation', value=str(profile[4]), inline=True)
    current_embed.set_footer(text='Visually see previous scores with the command !graph', icon_url='https://cdn.discordapp.com/attachments/840084220478357504/1182930240280997989/bageltransp.png?ex=65867ca3&is=657407a3&hm=234cfd23398dfe7fa5ddb89e54485e5591dc183dbe6442d3b693c98b0ccf9b1a&')
    return True, current_embed, profile[6]


def create_graph(id, scores_to_grab=10):
    gh = pygsheets.authorize(service_file='service_account_credentials.json')
    sh = gh.open(sheet_name).worksheet_by_title('Culvert')
    row = get_user_row(id, sh)

    if not row:
        return False, 'IGN not found.'

    row = sh.get_row(row)
    dates = sh.get_row(1)
    y_axis, x_axis = grab_last_scores(row, scores_to_grab, dates)

    if len(y_axis) <= 1:
        return False, 'Need more than 1 GPQ score.'

    x_axis = x_axis[::-1]
    y_axis = np.asarray(y_axis[::-1], dtype=np.float32)

    fig, ax = plt.subplots(figsize=[7, 5])
    l = ax.fill_between(x_axis, y_axis)

    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.margins(0)
    ax.set_facecolor('black')
    fig.set_facecolor('black')

    l.set_facecolors('#93DAFE')
    l.set_edgecolors('#93DAFE')
    l.set_linewidths([5])

    plt.title(get_user_ign(id, sh), fontsize=17, color='white', fontweight='bold')
    plt.xlabel('Previous Weeks', color='white')
    plt.ylabel('GPQ Score', color='white')
   

    ax.tick_params(axis='y', colors='white')
    ax.tick_params(axis='x', colors='white')
    ax.set_ylim([min(y_axis) * 0.95, max(y_axis) * 1.05])

    ax.xaxis.get_label().set_size(14)
    ax.yaxis.get_label().set_size(14)

    if scores_to_grab <= 10:
        plt.grid(False)
        ax.grid(color='white')
        plt.xticks(rotation=40, ha='right')
    else:
        ax.get_xaxis().set_visible(False)

    plt.tight_layout()
    plt.savefig('graph.png')
    plt.cla()
    plt.close()

    return True, True

def download_image(id):
    """
    Downloads an image from a URL obtained by calling the `get_link` function with the given ID.

    Args:
        id (str): The ID used to get the image URL.

    Returns:
        bool: True if the image was downloaded successfully, False otherwise.
    """
    image_url = get_link(id)
    if not image_url:
        return False

    img_data = requests.get(image_url).content
    with open('avatar.jpg', 'wb') as handler:
        handler.write(img_data)
    return True

def get_link(ign):
    """
    Sends a GET request to the Maplestory API to get the image URL of a character.

    Args:
        ign (str): The in-game name of the character.

    Returns:
        str: The image URL of the character if the request was successful and the character exists.
        bool: False if the request was not successful or the character does not exist.
    """
    try:
        r = requests.get(f'https://maplestory.nexon.net/api/ranking?id=job&rebootIndex=0&character_name={ign}&page_index=1', timeout=5)
        if r.status_code != 200:
            print(f'{r} {ign}')
            return False

        json_response = r.json()
        if not json_response:
            print(f"No data found for {ign}")
            return False

        return json_response[0]['CharacterImgUrl']

    except Exception as e:
        print(e, ign)
        return False

@client.event
async def on_message(message):
    if message.guild.name == "":
        author_id_str = str(message.author.id)
        if message.content.startswith('!profile'):
            success, *embed = embed_profile(author_id_str)
            if success:
                image_dl = download_image(embed[1])
                if image_dl:
                    file = discord.File('avatar.jpg')
                    embed[0].set_thumbnail(url='attachment://avatar.jpg')
                    await message.reply(file=file, embed=embed[0])
                else:
                    await message.reply(embed=embed[0])
                emoji = client.get_emoji()
                await message.add_reaction(emoji)
            else:
                await message.reply("IGN not found.")

        elif message.content.startswith('!graph'):
            command_parts = message.content.split()
            if len(command_parts) == 1:
                created = create_graph(author_id_str)
            elif len(command_parts) == 2:
                grab_score_length = command_parts[1].lower()
                if grab_score_length in ['max', 'all']:
                    created = create_graph(author_id_str, 999)
                elif grab_score_length.isdecimal() and int(grab_score_length) >= 1:
                    created = create_graph(author_id_str, int(grab_score_length))
                else:
                    await message.channel.send('Positive numbers only.')
            else:
                await message.channel.send('!graph max | !graph <number of dates>')

            if created[0]:
                chart = discord.File('graph.png', filename="graph.png")
                embed = discord.Embed(description='GPQ Scores', color=0x9AECB2)
                embed.set_image(url='attachment://graph.png')
                await message.reply(embed=embed, file=chart)
                for emoji_id in [986885221456678942, 971594490563416064]:
                    emoji = client.get_emoji(emoji_id)
                    await message.add_reaction(emoji)
            else:
                await message.reply(created[1])




@client.event
async def on_ready():
    print('Bot On.')


client.run('')
