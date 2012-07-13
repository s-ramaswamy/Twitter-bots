import imdb
import re
import twitter
import json
import pickle
import os
import random
import time
from rottentomatoes import RT
import tweetstream

FAIL_MESSAGES = u'''
$USERNAME Sorry mate I couldn't find the movie $MOVIENAME
Oops! I failed miserably trying to find $MOVIENAME for $USERNAME
$USERNAME Hey! Looks like $MOVIENAME doesn't exist in IMDB
Damn! Sorry $USERNAME I can't find $MOVIENAME
Hey $USERNAME ! Are you sure $MOVIENAME is a movie ? Can't find it
'''.split('\n')
def check_if_done(id):
    '''
    Checks if a tweet has already been responded to
    '''
    if os.path.exists('/home/meetaw/done.pkl'):
        f = open('/home/meetaw/done.pkl', 'r')
        done = pickle.load(f)
        f.close()
        if id in done:
            return True
    return False
def update_done(id):
    '''
    Updates a list of tweets that've been replied to
    '''
    if os.path.exists('/home/meetaw/done.pkl'):
        f = open('/home/meetaw/done.pkl', 'r')
        done = pickle.load(f)
        f.close()
    else:
        done = []
    done.append(id)
    f = open('/home/meetaw/done.pkl', 'w')
    pickle.dump(done, f)
    f.close()
    
        
def main():    
    api = twitter.Api(consumer_key='jHYTabwRpnc7vv84Q9JQ',consumer_secret='FMvYUo7CYRjTZmE0b4Js2T9ICSjGDcroHMDIkxOpUc', access_token_key='634600300-rplkYB6iGkGFCHushkSOsRjoem3Nui6hpfm6EVw', access_token_secret='eLPAV4skpyACMLiFdJZzQHBkehE7r9I1rA85DAo2Ez4') 
    ia = imdb.IMDb()
    counter = 0
    
    while True:
        if api.GetRateLimitStatus()['remaining_hits']<100:
            rand_time = random.randint(60*60, 120*60)
            print 'sleeping for %s minutes' % (rand_time/60)
            time.sleep(rand_time)
        #    counter = 0
            
        #rand_time = random.randint(0, 1000)
        #time.sleep(rand_time)
        #print counter
        #if (rand_time%87==0):
            ##p= api.GetPublicTimeline()
            ##counter=counter+1
            #for x in p:
                #name= x.user.screen_name
                #friends= x.user.friends_count
                #followers= x.user.followers_count
                #seed=random.randint(1,10)
                #friends= x.user.friends_count
                #followers= x.user.followers_count
                #if float(friends/(followers+1))>2.5 and friends>200 and seed%2==0:
                    ##api.CreateFriendship(name)
                    ##counter=counter+1
                    #print 'Now following ' + name
        rand_time = random.randint(0, 10)            
        if (rand_time%2==0):
            mentions = api.GetMentions()
         #   counter = counter+1
            for mention in mentions:
                if not check_if_done(mention.id):
                    seed = random.randint(1,10)
                    if seed%2==0:
                        api.CreateFriendship(mention.user.screen_name)
                        print "Now following " + mention.user.screen_name
                        counter=counter +1
                    text = re.sub(re.escape('@theimdbbot '), '', mention.text)
                    s_result = ia.search_movie(text)
                    rt_result=RT('qn8g46yvmjmnhyd65xm4qc9p').feeling_lucky(text)
                    print text
                    if not s_result or not rt_result:
                        tries = 0;
                        while tries < 10:
                            message = FAIL_MESSAGES[random.randint(0, len(FAIL_MESSAGES) - 1)]
                            message = message.replace('$USERNAME', '@%s' % mention.user.screen_name)
                            message = message.replace('$MOVIENAME', '%s' % text)
                            if message and len(message) < 141: 
                                post = api.PostUpdate(message,in_reply_to_status_id=mention.id)
                                print message
          #                      counter = counter +1
                                tries = 50
                            else:
                                tries = tries +1
                        #if counter > 250:
                            #rand_time = random.randint(120*60, 240*60)
                            #print 'sleeping for %s minutes' % (rand_time/60)
                            #time.sleep(rand_time)
                            #counter = 0
                        update_done(mention.id)    
                    else:    
                        the_unt = s_result[0]
                        ia.update(the_unt)
                        update_done(mention.id)
                        message = '@'+mention.user.screen_name+' '
                        genres = ', '.join(the_unt['genres'])
                        rating = str(the_unt['rating']).encode('utf8', 'replace')
                        director = str(the_unt['director'][0]).decode('utf8', 'replace')
                        freshness = str(rt_result['ratings']['audience_score']).encode('utf8', 'replace')+'%'
                        runtime = str(rt_result['runtime']).encode('utf8', 'replace')+'mins'
                        year = str(the_unt['year']).encode('utf8', 'replace')
                        cast0 = str(the_unt['cast'][0]).decode('utf8')
                        cast1 = str(the_unt['cast'][1]).decode('utf8')
                        objects = [rating,freshness,runtime,director,genres,year,cast0,cast1]
                        print objects
                        for item in objects:
                            if len(message) <140:
                                finmessage=message
                                message=message + item +'; '
                            else:
                                pass
                        if len(message) < 140:
                            finmessage = message    
                        print finmessage
                        try:
                            post = api.PostUpdate(finmessage,in_reply_to_status_id=mention.id)
                            counter = counter +1
                        except:
                            pass
                        update_done(mention.id)
                        
if __name__ == '__main__':
    main()            


