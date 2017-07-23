'''
This is a reddit bot coded by
/u/Mjone77
'''
import praw
import random
import sys
import configparser
#import discord
#import asyncio

#This sets up the variables and junk from the ini file, also creates an ini file if it is missing
try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    welcomeMessageLines = config['Welcome']['message'].split('$')
    refreshMessage = config['Welcome']['refresh']
    admins = config['Admin']['users'].lower().split(',')
    alreadyReplied = config['Technical']['alreadyReplied'].split(',')
    alreadyReplied.pop() #removes empty item on the end
    alreadyRepliedPm = config['Technical']['alreadyRepliedPm'].split(',')
    alreadyRepliedPm.pop() #removes empty item on the end
    alreadyWelcomed = config['Technical']['alreadyWelcomed'].split(',')
    alreadyWelcomed.pop()
    seenPosts = config['Technical']['seenPosts'].split(',')
    seenPosts.pop()
    username = config['Cred']['username']
    password = config['Cred']['password']
    botID = config['Cred']['id']
    botSecret = config['Cred']['Secret']
#    token = config['Accnt']['discordToken'] #the token for discord
except Exception as e:
    print(str(e))
    config = configparser.ConfigParser()
    config['Welcome'] = {'message': 'Welcome!',
                         'refresh': 'Refresh'}
    config['Admin'] = {'users': ''}
    config['Technical'] = {'alreadyReplied': '',
                           'alreadyWelcomed': '',
                           'seenPosts': '',
                           'alreadyRepliedPm': ''}
    config['Cred'] = {'username':'',
                      'password':'',
                      'id':'',
                      'secret':''}
#    config['Accnt'] = {'discordToken': ''}
    with open('config-new.ini','w') as configfile:
        config.write(configfile)
    print("Please complete generated config-new.ini")
    sys.exit()

#log's on to reddit here and set the subreddit
r = praw.Reddit(client_id=botID,
                     client_secret=botSecret,
                     user_agent='A bot for roleplaying',
                     username=username,
                     password=password)
#outdated oauth
'''
o = OAuth2Util.OAuth2Util(r)
o.refresh(force=True)
'''
subreddit = r.get_subreddit('secretsubreddit')
#Set up variables
message = "" #add replies to this. Make sure to add a \n___\n (3 underscores) after every message. Hopefully this will allow multiple commands to be called with one comment
needSave = False
welcomeMessage = ''
tempRefresh = ''
needConfirmRefresh = False
for line in welcomeMessageLines:
    welcomeMessage+=line+'\n\n'
messageEnd = "[meta][See all my commands](http://secretsubreddit.wikia.com/wiki/FacilityAI)|[suggest new features](https://www.reddit.com/message/compose/?to=Mjone77&subject=FacilityAI_Suggestion)|[report bugs/errors](https://www.reddit.com/message/compose/?to=Mjone77&subject=FacilityAI_Report)"
refreshMsgLines = refreshMessage.split('\n')

'''
#creates a client object for discord
client = discord.Client()
'''

#Add comment or post id's to array and config.ini
#idType: 0 is a comment.id, 1 is a username, 2 is for post, 3 is for pm's
def addID(idToAdd, idType):
    if idType == 0:
        alreadyReplied.append(idToAdd)
        while (len(alreadyReplied)>100): #only keep 100 most recent replied comments
            alreadyReplied.pop(0)
        config['Technical']['alreadyReplied']= ''
        for comment in alreadyReplied:
            config['Technical']['alreadyReplied']+=(comment+',')

    elif idType == 3:
        alreadyReplied.append(idToAdd)
        while (len(alreadyReplied)>100): #only keep 100 most recent replied comments
            alreadyRepliedPm.pop(0)
        config['Technical']['alreadyRepliedPm']= ''
        for comment in alreadyReplied:
            config['Technical']['alreadyRepliedPm']+=(comment+',')

    elif idType == 1:
        alreadyWelcomed.append(idToAdd)
        config['Technical']['alreadyWelcomed']+=(idToAdd+',')
    elif idType == 2:
        seenPosts.append(idToAdd)
        while (len(seenPosts) > 5) : #only keep 5 most recent seen posts
            seenPosts.pop(0)
        config['Technical']['seenPosts']= ''
        for post in seenPosts:
            config['Technical']['seenPosts']+=(post+',')
    global needSave
    needSave = True

