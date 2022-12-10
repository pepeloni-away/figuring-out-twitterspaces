#!/usr/bin/python
import os
import subprocess
#import requests
import urllib.request
import re
import sys


args = ' '.join(map(str, (sys.argv[1:])))

try:
    stream_name = re.search('[A-Za-z0-9\_\-]{86}', args).group()
except AttributeError:
    print('Provide the 86 characters long stream name or master/dynamic url that contains it')
    sys.exit(1)


download = True
if re.search('-g\s', args) or re.search('\s-g', args):
    download = False

#given_master = re.search('https:\/\/(canary-video-|prod-fastly-)(us-east-\d|ap-northeast-\d|ap-southeast-\d|us-west-\d|eu-west-\d|eu-central-\d)\.(video\.)?pscp\.tv\/Transcoding\/v1\/hls\/([A-Za-z0-9\_\-]{86}|{stream_name})\/non_transcode\/(us-east-\d|ap-northeast-\d|ap-southeast-\d|us-west-\d|eu-west-\d|eu-central-\d)\/periscope-replay-direct-prod-(us-east-\d|ap-northeast-\d|ap-southeast-\d|us-west-\d|eu-west-\d|eu-central-\d)-public\/audio-space\/master_playlist.m3u8', args)
given_master = re.search('https:\/\/(canary-video-|prod-fastly-)\w+-\w+-\d.(video.)?pscp.tv\/Transcoding\/v1\/hls\/[A-Za-z0-9\_\-]{86}\/non_transcode\/\w+-\w+-\d\/periscope-replay-direct-prod-\w+-\w+-\d-public\/audio-space\/(master_|dynamic_)playlist.m3u8', args)
if given_master is not None:
    given_master = given_master.group(0).replace('dynamic', 'master')
#print(given_master)

if given_master is None:
    
    print('trying to figure out fragment server, can fail') # sometimes stream names match work on other servers than the ones that host their fragments ...
                                                            # ex ZFZ94Boo57FAHG-Qye1kfbIygRy3T0ac1O5c5MlQxoqbAUhY05a4cyIPRuYBXg21wWYFE_cfSaGiUL2wc5Q7TA from
                                                            # eu central gets response from ap northeast but no fragments
    
       
    base_url = 'https://canary-video-us-east-1.pscp.tv'  # doesn't seem like this needs to match the server for audio fragments
    
    # https://gist.github.com/random-robbie-research/a02ec4c9d2826799d1ab9b09933bdcdc
    # https://random-robbie.github.io/bugbounty-scans/pscp.tv/report/report_page_0.html
    servers = [
    
        f"https://prod-fastly-ap-northeast-1.video.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/ap-northeast-1/periscope-replay-direct-prod-ap-northeast-1-public/audio-space/master_playlist.m3u8",
        
        f"https://prod-fastly-ap-southeast-1.video.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/ap-southeast-1/periscope-replay-direct-prod-ap-southeast-1-public/audio-space/master_playlist.m3u8",
        
        f"https://prod-fastly-ap-southeast-2.video.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/ap-southeast-2/periscope-replay-direct-prod-ap-southeast-2-public/audio-space/master_playlist.m3u8",
        
        f"https://prod-fastly-us-east-1.video.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/us-east-1/periscope-replay-direct-prod-us-east-1-public/audio-space/master_playlist.m3u8",
        
        f"https://prod-fastly-us-west-1.video.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/us-west-1/periscope-replay-direct-prod-us-west-1-public/audio-space/master_playlist.m3u8",
        
        f"https://prod-fastly-us-west-2.video.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/us-west-2/periscope-replay-direct-prod-us-west-2-public/audio-space/master_playlist.m3u8",
        
        f"https://prod-fastly-eu-west-3.video.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/eu-west-3/periscope-replay-direct-prod-eu-west-3-public/audio-space/master_playlist.m3u8",
        
        f"https://prod-fastly-eu-central-1.video.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/eu-central-1/periscope-replay-direct-prod-eu-central-1-public/audio-space/master_playlist.m3u8",
        
        f"https://prod-video-sa-east-1.pscp.tv/Transcoding/v1/hls/{stream_name}/non_transcode/sa-east-1/periscope-replay-direct-prod-sa-east-1-public/audio-space/master_playlist.m3u8" 
        
    ]  # all i can find for now, if twitter adds more add them here
    
    master_playlist = None
    for sv in servers:
        while master_playlist is None:
            #master_playlist = re.search('\/Transcoding.*\.m3u8', requests.get(sv).text).group()
            #print(sv)
            try:
                master_playlist = re.search('\/Transcoding.*\.m3u8', urllib.request.urlopen(sv).read().decode('utf-8')).group()
            except urllib.error.HTTPError as e:
                print(f"\n{e} on {sv}")
                break
            #current_server = sv   # not reliable
    if master_playlist is None:
        print("\nfailed to find master playlist")
        sys.exit(1)

if given_master is not None:
    #master_playlist = requests.get(given_master.group(0)).text
    master_playlist = urllib.request.urlopen(given_master).read().decode('utf-8')
    current_server = given_master

playlist_longtimestamp = re.search('playlist_\d{20}', master_playlist).group()


if given_master is not None:
    dl_playlist = current_server.replace('master_playlist', playlist_longtimestamp)
else:
    dl_playlist = base_url + (re.sub('\/ey.*\.ey.*\..*\/audio', '/audio', master_playlist)).replace('transcode','non_transcode')



if download is True:
    #t = requests.get(dl_playlist).text
    t = urllib.request.urlopen(dl_playlist).read().decode('utf-8')
    space_date = (re.search('\d{4}-\d{2}-\d{2}', t)).group()
    output = f'{space_date} [{stream_name}].aac'
    
    command = ['ffmpeg', '-i', f'{dl_playlist}', '-c', 'copy', '-threads', '18', f'{output}']
    
    subprocess.run(command)
    print('\nyou can use -g to show playable m3u8 and skip download')
else:
    print(f"\n   play from: \n{dl_playlist}")
    
