
import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import DATABASE_URI2, DATABASE_NAME2, COLLECTION_NAME, USE_CAPTION_FILTER, MAX_B_TN
from utils import get_settings, save_group_settings



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = AsyncIOMotorClient(DATABASE_URI2)
db = client[DATABASE_NAME2]
instance = Instance.from_db(db)


async def get_db_size():
    stats = await db.command("dbstats")
    size_in_bytes = stats["dataSize"]
    return size_in_bytes
    

languages = [" Hin ", "Hindi", "हिन्दी", " Eng ", "English", " Tam ", "Tamil", "தமிழ்", " Tel ", "తెలుగు", "Telugu", " Mal ", "മലയാളം", "Malayalam", " Kan ", "ಕನ್ನಡ", "Kannada", " Guj ", "ગુજરાતી", "Gujrati", " Mar ", "मराठी", "Marathi", "Beng", "বাংলা", "Bangla", "Bengali", "Korean", "Japanese", "Chinese", "Punjabi", "Odia", "Assamese", "Bhojpuri", "Spanish", "French", "German", "Russian", "Portuguese", "Arabic", "Fan dub", "Hindi Clean"]



# List of video qualities
qualities = ["240p", "360p", "480p", "576p", "720p", "900p", "1080p", "1440p", 
             "2160p", "2880p", "3072p", "4320p", "5760p", "8640p"]

# Dictionary to map short names to full names
language_map = {
    " Hin ": "Hindi",
    "Hindi": "Hindi",
    "हिन्दी": "Hindi",
    " Eng ": "English",
    "English": "English",
    " Tam ": "Tamil",
    "Tamil": "Tamil",
    "தமிழ்": "Tamil",
    " Tel ": "Telugu",
    "తెలుగు": "Telugu",
    "Telugu": "Telugu",
    " Mal ": "Malayalam",
    "മലയാളം": "Malayalam",
    "Malayalam": "Malayalam",
    " Kan ": "Kannada",
    "ಕನ್ನಡ": "Kannada",
    "Kannada": "Kannada",
    " Guj ": "Gujrati",
    "ગુજરાતી": "Gujrati", 
    "Gujrati": "Gujrati",
    " Mar ": "Marathi",
    "मराठी": "Marathi",
    "Marathi": "Marathi",
    "Beng": "Bengali",
    "বাংলা": "Bengali",
    "Bangla": "Bengali",
    "Bengali": "Bengali",    
    "Korean": "Korean",
    " Jap ": "Japanese",
    # Add other short to full name mappings as needed
    # ...
}

@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        indexes = ('$file_name', )
        collection_name = COLLECTION_NAME


