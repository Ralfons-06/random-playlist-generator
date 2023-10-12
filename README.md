# random-playlist-generator

Python script that creates random spotify playlists from your favorite Songs configured to run on UNIX-Systems using cronjob. 

## Installation 

Install Requirements `pip install -r requirements.txt`

## Usage

1. Obtain a Spotify Cookie as described here: [Spotcast](https://github.com/fondberg/spotcast). 
2. Insert the obtained _sp_key_ and _sp_dc_ to the config.py file.
3. Now you can run the Script with `python3 playlist_generator.py`


### Run Script automatically with Crontab

To run the script periodically, e.g. every 2 Days, you can use the crontab. To edit the crontab run `crontab -e` and 
add the following line to the file:

`0 0 2 * * /usr/bin/python3 /path/to/playlist_generator.py` 




