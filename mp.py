



















import os, traceback, time, os

from multiprocessing import Process, Queue, Lock
import queue


num_threads = 26
civfile = open(r'''C:\Users\jschiffler\Desktop\Text_n_Stuff\current\civil_ny.txt''')


allcivurls = Queue()
for civline in civfile:
    allcivurls.put(civline)

qlength = allcivurls.qsize()
tasks_that_are_done = Queue()




def crawler(allcivurls, tasks_that_are_done, lock):
    while True:
        lock.acquire()
        try:
            eachcivurl = allcivurls.get_nowait()
            print('here1', eachcivurl, tasks_that_are_done.qsize())
            
        except queue.Empty:
            print('here2')
            lock.release()
            break

        else:
            print('here3')

            print('here4\n\n')
            tasks_that_are_done.put('YYYYYYYYYYYYYYYYYYY' + str(os.getpid()))
            lock.release()





if __name__ == '__main__':
    lock = Lock()
    print('xxxxxxxxxxxxx', tasks_that_are_done.qsize(), qlength)

    print('join_count')



    for ii in range(num_threads):
        worker = Process(target=crawler, args=(allcivurls, tasks_that_are_done, lock))
        worker.start()



        
    while True:
        if tasks_that_are_done.qsize() >= qlength:
            print('done', tasks_that_are_done.qsize(), qlength)
            break
        else:
            print('waiting', tasks_that_are_done.qsize(), qlength)
            time.sleep(1)


    print('YYAAAAYYY')























































#!/usr/bin/python3.7

# Description: Search the provided webpages for keyword and attempt relavent crawling.

# To do:
# Phase 1: Basic function +
# proper html parsing - 404 and 403 error 4 +
# Phase 2: Basic optimization +
# limit results per baseurl. Overload to seperate set.
# lock global vars - . Use keyvalue instead?
# pathlib
# Phase 3: Advanced features
# parellelization. Queue?
# user-defined levels of crawling
# Phase 4: Distribution
# enable cross-platform
# Phase 5: GUI

#error 3, 5, 6

# Start timer
import datetime
startTime = datetime.datetime.now()

import urllib.request, urllib.parse, urllib.error, os, platform, webbrowser, traceback, time

from multiprocessing import Process, Queue
import queue



keyword = ['plant operator', 'librarian']
num_threads = 26
baseurllimit = 5


# Set OS
osname = platform.system()

# Set blacklist
if osname == 'Windows':
    blacklisthand = open(r'''C:\Users\jschiffler\Desktop\Text_n_Stuff\current\blacklist.txt''')
elif osname == 'Linux':
    blacklisthand = open(r'''/home/joepers/code/current/civ_crawl/blacklist''')
elif osname == 'Darwin':
    blacklisthand = open(r'''/home/joepers/code/current/civ_crawl/blacklist''')
else:
    print(osname, 'Unknown OS platform. Exiting...')
    exit()

blacklist = blacklisthand.read()


## change to pathlib
# Clear errorlog
if osname == 'Windows':
    errorfile = open(r'''C:\Users\jschiffler\Desktop\Text_n_Stuff\current\errorlog.txt''', "w")
elif osname == 'Linux':
    errorfile = open(r'''/home/joepers/code/current/civ_crawl/errorlog''', "w")
elif osname == 'Darwin':
    errorfile = open(r'''/home/joepers/code/current/civ_crawl/errorlog''', "w")
    
errorfile.write('')

# Clear results
if osname == 'Windows':
    comp_hand = open(r'''C:\Users\jschiffler\Desktop\Text_n_Stuff\current\results.txt''', "w")
elif osname == 'Linux':
    comp_hand = open(r'''/home/joepers/code/current/civ_crawl/results''', "w")

comp_hand.write('')

# Get portal URLs from file
if osname == 'Windows':
    civfile = open(r'''C:\Users\jschiffler\Desktop\Text_n_Stuff\current\sar.txt''')
elif osname == 'Linux':
    civfile = open(r'''/home/joepers/code/current/civ_crawl/civil_ny''')
elif osname == 'Darwin':
    civfile = open(r'''/home/joepers/code/current/civ_crawl/civil_ny''')

