from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from urllib.parse import quote
import re
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from info import CHANNELS, MV_UPDATE_CHANNEL, LOG_CHANNEL, FILE_STORE_CHANNEL, PUBLIC_FILE_STORE, SEND_MV_LOGS
from database.ia_filterdb import save_file, unpack_new_file_id
from utils import get_poster, temp

from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
import os
import json
import base64
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Function to generate link
async def generate_file_link(replied, bot):
    file_type = replied.media
    if file_type not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
        return
    file_id, ref = unpack_new_file_id((getattr(replied, file_type.value)).file_id)
    string = 'file_'
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    link = f"https://t.me/{temp.U_NAME}?start={outstr}"
    return link

# Handler for new messages in LOG_CHANNEL
@Client.on_message(filters.chat(LOG_CHANNEL) & (filters.video | filters.audio | filters.document))
async def new_file_handler(bot, message):
    link = await generate_file_link(message, bot)
    if link:
        await bot.send_message(
            chat_id=LOG_CHANNEL,
            text=f"Here is your Link:\n{link}"
        )



# List of languages to detect
languages = [
    "Hindi", "Hin", "Eng", "English", "Tamil", "Tam", "Tel", "Telugu", "Telgu", 
    "Mal", "Malyalam", "Malaya", "Kan", "Kannada", "Kannad", "Kanada",
    "Japanese", "Punjabi", "Gujrati", "Guj", "Marathi", 
    "Bangla", "Bengali", "Odia", "Assamese", "Bhojpuri", "Malayalam", 
    "Mandarin", "Spanish", "French", "German", "Korean", "Russian", "Italian",
   "Portuguese", "Arabic", "Clean", "Unofficial dub", "Unofficial", 
   "Studio dub", "Fan dub", "dual audio", "Clear",
] 

# Video resolutions
video_resolutions = [
    "240p", "360p", "480p", "576p", "720p", "900p", "1080p", 
    "1440p", "2160p", "2880p", "3072p", "4320p", "5760p", "8640p"
]

# Video qualities
video_qualities = [
    "BluRay", "HDRip", "TRUE WEB-DL", "UNTOUCHED", "DS4K", 
    "ESub", "×264", "×265", "WEBRip", "WEB-DL", "HDTV", "DVDRip", 
    "DVDScr", "AAC 5.1", "AAC 4.1", "AAC 3.1", "AAC 2.1", "AAC 1.1", 
    "AAC 5.0", "AAC 4.0", "Original", "8bit", 
    "AAC 3.0", "AAC 2.0", "AAC 1.0", "HDTV-Rip", 
    "CAM", "DHCAM", "HEVC", "DTS", "PreDVD", "BDRip", "BRRip", "BDR", 
    "BRR", "BDRM", "BRRM", "HDPopcorns", "3D", "BluRay REMUX", "BluRay 1:1", 
    "UHD", "UHD BluRay", "HMAX", "NF", "AMZN", "WEBR", "WEBDL", "iTunes", 
    "HDCenter", "CRF", "SDTV", "TVRip", "VODRip", "PPVRip", "WP", 
    "WPDL", "PPV", "DSRip", "DTVrip", "PPVR", "SDRip", "HQrip", 
    "P2P", "TC", "VHSRip", "VHS", "TVrip", "IPTVRip", "SatRip", "VCDRip", 
    "VCD", "VHSR", "Satrip", "LaserDisc Rip", "PPVR", "DD5.1", "Full HD", 
    "HD", "DDP5.1.x265", "ESubs", "AAC 5.1", "10bit", "UNCUT", 
    "Blu-ray", "DVD", "TS", "HDCAM", "R5", "MSubs", "XviD", "DivX", "h264", 
    "Remux", "HQ SPrint", "HDTS", "HQ S-Print", "PreDVDRip", "HEVC-PSA", "HQ Print", 
    "COMBINED", "ORG", "Dual Audio", "Multi Audio", "Dolby Digital", "4k", "HQ", 
]

# Function to extract details from the filename
def extract_details(text):
    # Replace underscores, dots, and dashes with spaces before any other cleanup
    clean_name = text.replace('_', ' ').replace('.', ' ').replace('-', ' ').replace('(', ' ').replace(')', ' ').replace(':', ' ')

    # Remove telegram usernames, brackets, and other unnecessary parts
    clean_name = re.sub(r'\[.*?\]|\(.*?\)|@[\w]+', '', clean_name)




    # Extract episode information if available
    episode_match = re.search(r'(S\d{2}\s?E\d{2}|EP\d{2}|E\d{2})', clean_name, re.IGNORECASE)
    episode_info = ""
    if episode_match:
        episode_info = episode_match.group()
        clean_name = clean_name[:episode_match.start()].strip()

    # Extract year if episode information is not available
    year_match = re.search(r'([(\.-_])?(20\d{2}|19\d{2})([)\.-_])?', clean_name)
    if year_match:
        clean_name = re.sub(r'(\(|\))', '', 
    clean_name[:year_match.end()].strip())


    resolution_match = re.search(rf'({"|".join(video_resolutions)})', clean_name, re.IGNORECASE)
    resolution = ""
    if resolution_match:
        resolution = resolution_match.group()
        clean_name = clean_name[:resolution_match.start()].strip()
        
        
    # Extract quality and resolution if available
    quality_match = re.search(rf'({"|".join(video_qualities)})', clean_name, re.IGNORECASE)
    quality = ""
    if quality_match:
        quality = quality_match.group()
        clean_name = clean_name[:quality_match.start()].strip()
    

    # Remove additional unnecessary parts like quality, resolution, and size details
    
    #added
    clean_name = re.sub(r'(Hindi|English|AMZN|Tamil|Malyalam|Kannada|Telugu|Mkv|WebRip|DD5.1|NF Series|MSubs|Full HD|HDRip|265|HD|DDP2|PrimeFix|HQ HDRip|WEBRip|mp4|BRRip|mkv|mp3|Kbps|Series|Movie|Movies|AAC2|HDRip|BluRay|AAC2|AAC|DD 5.1|DDP5.1.x265|AMZN|x264|x265|ESubs|AAC 5.1|10bit|UNCUT|HEVC|Blu-ray|DVD|PreDVD|CAM|TS|HDCAM|DVDRip|DVDScr|R5|HDTV|XviD|DivX|h264|Remux|WEB-DL|HQ SPrint|HQ S-Print|HQ Print|COMBINED| WEB |Dual Audio|Multi Audio|WEBDL|DTS|Dolby Digital|360p|480p|720p|1080p|2160p|4k)', '', clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(rf'({"|".join(video_qualities)}|{"|".join(video_resolutions)})', '', clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r'\s+', ' ', clean_name).strip()  # Remove extra spaces
    clean_name = re.sub(r'[\[\]{}\-+_]', '', clean_name)  # Remove specified symbols
    clean_name = re.sub(r'(\s*\.\s*)', ' ', clean_name).strip()  # Remove dots with spaces around them    

    # Include the episode information if available
    if episode_info:
        clean_name = f"{clean_name} {episode_info}".strip()

    return clean_name.strip(), quality.strip(), resolution.strip()

# Function to extract patterns from text
def extract_patterns(text, patterns):
    matches = set()
    for pattern in patterns:
        if re.search(rf'(\b|\.|_){pattern}(\b|\.|_)', text, re.IGNORECASE):
            matches.add(pattern)
    return ", ".join(matches)






# File path to store logged files
LOGGED_FILES_PATH = 'logged_files.json'

# Initialize a set to store logged filenames
logged_files = set()

# Load the logged files from the JSON file on startup
if os.path.exists(LOGGED_FILES_PATH):
    with open(LOGGED_FILES_PATH, 'r') as file:
        logged_files = set(json.load(file))

# List of admin user IDs
ADMINS = [622730585, 1003337276]  # Replace with actual admin user IDs

# Command to clear the logged files
@Client.on_message(filters.command("clear_logs") & filters.user(ADMINS))
async def clear_logs(bot, message: Message):
    global logged_files
    logged_files.clear()  # Clear the in-memory set

    # Remove the JSON file or clear its contents
    if os.path.exists(LOGGED_FILES_PATH):
        with open(LOGGED_FILES_PATH, 'w') as file:
            json.dump([], file)  # Write an empty list to the file

    await message.reply_text("Logged files have been cleared.")
                
    

@Client.on_message(filters.chat(CHANNELS) & filters.media)
async def media_handler(bot, message):
    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    media.file_type = file_type
    media.caption = message.caption
    await save_file(media)
    if SEND_MV_LOGS == True:
        filename, quality_from_name, resolution_from_name = extract_details(media.file_name)
    
        # Remove episode information for IMDb search
        clean_filename = re.sub(r'(S\d{2}\s?E\d{2}|EP\d{2}|E\d{2})', '', filename, re.IGNORECASE).strip()

        size = media.file_size
        size_str = f"{size / (1024 * 1024):.2f} MB" if size < (1024 * 1024 * 1024) else f"{size / (1024 * 1024 * 1024):.2f} GB"
    
        # Extract language from both filename and caption
        languages_from_filename = extract_patterns(media.file_name, languages)
        languages_from_caption = extract_patterns(media.caption, languages) if media.caption else ""
        all_languages = set(languages_from_filename.split(", ") + languages_from_caption.split(", "))
        all_languages.discard('')
        language_str = ", ".join(all_languages) if all_languages else "No Idea 🤪"
   
        # Extract qualities from both filename and caption
        quality_from_name = extract_patterns(media.file_name, video_qualities)
        quality_from_caption = extract_patterns(media.caption, video_qualities) if media.caption else ""
        all_qualities = set(quality_from_name.split(", ") + quality_from_caption.split(", "))
        all_qualities.discard('')
        quality_str = ", ".join(all_qualities) if all_qualities else "No Idea 🤪"
        
        #  Extract resolution from both filename and caption
        resolution_from_name = extract_patterns(media.file_name, video_resolutions)
        resolution_from_caption = extract_patterns(media.caption, video_resolutions) if media.caption else ""
        all_resolutions = set(resolution_from_name.split(", ") + resolution_from_caption.split(", "))
        all_resolutions.discard('')
        resolution_str = ", ".join(all_resolutions) if all_resolutions else "No Idea 🤪"
        
        # Remove episode information for duplication check
        base_filename = re.sub(r'(S\d{2}\s?E\d{2}|EP\d{2}|E\d{2})', '', filename, re.IGNORECASE).strip()
    
        # Check if the base filename is already logged 
        if base_filename not in logged_files:
            logged_files.add(base_filename)

            # Save the updated logged_files set to the JSON file
            with open(LOGGED_FILES_PATH, 'w') as file:
                json.dump(list(logged_files), file)
        
            #  Fetch file link from generate_file_link
            link = await generate_file_link(message, bot)
        
            #  URL-encode the filename to handle multiple words and spaces
            encoded_filename = quote(filename)                

            #  Create the buttons
            button1 = InlineKeyboardButton('Get This File♂️', url=f'{link}')
          #  button2 = InlineKeyboardButton('Get With All qualities♂️', url=f'https://t.me/{temp.U_NAME}?text={encoded_filename}')
            button2 = InlineKeyboardButton('Request Group', url=f'https://telegram.me/+HldvnSK5kV9hMmFl')
            #  Arrange the buttons in a single keyboard
            keyboard = InlineKeyboardMarkup([[button1], [button2]])    

            try:
                #  Fetch the IMDb data
                poster_data = await get_poster(clean_filename)
                rating = poster_data.get('rating', 'N/A') if poster_data else 'N/A'
                genres = poster_data.get('genres', 'N/A') if poster_data else 'N/A'

                #  Send the log message without a movie poster
                await bot.send_message(
                    MV_UPDATE_CHANNEL,
                    text=f"   𝗡𝗲𝘄𝗙𝗶𝗹𝗲_𝗔𝗱𝗱𝗲𝗱\n"
                         f"𝗙𝗶𝗹𝗲 𝗡𝗮𝗺𝗲: {filename}\n"
                         f"𝗜𝗠𝗗𝗕 𝗥𝗮𝘁𝗶𝗻𝗴: {rating}\n"
                         f"𝗚𝗲𝗻𝗿𝗲𝘀: {genres}\n"
                         f"𝗙𝗶𝗹𝗲 𝗦𝗶𝘇𝗲: {size_str}\n"
                         f"𝗤𝘂𝗮𝗹𝗶𝘁𝘆: {quality_str}\n"
                         f"𝗙𝗶𝗹𝗲 𝗥𝗲𝘀𝗼𝗹𝘂𝘁𝗶𝗼𝗻: {resolution_str}\n"
                         f"𝗟𝗮𝗻𝗴𝘂𝗮𝗴𝗲𝘀: {language_str}",
                    reply_markup=keyboard
                )
                print(f"Message sent to {MV_UPDATE_CHANNEL}: {filename}, {size_str}, {quality_str}, {resolution_str}, {language_str}")
            except Exception as e:
                print(f"Failed to send message to {MV_UPDATE_CHANNEL}: {e}")           
    else:
        return 
 
      