#Checks the comments/posts/pm's for commands, and handles them
def checkForCommands():
    global message
    recentComments = r.get_comments('secretsubreddit')
    #Checks for commands in comments
    for comment in recentComments:
        analyzeText(comment,0)
    #checks for commands in pm's
    for comment in r.get_unread(unset_has_mail=True, update_user=True):
        analyzeText(comment,1)
    #check if new poster is known
    for submission in subreddit.get_new(limit=3):
        if str(submission.author) not in alreadyWelcomed:
            addID(str(submission.author), 1)
            message = ''
            #welcome(submission)
        #discord stuff
        '''
        if str(submission.id) not in eenPosts:
            await announcePost(submission)
            addID(submission.id, 2)
        '''

#searches for possible commands in a comment/pm, then passes them on to be searched and replied to
def analyzeText(comment,commentOrPm):
    global message
    if '!' in comment.body and str(comment.id) not in alreadyReplied and str(comment.author) != 'FacilityAI':
        addID(str(comment.id), commentOrPm)
        links = []
        try:
            links.append(comment.permalink)
            links.append(comment.link_url)
        except:
            pass
        searchForCommands(comment.body, comment.author, links)
        if message:
            commentReply(comment)
            message = ''

#searches a string for commands
def searchForCommands(body, author, links):
    global message
    global admins
    message = ''
    commentLines = body.lower().splitlines()
    commentWords = []
    for line in commentLines:
        for word in line.split(' '):
            commentWords.append(word)
    if '!roll' in commentWords:
        try:
            numbers = commentWords[commentWords.index('!roll')+1].split('d')
            rollDice(int(numbers[0]),int(numbers[1]))
        except:
            message+='[META]To roll dice, please use !roll followed by #d#, for example saying \"!roll 3d5\" would roll 3 dice with 5 sides each.\n___\n'
    if '!cake' in commentWords:
        cake()
    if '!refresh' in commentWords:
        refreshMemory()
    #encryption doesn't work and nobody uses it anyway so it's disabled
    '''
    if '!encrypt' in commentWords:
        try:
            msg = body[body.lower().find('!encrypt'):len(body)].split('"')[1]
            offset = int(body[body.lower().find('!encrypt')+9:len(body)].split(' ')[0])
            message+=a1z26(offset,msg)+'\n___\n'
        except:
            message+='In order to encrypt a message, please comment like this:\n!encrypt offset "message to encrypt"\nOffset is a number, normally 0. The message must be surrounded by ", this allows you continue your comment past the command if you\'d like\n___\n'
    if '!decrypt' in commentWords:
        try:
            msg = body[body.lower().find('!decrypt'):len(body)].split('"')[1]
            offset = int(body[body.lower().find('!decrypt')+9:len(body)].split(' ')[0])
            message+=a1z26Rev(offset,msg)+'\n___\n'
        except:
            message+='In order to decrypt a message, please comment like this:\n!decrypt offset "message to decrypt"\nOffset is a number, normally 0. The message must be surrounded by ", this allows you continue your comment past the command if you\'d like\n___\n'
    '''
    if '!nowelcome' in commentWords and str(author) not in alreadyWelcomed:
        print(str(author))
        addID(str(author),1)
        message+='You have been registered as a veteran faculty member and will not be welcomed to work. Ever.\n___\n'
    if '!summon' in commentWords:
        try:
            customSplit = body[body.lower().find('!summon'):len(body)].split('"')
            custom = ''
            if len(customSplit)>1:
                custom = customSplit[1]
            users = body[body.lower().find('!summon'):len(body)].split("'")[1].split(' ')
            summon(str(author), users, custom, links)
        except Exception as e:
            print(e)
            message+='Something went wrong, please remember the formating (no u/ needed):\n\n!summon \'name name name name\' "optional additional message"\n\nError Message (for dev): \n\n'+str(e)+'\n___\n'
    if '!editdesc' in commentWords:
        user = '/u/'+str(author)+':'
        mssg = body[body.lower().find('!editdesc'):len(body)].split("'")[1]
        if checkMsg(mssg):
            if findLine(user.lower()) is None:
                addLine(user, mssg)
                message+='You have been added to the refresh message.\n\n'
            else:
                changeLine(user, mssg)
                message+='Your description has been changed.\n\n'
            message+=findLine(user.lower())+'\n\nIf your message was cut short, ensure that it does not contain \'.'
        else:
            message+='Your description violates the requirements, make sure it is under 600 characters and has no line breaks.\n\n'
        message+='\n___\n'
    if '!refreshuser' in commentWords:
        user = '/u/'+body[body.lower().find('!refreshuser'):len(body)].split(" ")[1].lower()+':'
        if findLine(user) is None:
            message+='This user is not in the refresh message.'
        else:
            message+=findLine(user)+'\n\n'
        message+='\n___\n'
    if '!removedesc' in commentWords:
        user = '/u/'+str(author)+':'
        if findLine(user.lower()) is None:
            message+='You are not in the refresh message.\n___\n'
        else:
            changeLine(user, '')
            message+='You have been removed from the refresh message.\n___\n'
    if '!give' in commentWords:
        item = commentWords[commentWords.index('!give')+1]
        message+="Here is the "+item+" that you requested.\n___\n"
    '''
    Admin commands
    '''
    if str(author).lower() in admins:
        global needConfirmRefresh
        global tempRefresh
        global needSave
        if needConfirmRefresh:
            if '!cancelrefresh' in commentWords:
                needConfirmRefresh = False
                tempRefresh = ''
                message+='Changes to !refresh have been canceled.\n\n___'
            elif '!confirmrefresh' in commentWords:
                try:
                    global refreshMessage
                    global refreshMsgLines
                    config['Welcome']['refresh'] = tempRefresh
                    refreshMsgLines = tempRefresh.split('\n')
                    refreshMessage = ''
                    for line in refreshMsgLines:
                        refreshMessage+=line+'\n\n'
                    needSave = True
                    needConfirmRefresh = False
                    message+='Refresh updated.\n___\n'
                    refreshMemory()
                except:
                    message+='Something went wrong when attempting to update the Refresh message, please try again. Refer to the wiki for a guide on how to update the message or pm /u/Mjone77 if you have any questions.\n___\n'
        if '!updaterefresh' in commentWords:
            try:
                tempRefresh = body[body.lower().find('!updaterefresh')+15:len(body)] #removed the split at ", now it just uses the complete message
                msg = tempRefresh
                sampleRefresh = tempRefresh+'\n\n'#''
                #for line in msg:
                #    sampleRefresh+=line+'\n\n'
                needConfirmRefresh = True
                message+='The refresh message will be set to this once you reply with !confirmRefresh (!cancelRefresh to abort changes):\n___\n\n'+sampleRefresh+'\n___\n'
            except:
                message+='Something went wrong when attempting to update the Refresh message, please try again. Refer to the wiki for a guide on how to update the message or pm /u/Mjone77 if you have any questions.\n___\n'    
        if '!refreshsource' in commentWords:
            message+=config['Welcome']['refresh']+'\n___\n'
        if '!addadmin' in commentWords:
            try:
                if str(commentWords[commentWords.index('!addadmin')+1]) not in admins:
                    admins.append(str(commentWords[commentWords.index('!addadmin')+1]))
                    tempAdmins = ''
                    for name in admins:
                        if(name):
                            tempAdmins+=name+','
                    config['Admin']['users'] = tempAdmins
                    needSave = True
                message+='The admins are now:\n\n'+str(admins)+'\n___\n'
            except Exception as e:
                print(e)
                message+='Something went wrong, please make sure your command looks like this:\n\n!addAdmin name\n___\n'
        if '!removeuser' in commentWords:
            user = '/u/'+body[body.lower().find('!removeuser'):len(body)].split(" ")[1].lower()+':'
            if findLine(user) is None:
                message+='This user is not in the refresh message.\n___\n'
            else:
                changeLine(user, '')
                message+= body[body.lower().find('!removeuser'):len(body)].split(" ")[1] + ' has been removed from the refresh message.\n___\n'