# Store portal urls in queue
#allcivurls = multiprocessing.JoinableQueue()
allcivurls = Queue()
for civline in civfile:
    #civline = civline0.strip()
    allcivurls.put(civline)

qlength = allcivurls.qsize()
tasks_that_are_done = Queue()




t = {}
wait_count = 0
keywordurlset = set()
checkedurls = set()
#block_size = len(allcivurls) / num_threads + 1)
block_count = 0
#block_begin = 0
#block_end = block_size
urlblock = {}
errorurls = {}
baseurllimitset = {}
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'
td = 0



######  Define the crawling function  ######
def crawler(allcivurls, tasks_that_are_done):

    while True:

        print('\n\n\n\n ============================ Start function =========================== PID =', os.getpid())
        progresscount = 1
        try:
            # Begin fetching    
            eachcivurl = allcivurls.get_nowait()
            print('here1')

        except queue.Empty:
            print('here2')            
            break
        

        else:
            print('eachcivurl = ', eachcivurl)

            # Skip checked pages
            if eachcivurl in checkedurls:
                print('Skipping', eachcivurl)
                continue
                

            eachcivurl = eachcivurl.lower()
            baseurllimitset.clear
            urllistgood = {}
            urllistgood.clear
            urllistgood.setdefault(eachcivurl, [])
            urllistprefilter = []
            urllistprefilter.clear()
            urllist1 = []
            urllist1.clear()
            urllist2 = []
            urllist2.clear()
            alltags = set()
            alltags.clear()
            abspath = None

            print('\n\n ~~~~~~~~~~~~~~~~~~~~~~~~~~ Next civurl ~~~~~~~~~~~~~~~~~~~~~~~~~~  \n PID =', os.getpid(), 'Progress = ', progresscount)
            progresscount += 1
            baseurl = eachcivurl

            # Get html from url
            try:           
                # Spoof user agent
                request = urllib.request.Request(eachcivurl,headers={'User-Agent': user_agent})
                html = urllib.request.urlopen(request, timeout=20)

            except Exception as errex:
                print('error 1: url request at', eachcivurl)
                errorurls[eachcivurl] = 'error 1:', errex
                checkedurls.add(eachcivurl)
                continue
                

            # Decode if necessary
            charset_encoding = html.info().get_content_charset()
            print('Char encoding =', charset_encoding)
            
        ## review
            if charset_encoding == None:
                try:
                    #dechtml = html.read().decode(errors='ignore')
                    dechtml = html.read().decode()
                except Exception as errex:
                    print('error 2: decode at ', eachcivurl)
                    errorurls[eachcivurl] = 'error 2:', str(errex)[:999]
                    checkedurls.add(eachcivurl)
                    continue
                    
            else:
                try:
                    dechtml = html.read().decode(charset_encoding)
                except Exception as errex:
                    print('error 2: decode at ', eachcivurl)
                    errorurls[eachcivurl] = 'error 2:', str(errex)[:999]
                    checkedurls.add(eachcivurl)
                    continue
                    

            dechtml1 = dechtml.lower()

            # Search for keyword on page
            if any(zzzz in dechtml1 for zzzz in keyword):
                print('\n~~~~~~ Keyword match ~~~~~~\n')
                
                # Remove trailing slash
                if eachcivurl.endswith('/'):
                    eachcivurl = eachcivurl.rsplit('/', 1)[0]

                keywordurlset.add(eachcivurl)

            # Add to checked pages set
            checkedurls.add(eachcivurl)
            
            ## href= as delimiter?
            # Seperate html into lines using <a delimiter
            htmllines = dechtml1.split('<a ')

            # End lines using </a> delimiter and add to alltags set
            for eachhtmlline in htmllines:

                ## Remove?
                # Omit lengthy <!DOCTYPE tag
                if eachhtmlline.startswith('<!doctype'):
                    print ('!DOCTYPE tag omitted\n')
                    continue
                else:
                    loc = eachhtmlline.find('</a>')
                    result = eachhtmlline[:loc]
                    alltags.add(result)

            # Set jobwords and bunkwords
            jobwords = ['employment', 'job', 'opening', 'exam', 'test', 'postions', 'civil', 'career', 'human', 'personnel']
            bunkwords = ['javascript:', '.pdf', '.jpg', '.ico', '.doc', 'mailto:', 'tel:', 'description', 'specs', 'specification', 'guide', 'faq', 'images']

            # Determine if the tag contains a jobword
            for tag in alltags:

                # Append only the url to the list
                if tag.count('href') > 0:
                    urlline0 = tag.split('href')[1]

                    if any(xxx in urlline0 for xxx in jobwords):

                        # Determine if double or single quote comes first in tag
                        dqloc = urlline0.find('"')
                        sqloc = urlline0.find("'")

                        if dqloc < sqloc:
                            if dqloc > -1:
                                quovar = '"'
                            else: quovar = "'"
                        elif dqloc > sqloc:
                            if sqloc > -1:
                                quovar = "'"
                            else: quovar = '"'
                        
                        urlline = urlline0.split(quovar)[1]

                        # Convert any rel paths to abs
                        abspath = urllib.parse.urljoin(baseurl, urlline)

                        ## keep queries?
                        # Remove queries and fragments from url
                        abspath = abspath.split('?')[0].split('#')[0]
                        abspath = abspath.lower()
                        urllistprefilter.append(abspath)

                        # Exclude if the tag contains a bunkword
                        if not any(yyy in tag for yyy in bunkwords):
                            urllist1.append(abspath)

                            # Exclude if the abspath is on the Blacklist
                            if not abspath in blacklist:
                                urllist2.append(abspath)

                                # Exclude if the abspath is a checked page
                                if not abspath in checkedurls:

                                    # Remove trailing slash
                                    if abspath.endswith('/'):
                                        abspath = abspath.rsplit('/', 1)[0]
                                    
                                    urllistgood.setdefault(eachcivurl, []).append(abspath)
                                               
                else:
                    #errorurls[tag] = 'error 5: no "href="'
                    continue

            # Show excluded urls
            excludedbybw = list(set(urllistprefilter) - set(urllist1))
            excludedbybl = list(set(urllist1) - set(urllist2))
            try:
                excludedbydups = list(set(urllist2) - set(urllistgood[eachcivurl]))

                print('excluded by bunkwords = ', len(excludedbybw), '\nexcluded by blacklist = ', len(excludedbybl), excludedbybl, '\nexcluded by dups = ', len(excludedbydups), excludedbydups, '\nul1nbw = ', len(urllist1), '\nul2nbl = ', len(urllist2), '\nulgndups = ', len(urllistgood[eachcivurl]))

            except Exception as errex:
                print('error 3: excludedbydups at', abspath)
                errorurls[abspath] = 'error 3:', errex
                





            # Begin crawl
            print('\n-------------------- Begin crawl ----------------------  \n PID =', os.getpid(), '\n', eachcivurl,)

            for workingurl in urllistgood[eachcivurl]:
                
                # Skip checked pages
                if workingurl in checkedurls:
                    print('Skipping', workingurl)
                    continue
            
                print('\n',workingurl)

                # Get html from url
                try:
                    # Spoof user agent
                    workingrequest = urllib.request.Request(workingurl,headers={'User-Agent': user_agent})
                    workinghtml = urllib.request.urlopen(workingrequest, timeout=20)

                except Exception as errex:
                    print('error 4: url request at', workingurl)
                    errorurls[workingurl] = 'error 4:', errex
                    checkedurls.add(workingurl)
                    continue

                # Decode if necessasry
                charset_encoding = workinghtml.info().get_content_charset()
                print('Char encoding =', charset_encoding)

                if charset_encoding == None:
                    try:
                        decworkinghtml = workinghtml.read().decode()
                        #decworkinghtml = workinghtml.read().decode(errors='ignore')
                    except Exception as errex:
                        print('error 8: decode at ', workingurl)
                        errorurls[workingurl] = 'error 8:', str(errex)[:999]
                        checkedurls.add(workingurl)
                        continue
                else:
                    try:
                        decworkinghtml = workinghtml.read().decode(charset_encoding)
                    except Exception as errex:
                        print('error 9: decode at ', workingurl)
                        errorurls[workingurl] = 'error 9:', str(errex)[:999]
                        checkedurls.add(workingurl)
                        continue

                decworkinghtml1 = decworkinghtml.lower()
                # Search for keyword on page
                if any(zzz in decworkinghtml1 for zzz in keyword):
                    print('\n~~~~~~ Keyword match ~~~~~~\n')
        ## review                
                    baseurllimitset[baseurl] = {}
                    if len(baseurllimitset[baseurl]) < baseurllimit:
                        keywordurlset.add(workingurl)
                    else:
                        print('Match omitted. Baseurl limit exceeded.')
                        baseurllimitset[baseurl].add(workingurl)
                #else:
                    #print('~~~ No match ~~~\n')

                # Add to checked pages set
                checkedurls.add(workingurl)



            print('------------ End of function ------------  PID =', os.getpid())

        finally:
            print('here3\n\n')            
            tasks_that_are_done.put('YYYYYYYYYYYYYYYYYYY' + str(os.getpid()))



