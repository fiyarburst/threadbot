import requests, time, sys, pprint, datetime

p = pprint.PrettyPrinter() #for debugging

###### LOGIN ######
import ConfigParser, os
config = ConfigParser.RawConfigParser(allow_no_value=False)
config.readfp(open("threadbot.cfg"))
sr = config.get("threadbot", "subreddit")
user = config.get("threadbot", "username")
pw = config.get("threadbot", "password")

user_pass_dict = {'user': user,
              'passwd': pw,
              'api_type': 'json'}

s = requests.Session()
s.headers.update({'User-Agent' : 'edmproduction weekly threadbot by /u/fiyarburst'})
r = s.post('http://www.reddit.com/api/login', data=user_pass_dict)
login = r.json()['json']['data']
cookie = {'cookie': login['cookie']}
mh = login['modhash']

##### Check day, select appropriate thread

d = datetime.date.today()
day = d.weekday()
# 0 / Monday / Feedback thread
# 1 / Tuesday / How do I make this sound thread
# 2 / Wednesday / There are no stupid questions thread
# 3 / Thursday / Marketplace thread

if day == 0:
    thread_call = {'api_type': 'json', 'kind': 'self', 'sr':sr, 'uh': mh, \
     'title': 'Feedback Thread (' + d.strftime("%B %d") + ')', \
     'text': 'Please post any and all [Feedback] or [Listen] type threads in this thread '+ \
        'until the next one is created. Any threads made that should be a comment here will ' + \
        'be removed. Please ask for specific advice.\n\n\nFurthermore, please link to the feedback ' +\
        'comments you\'ve left in your top-level comment. This will show others the feedback you\'ve ' + \
        'left, and you\'re more likely to get feedback yourself! Also, please notice those who are ' + \
        'leaving a lot of feedback and give them some, too. This is a cooperative ' + \
        'effort!\nSomething like:\n\n> [feedback for bob] \n\n> [feedback for bill] \n\n> [feedback' + \
        ' for joe] \n\n> Here\'s my track [link]. I\'m looking for ___'
     }
elif day == 1:
    thread_call = {'api_type': 'json', 'kind': 'self', 'sr':sr, 'uh': mh, \
     'title': '"How do I make this sound?" Thread (' + d.strftime("%B %d") + ')', \
     'text': "Post all \"How do I make this sound?\" questions" + \
      " in this thread until the next one is created. Any threads made that " + \
      " should be a comment here will" + \
      " be removed.\nPlease include a timestamped link to your request." }
elif day == 2:
    thread_call = {'api_type': 'json', 'kind': 'self', 'sr':sr, 'uh': mh, \
     'title': '"No Stupid Questions" Thread (' + d.strftime("%B %d") + ")", \
     'text': "While you should search, read the Newbie FAQ, and " + \
      "definitely [RTFM](http://en.wikipedia.org/wiki/RTFM) when you have a question, some days " + \
      "you just [can't get rid of a bomb](http://cdn.uproxx.com/wp-content/uploads/2011/08/tumblr_lpnoa80qJS1qj4b9to2_r1_500.gif)." + \
      " Ask your ~~stupid~~ questions here." }
elif day == 3:
    thread_call = {'api_type': 'json', 'kind': 'self', 'sr':sr, 'uh': mh, \
     'title': 'edmp Marketplace Thread (' + d.strftime("%B %d") + ")", \
     'text': "This thread is where you may share or request services" + \
              " you have to offer to the edmproduction community. Post your " + \
              " programs and plugins, your mastering/teaching/coaching/artwork " + \
              "services, your website/tutorials, your preset/sample packs, your" + \
              " labels- anything but actual music itself.\n\n**Rules:**\n\n1. No " + \
              "posting music. No posting your soundcloud when you're looking for " + \
              "labels, no ghost production; nothing that constitutes you selling or " + \
              "sharing your own created tracks.\n\n2. Spam will not be tolerated. Repeated " + \
              "postings for the same product/service in the same thread will not be allowed, " + \
              "but you can wait until the following week to repost.\n\n3. Mark very clearly " + \
              "whether you're requesting or offering services, and if you're offering them, " + \
              "whether those services are paid or free.\n\nAs with the rest of the subreddit, " + \
              "final decisions over what constitutes an acceptable posting here will be at the " + \
              "sole discretion of the mods." }
else:
    sys.exit()

#### Post thread

r = s.post('http://www.reddit.com/api/submit', data=thread_call, cookies = cookie)
thread_r = r.json()['json']

if len(thread_r['errors']) > 0:
    print "fuckin captcha or something"
    iden = thread_r['captcha']
#    captcha = s.get('http://www.reddit.com/captcha/' + iden)
    import subprocess
    subprocess.call(['open', 'http://www.reddit.com/captcha/' + iden ])
    thread_call['captcha'] = input("Captcha (enclose in quotes):")
    thread_call['iden'] = iden
    r = s.post('http://www.reddit.com/api/submit', data=thread_call, cookies = cookie)
    thread_r = r.json()['json']['data']
    print r.json()

thread_r = thread_r['data']
#p.pprint(thread_r)
name = thread_r['name']
tid = thread_r['id']
url = thread_r['url'] + '?sort=new'
print url

#print "Submitted thread. Now distinguishing:"

#### Mod-Distinguish thread

dist_data = {'api_type': 'json', 'how':'yes', 'id':name, 'uh': mh}
r = s.post('http://www.reddit.com/api/distinguish', data=dist_data, cookies = cookie)
thread_r = r.json()['json']
if len(thread_r['errors']) > 0:
    p.pprint(thread_r)

#print "Submitted thread. Editing to include thread sort link:"

body_text = "*[Please sort this thread by new!]("+url+")\n\n*" + thread_call['text']
#print "Sending edits."
edit_data = {'api_type': 'json', 'text': body_text,
        'thing_id':name, 'uh': mh}
r = s.post('http://www.reddit.com/api/editusertext', data=edit_data, cookies = cookie)
#thread_r = r.json()['json']
print "errors:"
p.pprint(r.json()['json']['errors'])
