# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/sandippshah/Rx-AutoFiler2.git /RX-AUTOFILER2 
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /RX-AUTOFILER2 
fi
cd /RX-AUTOFILER2 
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py