####   End of function   ####




if __name__ == '__main__':
    join_list = 0
    print('xxxxxxxxxxxxx', tasks_that_are_done.qsize(), qlength)



    for ii in range(num_threads):
        worker = Process(target=crawler, args=(allcivurls, tasks_that_are_done))
        #worker.setDaemon(True)
        join_list += 1
        print('join_list', join_list)
        worker.start()
        
    print('yyyyyyyyyyyyy', tasks_that_are_done.qsize(), qlength)
    
    for ooo in range(join_list):
        print('\n\nWaiting for threads ...', wait_count, join_list)
        #worker.join()
        wait_count += 1

while True:
    if tasks_that_are_done.qsize() >= qlength:   
        print('zzzzzzzzzzzz', tasks_that_are_done.qsize(), qlength)
        break
    else:
        time.sleep(1)
        print('aaaaaaaaaaaa', tasks_that_are_done.qsize(), qlength)



print(' ==========================================================')




finalkeywordurlset = set()

# Write results and errorlog
if osname == 'Windows':
    writeresults = open(r'''C:\Users\jschiffler\Desktop\Text_n_Stuff\current\results.txt''', "a")
    writeerrors = open(r'''C:\Users\jschiffler\Desktop\Text_n_Stuff\current\errorlog.txt''', "a")