#Reply to comments
def commentReply(comment): #Don't forget takes in comment
    print('replying\n'+comment.body+'\n______________________________\n')
    global message
    comment.reply(message+messageEnd)
    #is there a way to do the ^^ effect without having to do it before every word?

#rolls dice and saves each roll in an array, total of the rolls is at the end of the array. This is done so that a table of the rolls can be made if needed.
#command can be '!roll 5d6' or something like that
#ready for initial usage in the bot - can be upgraded later
def rollDice(amnt, sides):
    if amnt <= 1000000 and sides <= 1000000:
        total = 0
        rolls = []
        for i in range(0,amnt):
            del i
            roll = random.randrange(sides)+1 
            total+=roll
            rolls.append(roll)
        #rolls.append(total)
        global message
        if amnt == 1:
            message+="You roll a "+str(sides)+" sided die.\n\nYour result is: **"+str(total)+"**\n___\n"
        else:
            message+="You roll "+str(amnt)+" dice with "+str(sides)+" sides each.\n\n"
            message+="\nYour total is: **"+str(total)+'**\n\n'
            if amnt > 100:
                amnt = 100
                message+="I can only show a maximum of 100 results at once.\n\n"
            message+="Your results are: \n\n|Die|#|\n-|-\n"
            for i in range(0,amnt):
                message+=str(i+1)+'|'+str(rolls[i])+"|\n"
            message+="\n___\n"
    else:
        message+="A number you entered was too large, please only use numbers that are equal to or less than 1000000\n___\n"
