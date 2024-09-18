# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/sandippshah/Rx-AutoFiler2.git /Rx-AutoFiler2 
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /Rx-AutoFiler2 
fi
cd /Rx-AutoFiler2 
pip3 install -U -r requirements.txt
echo "Starting Bot...."
gunicorn app:app & python3 bot.py