elif osname == 'Linux':
    writeresults = open(r'''/home/joepers/code/current/civ_crawl/results''', "a")
    writeerrors = open(r'''/home/joepers/code/current/civ_crawl/errorlog''', "a")
    
for kk in keywordurlset:
    kk = kk.split('://')[1]
    kk = str(kk)

    if kk.count('www.') > 0:
        kk = kk.split('www.')[1]

    kk = kk.strip("']")
    kk = kk.strip()
    finalkeywordurlset.add(kk)

for kk in finalkeywordurlset:
    kws = str(kk + '\n')
    writeresults.write(kws)

for k, v in errorurls.items():
    vk = str((v, '::', k))
    writeerrors.write(vk + '\n\n')
try:
    # Calculate error rate
    error_rate = len(errorurls) / len(checkedurls)
    if error_rate < 0.02:
        error_rate_desc = '(low)'
    elif error_rate < 0.2:
        error_rate_desc = '(medium)'
    else:
        error_rate_desc = '(high)'
except:
    error_rate_desc = '(high)'

# Stop timer and display stats
duration = datetime.datetime.now() - startTime
print('\n\n\nPages checked =', len(checkedurls), '\nDuration =', duration.seconds, 'seconds', '\nErrors detected =', len(errorurls), error_rate_desc)



# Display results
print('\n\n\n   ################ ', len(finalkeywordurlset), ' matches found ', ' ################\n')
for i in sorted(list(finalkeywordurlset)):
    print(i)

# Display baseurl limit exceedances
if len(baseurllimitset.values()) > 1:
    print('\n\nBaseurl limit exceedances at:\n', baseurllimitset.values())
    writeresults.write('\n\nBaseurl limit exceedances at:\n' + str(baseurllimitset.values()))

'''# Open in browser
if len(keywordurlset) > 0:
    browserresp = input('\n\nOpen all results in browser?\ny/n\n')
    if browserresp.lower() == 'y' or browserresp.lower() == 'yes':
        for eachbrowserresult in keywordurlset:
            webbrowser.open(eachbrowserresult)

'''
