#makes a cake, probably won't use this actual method in the final code as it's so short
#command can be '!cake' or something like that, or you mentioned something about it being taken under verbage
#ready for initial usage in the bot - can be upgraded later
def cake():
    global message
    #message+="Here is your cake sir:\n\n      ,,,,,  \n     _|||||_  \n    {~\*~\*~\*~}  \n  __{\*~\*~\*~\*}__  \n `-------------`\n___\n"
    message+="Here is your cake sir:\n\n*tube descends from the ceiling and spits out a [cake](http://i.imgur.com/KeSyZN9.jpg)*\n___\n"

#this is the welcome message. Will be replied to posts of users that have never posted before
#ready for initial usage in the bot - can be upgraded later
def welcome(submission):
    global message
    message+=welcomeMessage+"\n"
    refreshMemory()
    submission.add_comment(message+messageEnd)

#this is the second part of the welcome message that people can ask for on demand
#ready for initial usage in the bot - can be upgraded later
def refreshMemory():
    global message
    if len(message) > 10000:
        message+='The refresh message is over 10k characters long and can not fit in a Reddit comment, please have my admins remove old descriptions or have users remove themselves from the description.\n___\n'
    else:
        message+=refreshMessage+'\n___\n'

#saves changes to config file
def saveConfig():
    with open('config.ini','w') as configfile:
        config.write(configfile)

'''
#Takes in a number and makes it between 1 and 26, used for a1z26
def valueBetween1And26(num):
    while(num<1 or num>26):
        if num>26:
            num-=26
        elif num<1:
            num+=26

#encrypts a string into a1z26 using an offset to shift the numbers around
def a1z26(offset, msg):
    letters = list(msg.upper())
    nums = ""
    for let in letters:
        if not(ord(let)>64 and ord(let)<91):
            if nums[len(nums)-1] is '-':
                nums = nums[0:len(nums)-1]+let
            else:
                nums = nums[0:len(nums)]+let
        else:
            num = ord(let)-64+offset
            valueBetween1And26(num)
            nums = nums+str(num)+'-'
    if nums[len(nums)-1] is '-':
        return nums[0:len(nums)-1]
    else:
        return nums

#Decrypts a1z26
def a1z26Rev(offset, msg):
    nums = list(msg.upper())
    lets = ''
    realNum  = ''
    isNum = False
    for num in nums:
        try:
            int(num)
            isNum = True
        except:
            isNum = False
        if isNum:
            realNum = realNum+num
        else:
            if realNum:
                finalNum = int(realNum)-offset
                valueBetween1And26(finalNum)
                lets = lets+str(chr(finalNum+64))
                realNum = ''
            if num is not '-':
                lets = lets+num
    if isNum:
        finalNum = int(realNum)-offset
        valueBetween1And26(finalNum)
        lets = lets+str(chr(finalNum+64))
    return lets
'''