async def save_file(media):
    """Save file in database"""

    # Extracting necessary fields
    file_id, file_ref = unpack_new_file_id(media.file_id)
    
    # Initial cleaning of file_name
    file_name = str(media.file_name)
    
    # Remove blacklist words and patterns
    file_name = re.sub(r"(mkv|movies|movie|x264| piro |x265|Kbps|mwkOTT|AAC|SMM|x264-PAHE|mp4|MP4|MP3|Mp4|telegram|Bollywood|Hollywood|Tollywood|Download|subtitles|film|dubbed|latest|ClipmateMovies|mkvCinemas|PrimeFix|www_SkymoviesHD_email|www|Latest_Movies_Reborn|Netflix_Villa_Original|FilmOne_Movies|Miteshpatelnewmovies|MoviesClubXyz|Skymovies|File_Movies_Uploaded|Tg-@New_Movies_OnTG|Tg_@New_Movies_OnTG|Moonknight_media|Bob_files|Desire|CineVood|Bisal|Miteshpatelnew|Mallu_Movies|TheMoviesBoss|cineasteseries|Links|Mallu|@MR_Linkz|Linkz|@Sons_of_TamilRockers|@VideoMemesTamil|@TM_LMO|@Vip_LinkzZ|@Tamil_LinkzZ|@mwkOTT|@C_V|@Mallu_Movies|TamilRockers|Tamilblasters|@lubokvideo|@NithinMovies|Linkzz|Bolly4u|Jesseverse|TeamSeries|@Mj_Linkz|@SY_MS|@ulluweb_Series|@Einthusan|@RayFilms4U|@IMDbFilms4U|@HindiOldMovies|@HollywoodBay|@hdhindicinemas|@Hollywood_WebHub|MoviesVerse|A2MOVIES|@CE_LinkS|@mallukingz|@MEDIA_KING|@MoviePlayTk|@MOVIEHUNT|@E4E_ROCKERS|@MOVIEZMOB|@pluscinemas|@QualityCinemaZ|@universalpicturez|@uteam|TamilMV|@mfmixhindi|@mwkseries|@FBM|@vivimaxx|@IM|@Cinemagramz|Toonsouthindia|POPCORN_FILMS|@UCParadiso|@ensembly|@nkmhdpro1|worldfree4|@bb_movie|@Links2U|A2MOVIES|@QualiStuff|@Hindi_UltraHD_Movies|@Moviesmasaaly|@KannadaWarriors|@Mxoriginals|@udanpadam|@Star_rockers|@TM_LMO|@mfmixhindi|@Ml_Movies|@SimplyCinema|www_TamilBlasters_uk|@khatrimaza|@MCArchives|@Movieslkwww|@HindiHDCinemaa|Filmy4wap_xyz|@InfotainmentMedia2|FILMCOMPANY|@CinematicsUnited|@ALBCINEMASALL|@Kande76|@MKMovieking|@SoumenBot|@FrediesChannel|@MMXE|@Massmoviess|@universalpicturez|@popcorn_cinemas|@tamilrockers_in|@TROFFICIAL|@Bollywoodcinemas|@desimovies_TelegramHindi|@CC_Series|KatmovieHD|@geniehd|@HindiRockers|@CelluloidCineClub|@Mlwapcinemas|@kickass_torrents|@fullyfilmie|@paravamedia|@southindianm|@H265_Movies|@t_m_Golmaal|Downloadhub.us|mobile_mm|TheMoviesBoss|TbestMovies4|movieworldkdY|Akatsuki_Media|@Einthusan|Tvserieshome|@WMR_Terminator|@HindiHDMovies_Netflix|@desimovies|@RickyChannel|MOVIEZXSTREAMZ|@Nex_Film|@TamilAnimation|@CC_ALL|@TM_LHM|@cc|@BestMovie|@cinema_company|@cinema_kottaka|@CK_Hindi|@WMR|@cinemacollections|Tinymkv|@CM|@iMediaShare|@TM_LMO|@Cw_Links|@MMXE|@Onmoviess|@Cinema_Company|@MCArchives|@Cinema_kottaka|@CeritaSarikataMelayu|@Qualitymovies|@TR_Moviez|@Hezz_Movies|@Bollywoodcinemas|@FBM_HW|@CKMovies|@DVDWOALL|@Dubbedmovies|@Disney_Links|@Hollywood500|@MJ_Linkz|@cinema_petty|@CK_HEVC|@mmsubtitles|@CINEMA_BEACON|@IndianMoviez|@cinema_company|MOVIEBOXPROTAMIL|@Cw_LINKS|BollYFlix|@HindiNewMovies|@mfmixhindi|@HindiNEWmovies|@HindiHDmovies|@RickyChristanto|@CC|RickyChannel|MoviezzClub|@agm_300mb_zone|links2u|MM_New|fimpurmovie|FilmyGod|mwklinks|@mobile_mm|@MM_Linkz|@FBM|@CCineClub|@HEVC_Moviesz|@MM_New|NithinMovies|@WorldCinemaToday|@Moviezzclub|@JohnWick_Files|@TG_UPDATES1|@KR_MOVIES|@Kannada_Dub|Join|@EE_MOVIES|@Ak_Movies|@KR_Crazy|@nkmhdpro1|@KANNADA_ROOCKERSZ|@NK_CINIMA|@MJ_Moviez|@CH_MOVIES1|@mj_link_4u|@Cmkmedia|@Kichcha_Creations|@Zee5_Movies_HD|@newrockers1|@D_W_T_1|@Kichcha_Creations|@Zee5_Kannada_Films|@KannadaWarriors|@Kannada_HEVC|@jeevan|@breakfreemovies|@UMR_KAN_MOVIES|@Cinema_Rockets|@KC|@ARUNMOVIES1|@FBM_New|Movie4uKannada|@TROFFICIAL|@Ott_Moviezz|@Movies_Pro|@UCDump|@Anylink_Movies|@MovieStoreOfcl|www_TamilBlasters_cloud|@WMR_Kirik|@colorkannadi_LinkzZ|@luxmv_Linkz|@KGRockers|www_TamilBlasters_kim|www_1TamilMV_fans|@DCENIMAS|@Movies_Platform|@SouthTamilall1|@Theprofffesorr|@NANDAN_REIGNS|@SouthTamilall|@RunningMovies|@Moviez_Empires|@Bullmoviee|@MasterLinZz|@Stark_X_Expo|@Dk_Drama|@MoviesWorldBkp|www_HTPMovies_org|APDBackup|@MoviezAdda|nnadavalCinemas|IMDB_Backup1|\[|\]|\_|\(|\)|\:|\}|\{|\-|\.|\+)", " ", file_name, flags=re.IGNORECASE)
    file_name = re.sub(r'@[\w]+|[._\(\)\[\]]', ' ', file_name)  # Replace usernames, ., _, (, ), [, ]
    file_name = re.sub(r"'", '', file_name)  # Remove single quotes
    file_name = re.sub(r'\s+', ' ', file_name).strip()  # Remove all extra spaces
   
    

    # Initialize sets to store found languages and qualities
    found_languages = set()
    found_qualities = set()

    # Clean up file_name from unnecessary characters and spaces initially
    file_name = re.sub(r'[@._\(\)\[\]+\s]+', ' ', file_name)
    file_name += ' '

    # Process the caption if it exists
    if media.caption:
        caption_text = media.caption 
        # Replace usernames, and specific symbols {., _, (, ), [, ]}
        caption_text = re.sub(r'@[\w]+|[._\(\)\[\]]', ' ', caption_text, flags=re.IGNORECASE)
        # Replace invite links
        caption_text = re.sub(r't\.me/\w+', ' ', caption_text, flags=re.IGNORECASE)
        # Replace URLs
        caption_text = re.sub(r'(http[s]?://\S+|www\.\S+)', ' ', caption_text, flags=re.IGNORECASE)
        # Remove extra spaces
        caption_text = re.sub(r'\s+', ' ', caption_text).strip()
        # Add extra space at the end of caption to catch last short names which contains space end of the word.
        caption_text += ' '
    else:
        caption_text = None  # No caption available

    # Search and extract languages from caption text and file name
    for lang in languages:
        if (caption_text and re.search(re.escape(lang), caption_text, flags=re.IGNORECASE)) or \
           re.search(re.escape(lang), file_name, flags=re.IGNORECASE):
            full_name = language_map.get(lang, lang)
            found_languages.add(full_name)
            # Remove the short and full language names from file_name
            file_name = re.sub(re.escape(lang), ' ', file_name, flags=re.IGNORECASE).strip()
            file_name = re.sub(re.escape(full_name), ' ', file_name, flags=re.IGNORECASE).strip()

    # Search and extract qualities from caption text and file name
    for quality in qualities:
        if (caption_text and re.search(re.escape(quality), caption_text, flags=re.IGNORECASE)) or \
           re.search(re.escape(quality), file_name, flags=re.IGNORECASE):
            found_qualities.add(quality)
            # Remove found qualities from file_name
            file_name = re.sub(re.escape(quality), ' ', file_name, flags=re.IGNORECASE).strip()

    # Clean up any extra spaces in the file name
    file_name = re.sub(r'\s+', ' ', file_name).strip()

    # Append found languages to the file_name
    if found_languages:
        file_name += " ll "  # To separate  file_name and languages
        file_name += "🔊 :- " + ', '.join(found_languages)

    # Append found qualities to the file_name
    if found_qualities:       
        file_name += " ll "  # To separate languages and qualities
        file_name += "📽️ :- " + ', '.join(found_qualities)   

                          
    try:
        # Create a new Media object
        file = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name if media.file_name else caption_text,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
           #caption=media.caption.html if media.caption else None,
        )
    except ValidationError:
        logger.exception('Error occurred while saving file in database')
        print(f"🚫Error occurred while saving file in database :- {file_name}")
        return False, 2
    else:
        try:
            await file.commit()
        except DuplicateKeyError:
            logger.warning(f'{getattr(media, "file_name", "NO_FILE")} is already saved in database')
            print(f"Found Duplicate❌ File :- {file_name}")
            return False, 0
        else:
            logger.info(f'{getattr(media, "file_name", "NO_FILE")} is saved to database')
            print(f"File Saved✅ to Database :- {file_name}")
            return True, 1
            
            
            