#sends a PM to an array of 'users' with a 'custom' message and tells the 'sender' that requested the notification
def summon(sender, users, custom, links):
    global messageEnd
    global message
    failed = False;
    for usr in users:
        msg = sender+' has requested me to summon you.'
        if custom:
            msg+='\n\nHe says: '+custom
        if len(links) == 0:
            msg+='\n\nI can not provide a location of the summon.'
        else:
            msg+='\n\nPlease arrive soon to [the thread]('+links[1]+') or [the comment]('+links[0]+').'
        msg+='\n___\n'+messageEnd
        try:
            r.send_message(usr, 'You have been summoned', msg)
            #message+=usr+' summoned\n\n'
        except:
            message+=usr+' failed.\n\n'
            failed = True;
    if failed:
        message+='All users except those above have been summoned at your request.\n\n'
    else:
        message+='All users have been summoned at your request.\n\n'
    message+='\n___\n'

#change an existing user
#user is a string formatted like this: /u/name:
def changeLine(user, message):
    global refreshMsgLines
    for i in range(len(refreshMsgLines)):
        name = refreshMsgLines[i].lower().split(' ')[0]
        if user.lower() == name:
            #print('match')
            if message:
                if checkMsg(message):
                    refreshMsgLines[i] = user+' '+message+'\n\n'
                    reconstructRefresh()
                break
            else:
                refreshMsgLines.pop(i)
                reconstructRefresh()
                break

#add a user
def addLine(user, msg):
    global refreshMsgLines
    global message
    if msg:
        newLine = user+' '+msg+'\n\n'
        refreshMsgLines.append(newLine)
        reconstructRefresh()
    else:
        message+='You can not add a blank description.\n\n'
#find user
def findLine(user):
    global refreshMsgLines
    for i in range(len(refreshMsgLines)):
        name = refreshMsgLines[i].lower().split(' ')[0]
        if user == name:
            return refreshMsgLines[i]
            break

#600 char max
#no line breaks
def checkMsg(message):
    if '\n' in message or len(message) > 600:
        return False
    else:
        return True

def reconstructRefresh():
    global refreshMsgLines
    global refreshMessage
    global needSave
    firstline = True
    refreshMessage = ''
    for line in refreshMsgLines:
        refreshMessage+=line
        if firstline:
            refreshMessage+="\n\n"
            firstline = False
    config['Welcome']['refresh']=refreshMessage
    needSave = True
'''
######################################################
#              DISCORD BOT BELOW                     #
######################################################
#takes in a post, retrieves the title and link, and announces the post to the discord server
async def announcePost(post): 
    await client.wait_until_ready()
    disMessage = '@everyone Breaking News! There\'s a new post by /u/'+str(post.author)+'!\n'+str(post.short_link)
    print (disMessage)
    channel = client.get_channel('267110648075386881')
    await client.send_message(channel, disMessage)

######################################################
#               DISCORD BOT END                      #
######################################################
'''
'''
#this is the task that runs the entire bot
async def backgroundTask():
    global needSave
    await client.wait_until_ready()
    #Tells me it started without error
    print('Starting')
    while not client.is_closed:
        try:
            await checkForCommands()
            if needSave:
                saveConfig()
                needSave = False
            await asyncio.sleep(10)
        except Exception as e:
            print(e)
            await asyncio.sleep(30)

#this loop restarts the bot when it stops running
while True:
    try: 
        #runs the backgroundTask() loop in the background, so basically this starts the bot
        client.loop.create_task(backgroundTask())
        #starts the discord bot
        client.run(token)
    except:
        pass

'''
#this is the old infinite loop
#Call everything the bot needs to do here, then write the code above
while True:
     try:
         checkForCommands()
         if needSave:
             saveConfig()
             needSave = False
         time.sleep(10)
     except Exception as e:
         print(e)
         time.sleep(30) #we can change the time to whatever