async def get_search_results(chat_id, query, file_type=None, max_results=10, offset=0, filter=False):
    """For given query return (results, next_offset)"""
    if chat_id is not None:
        settings = await get_settings(int(chat_id))
        try:
            if settings['max_btn']:
                max_results = 10
            else:
                max_results = int(MAX_B_TN)
        except KeyError:
            await save_group_settings(int(chat_id), 'max_btn', False)
            settings = await get_settings(int(chat_id))
            if settings['max_btn']:
                max_results = 10
            else:
                max_results = int(MAX_B_TN)
    query = query.strip()
    #if filter:
        #better ?
        #query = query.replace(' ', r'(\s|\.|\+|\-|_)')
        #raw_pattern = r'(\s|_|\-|\.|\+)' + query + r'(\s|_|\-|\.|\+)'
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    total_results = await Media.count_documents(filter)
    next_offset = offset + max_results

    if next_offset > total_results:
        next_offset = ''

    cursor = Media.find(filter)
    # Sort by recent
    cursor.sort('$natural', -1)
    # Slice files according to offset and max results
    cursor.skip(offset).limit(max_results)
    # Get list of files
    files = await cursor.to_list(length=max_results)

    return files, next_offset, total_results

async def get_bad_files(query, file_type=None, filter=False):
    """For given query return (results, next_offset)"""
    query = query.strip()
    #if filter:
        #better ?
        #query = query.replace(' ', r'(\s|\.|\+|\-|_)')
        #raw_pattern = r'(\s|_|\-|\.|\+)' + query + r'(\s|_|\-|\.|\+)'
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    total_results = await Media.count_documents(filter)

    cursor = Media.find(filter)
    # Sort by recent
    cursor.sort('$natural', -1)
    # Get list of files
    files = await cursor.to_list(length=total_results)

    return files, total_results

async def get_file_details(query):
    filter = {'file_id': query}
    cursor = Media.find(filter)
    filedetails = await cursor.to_list(length=1)
    return filedetails


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")


def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref
