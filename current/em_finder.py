
# Description: Crawl webpages and rank links based on likelihood of containing job postings.



# To do:
# AP and wnyric are not totally centralized? eg: https://www.applitrack.com/saugertiesk12/onlineapp/jobpostings/view.asp
# output all 4 items +
# use redirects instead of original URLs
# checked_pages has no jbw conf values. only None, redirect, or error
# dont output dups +

# modify for use with civs. ie: 
# dont output if only result is orignal URL








import datetime, requests, psutil, gzip, os, queue, re, socket, time, traceback, urllib.parse, urllib.request, webbrowser, ssl
from os.path import expanduser
from multiprocessing import active_children, Lock, Manager, Process, Queue, Value
from math import sin, cos, sqrt, atan2, radians
from http.cookiejar import CookieJar
from bs4 import BeautifulSoup




# Start timer
startTime = datetime.datetime.now()

# Make jorbs directory in user's home directory
jorb_home = '/home/joepers/jj_em_finder'
if not os.path.exists(jorb_home):
    os.makedirs(jorb_home)


# Make date dir to put results into
dater = datetime.datetime.now().strftime("%x").replace('/', '_')
dater_path = os.path.join(jorb_home, dater)
if not os.path.exists(dater_path):
    os.makedirs(dater_path)


# User agent
user_agent_str = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0'

# Compile regex paterns for finding hidden HTML elements
style_reg = re.compile("(display\s*:\s*(none|block);?|visibility\s*:\s*hidden;?)")
#class_reg = re.compile('(hidden-sections?|sw-channel-dropdown)')
class_reg = re.compile('(hidden-sections?|dropdown|has-dropdown|sw-channel-dropdown|dropdown-toggle)')

## unn?
# Omit these pages
blacklist = ('cc.cnyric.org/districtpage.cfm?pageid=112', 'co.essex.ny.us/personnel', 'co.ontario.ny.us/94/human-resources', 'countyherkimer.digitaltowpath.org:10069/content/departments/view/9:field=services;/content/departmentservices/view/190', 'countyherkimer.digitaltowpath.org:10069/content/departments/view/9:field=services;/content/departmentservices/view/35', 'cs.monroecounty.gov/mccs/lists', 'herkimercounty.org/content/departments/view/9:field=services;/content/departmentservices/view/190', 'herkimercounty.org/content/departments/view/9:field=services;/content/departmentservices/view/35', 'jobs.albanyny.gov/default/jobs', 'monroecounty.gov/hr/lists', 'monroecounty.gov/mccs/lists', 'mycivilservice.rocklandgov.com/default/jobs', 'niagaracounty.com/employment/eligible-lists', 'ogdensburg.org/index.aspx?nid=345', 'penfield.org/multirss.php', 'tompkinscivilservice.org/civilservice/jobs', 'tompkinscivilservice.org/civilservice/jobs')

# Omit these domains
blacklist_domains = ('twitter.com')

# Include links that include any of these
# High confidence civ jbws
jobwords_civ_high = ('continuous recruitment', 'employment', 'job listing', 'job opening', 'job posting', 'job announcement', 'job opportunities', 'jobs available', 'available positions', 'open positions', 'available employment', 'career opportunities', 'employment opportunities', 'current vacancies', 'current job', 'current employment', 'current opening', 'current posting', 'current opportunities', 'careers at', 'jobs at', 'jobs @', 'work at', 'employment at', 'find your career', 'browse jobs', 'search jobs', 'continuous recruitment', 'vacancy postings', 'prospective employees', 'upcoming exam', 'exam announcement', 'examination announcement', 'civil service opportunities', 'civil service exam', 'civil service test', 'current civil service','open competitive', 'open-competitive')

# Low confidence civ jbws
jobwords_civ_low = ('open to', 'job', 'job seeker', 'job title', 'civil service', 'exam', 'examination', 'test', 'positions', 'careers', 'human resource', 'personnel', 'vacancies', 'current exam', 'posting', 'opening', 'vacancy')


# High confidence sch and uni jbws
jobwords_su_high = ('continuous recruitment', 'employment', 'job listing', 'job opening', 'job posting', 'job announcement', 'job opportunities', 'job vacancies', 'jobs available', 'available positions', 'open positions', 'available employment', 'career opportunities', 'employment opportunities', 'current vacancies', 'current job', 'current employment', 'current opening', 'current posting', 'current opportunities', 'careers at', 'jobs at', 'jobs @', 'work at', 'employment at', 'find your career', 'browse jobs', 'search jobs', 'continuous recruitment', 'vacancy postings', 'prospective employees')

# Low confidence sch and uni jbws
jobwords_su_low = ('join', 'job seeker', 'job', 'job title', 'positions', 'careers', 'human resource', 'personnel', 'vacancies', 'posting', 'opening', 'recruitment', '>faculty<', '>staff<', '>adjunct<', '>academic<', '>support<', '>instructional<', '>administrative<', '>professional<', '>classified<', '>coaching<', 'vacancy')

# Worst offenders
#offenders = ['faculty', 'staff', 'professional', 'management', 'administrat', 'academic', 'support', 'instructional', 'adjunct', 'classified', 'teach', 'coaching']

## switching to careers solves all these
# career services, career peers, career prep, career fair, volunteer
## application
# Exclude links that contain any of these
bunkwords = ('academics', 'professional development', 'career development', 'javascript:', '.pdf', '.jpg', '.ico', '.rtf', '.doc', 'mailto:', 'tel:', 'icon', 'description', 'specs', 'specification', 'guide', 'faq', 'images', 'exam scores', 'resume-sample', 'resume sample', 'directory', 'pupil personnel')

# olas
# https://schoolapp.wnyric.org/ats/job_board
# recruitfront

# Multiprocessing lock for shared objects
lock = Lock()





# Removes extra info from urls to prevent duplicate pages from being checked more than once
def dup_checker_f(dup_checker):
    print(os.getpid(), 'start dup check:', dup_checker)

    # Remove scheme
    if dup_checker.startswith('http://') or dup_checker.startswith('https://'):
        dup_checker = dup_checker.split('://')[1]
    else:
        print('__Error__ No scheme at:', dup_checker)


    '''
    ## unn
    ## and must supply errorurls_man_dict as arg
    # Catch no scheme error
    else:
        with lock:
            print(os.getpid(), '\njj_error 2: No scheme:', dup_checker)
            errorurls_man_dict[dup_checker] = ['jj_error 2', 'No scheme', 111]
            outcome(checkedurls_man_list, dup_checker, 'jj_error 2')

        return dup_checker
    '''

    # Remove www. and variants
    if dup_checker.startswith('www.'):
        dup_checker = dup_checker.split('www.')[1]
    elif dup_checker.startswith('www2.'):
        dup_checker = dup_checker.split('www2.')[1]
    elif dup_checker.startswith('www3.'):
        dup_checker = dup_checker.split('www3.')[1]

    # Remove fragments
    dup_checker = dup_checker.split('#')[0]

    ## Remove double forward slashes?
    dup_checker = dup_checker.replace('//', '/')

    # Remove trailing whitespace and slash and then lowercase it
    dup_checker = dup_checker.strip().strip('/').lower()

    return dup_checker


# Determine if url has been checked already and optionally add to queue
def proceed_f(abspath, working_list, checkedurls_man_list, skipped_pages, current_crawl_level, all_urls_q, total_count, add_to_queue_b):

    # Call dup checker function before putting in queue
    dup_checker = dup_checker_f(abspath)

    # Exclude checked pages
    for i in checkedurls_man_list:
        if i == None:
            print('__ error. None in cml', checkedurls_man_list)
            continue
        if dup_checker == i[0]:
            print(os.getpid(), 'Skipping:', dup_checker)
            with lock:
                try:
                    skipped_pages.value += 1
                except Exception as errex: print(errex)

            # Declare not to proceed
            return False

    '''
    ##if dup_checker in checkedurls_man_list or dup_checker in blacklist:
    # Exclude checked pages
    if dup_checker in checkedurls_man_list:
        print(os.getpid(), 'Skipping:', dup_checker)
        with lock:
            skipped_pages.value += 1

        # Declare not to proceed
        return False
    '''

    # Exclude if the abspath is on the Blacklist
    if dup_checker in blacklist:
        print(os.getpid(), 'Blacklist invoked:', dup_checker)
        try:
            with lock:
                skipped_pages.value += 1
        except Exception as errex:
            print(errex)
        return False    


    # Form domain by splitting after 3rd slash
    domain = '/'.join(abspath.split('/')[:3])
    domain_dup = dup_checker_f(domain)

    # Exclude if the abspath is on the Blacklist
    if domain_dup in blacklist_domains:
        print(os.getpid(), 'Domain blacklist invoked:', domain_dup)
        try:
            with lock:
                skipped_pages.value += 1
        except Exception as errex:
            print(errex)
        return False


    # Add abspath to queue if add_to_queue_b is True
    if add_to_queue_b:

        # Create new working list: [URL, crawl level, portal URL, jbw type]
        new_working_list = [abspath, current_crawl_level, working_list[2], working_list[3]]
        print(os.getpid(), 'Putting list into queue:', new_working_list)

        # Put new working list in queue
        with lock:
            try:
                all_urls_q.put(new_working_list)
                total_count.value += 1
            except Exception as errex:
                print(errex)

    # Add dup_checker, jbw type, and jbw confidence placeholder to checked pages list
    print(os.getpid(), 'Adding to cml with None:', dup_checker)
    with lock:
        try:
            checkedurls_man_list.append([dup_checker, None])
        except Exception as errex:
            print(errex)


    # Declare to proceed
    return True



# Update outcome of each URL with jbw conf
def outcome(checkedurls_man_list, url, conf_val):

    # Convert URL to dup checker
    url = dup_checker_f(url)

    ## Catch multiple matches?
    # Attach jbw conf to URL in checkedurls_man_list
    #with lock:
    for each_url in checkedurls_man_list:
        if each_url[0] == url:
            remover = each_url
            break

            # Manager will not be aware of updates to items. Must append new item.

    # Catch no match
    else:
        print(os.getpid(), '__Error__ (1) not found in checkedurls_man_list:', url)
        return

    ## combine next two sections
    ## Remove old entry
    with lock:
        try:
            checkedurls_man_list.remove(remover)
        except Exception as errex:
            print(os.getpid(), '__Error__ (2) not found in checkedurls_man_list:', url)
            print(errex)
            return
            
    ## Append new entry
    new_i = [url, conf_val]
    with lock:
        try:
            checkedurls_man_list.append(new_i)
            print(os.getpid(), 'Updated outcome for / with:', url, conf_val)
        except Exception as errex:
            print(os.getpid(), '__Error__ (3) not found in checkedurls_man_list:', url)
            print(errex)
            

# Define HTML request function
def html_requester_f(workingurl, current_crawl_level, jbw_type, errorurls_man_dict, portalurl, sort_dict):

    ## Ignore SSL certificate errros
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    '''
    >>> context = ssl.SSLContext()
    >>> context.verify_mode = ssl.CERT_REQUIRED
    >>> context.check_hostname = True
    >>> context.load_verify_locations("/etc/ssl/certs/ca-bundle.crt")
    '''


    # Request html using a spoofed user agent, cookiejar, and timeout
    try:
        cj = CookieJar()
        ##
        req = urllib.request.Request(workingurl, headers={'User-Agent': user_agent_str}, unverifiable=False)
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        html = opener.open(req, timeout=10)
        
        # Catch new redirected url
        red_url = html.geturl()
        return html, red_url

    # Catch and log HTTP request errors
    except Exception as errex:

        # Retry on timeout error
        if 'timed out' in str(errex):
            print('jj_error 3: Request timeout:', workingurl)

            # Append to error log
            add_errorurls_f(workingurl, 'jj_error 3', str(errex), current_crawl_level, jbw_type, portalurl, errorurls_man_dict)

            # Declare a retry is needed
            return True, workingurl

        # Don't retry on 404 or 403 error
        elif 'HTTP Error 404:' in str(errex) or 'HTTP Error 403:' in str(errex):
            print('jj_error 4: HTTP 404/403 request:', workingurl)
            add_errorurls_f(workingurl, 'jj_error 4', str(errex), current_crawl_level, jbw_type, portalurl, errorurls_man_dict)

            # Declare not to retry
            return False, workingurl

        # Retry on other error
        else:
            print('jj_error 5: Other request', workingurl)
            add_errorurls_f(workingurl, 'jj_error 5', str(errex), current_crawl_level, jbw_type, portalurl, errorurls_man_dict)
            return True, workingurl




# Add URLs and info to the errorlog. Allows multiple errors (values) to each URL (key)
def add_errorurls_f(workingurl, err_code, err_desc, current_crawl_level, jbw_type, portalurl, errorurls_man_dict):

    # Append more values to key if key exists
    if workingurl in errorurls_man_dict:

        # Manager will not be aware of update to dict item unless you do this
        prev_item = errorurls_man_dict[workingurl]
        prev_item.append([err_code, err_desc, current_crawl_level])

        with lock:
            try:
                errorurls_man_dict[workingurl] = prev_item
            except Exception as errex:
                print(errex)

        '''
        # Assign a number to urls already in errorurls_man_dict
        num = 0
        while workingurl in errorurls_man_dict:
            num += 1
            workingurl = workingurl + '___' + str(num)

        with lock:
            errorurls_man_dict[workingurl] = [err_code, err_desc, current_crawl_level]
        print(os.getpid(), 'innn', errorurls_man_dict)
        '''

    # Create key if key doesn't exist
    else:
        with lock:
            try:
                errorurls_man_dict[workingurl] = [err_code, err_desc, current_crawl_level, jbw_type, portalurl]
            except Exception as errex:
                print(errex)

        outcome(checkedurls_man_list, workingurl, err_code)


# Define the crawling function
def scraper(all_urls_q, max_crawl_depth, checkedurls_man_list, errorurls_man_dict, skipped_pages, prog_count, total_count, jbw_tally_man_l, sort_dict):
    print(os.getpid(), os.getpid(), '====== Start scraper function ======')
    while True:

        # Get a url list from the queue
        try:
            with lock:
                working_list = all_urls_q.get(False)

        # If queue is empty wait and try again
        except queue.Empty:
            time.sleep(2)
            try:
                with lock:
                    working_list = all_urls_q.get(False)

            # Exit function if queue is empty again
            except queue.Empty:
                print(os.getpid(), os.getpid(), 'Queue empty. Closing process...')
                break



        # Begin fetching
        else:
            try:
                print(os.getpid(), 'working_list =', working_list)
                #for x in checkedurls_man_list: print(os.getpid(), x)
                # working_list contents: [workingurl, current_crawl_level, portal URL, jbw type]
                # Seperate working list
                workingurl = working_list[0]
                current_crawl_level = working_list[1]
                portalurl = working_list[2]
                jbw_type = working_list[3]

                ## remove this?
                ## there will never be a dup in the queue
                # Skip checked pages
                #add_to_queue_b = False
                #proceed_pass = proceed_f(workingurl, working_list, checkedurls_man_list, skipped_pages, current_crawl_level, all_urls_q, total_count, add_to_queue_b, blacklist)

                #if not proceed_pass: continue

                # Form domain by splitting after 3rd slash
                domain = '/'.join(workingurl.split('/')[:3])



                # Retry loop on request and decode errors
                loop_success = False
                for loop_count in range(3):

                    # Get html and red_url tuple
                    html_url_t = html_requester_f(workingurl, current_crawl_level, jbw_type, errorurls_man_dict, portalurl, sort_dict)


                    # Get HTML and redirected URL
                    html = html_url_t[0]
                    red_url = html_url_t[1]

                    # Prevent trivial changes (eg: https upgrade) from being viewed as different urls
                    workingurl_dup = dup_checker_f(workingurl)
                    red_url_dup = dup_checker_f(red_url)

                    # Follow redirects
                    if workingurl_dup != red_url_dup:
                        print(os.getpid(), 'Redirect from/to:', workingurl, red_url)

                        # Update checked pages conf value to redirected
                        conf_val = 'redirected'
                        outcome(checkedurls_man_list, workingurl, conf_val)

                        # Assign new redirected url
                        workingurl = red_url

                        # Skip checked pages using redirected URL
                        add_to_queue_b = False
                        proceed_pass = proceed_f(red_url, working_list, checkedurls_man_list, skipped_pages, current_crawl_level, all_urls_q, total_count, add_to_queue_b)

                        # Break request loop if redirected URL has been checked already
                        if not proceed_pass: break                   




                    # html_requester_f returns True to indicate a needed retry
                    if html_url_t[0] == True:
                        print(os.getpid(), 'Retry request loop:', workingurl)
                        continue

                    # html_requester_f returns False to indicate don't retry
                    elif html_url_t[0] == False:
                        print(os.getpid(), 'Break request loop:', workingurl)
                        break

                    # Declare successful and exit loop
                    else:
                        loop_success = True
                        print(os.getpid(), 'HTML request success:', workingurl)
                        #for x in checkedurls_man_list: print(os.getpid(), x)
                        break


                # Skip to next URL if loop is exhausted
                else:
                    print(os.getpid(), 'Loop exhausted:', workingurl)
                    #continue

                # Fatal error detection
                if loop_success == False:
                    print(os.getpid(), 'Loop failed:', workingurl)

                    ## not final if using domain as fallback?
                    # Append a final error designation
                    prev_item = errorurls_man_dict[workingurl]
                    prev_item.append('jj_final_error')

                    #with lock:
                    #    try:
                    errorurls_man_dict[workingurl] = prev_item
                    #    except Exception as errex:
                    #print(errex)


                    # If portal request failed, use domain as fallback one time
                    if current_crawl_level == 0:

                        # Skip if url is same as the domain
                        if workingurl != domain:

                            # Put fallback url into queue
                            #with lock:

                            add_to_queue_b = True
                            proceed_f(domain, working_list, checkedurls_man_list, skipped_pages, current_crawl_level, all_urls_q, total_count, add_to_queue_b)

                            #all_urls_q.put([domain, -1, portalurl, jbw_type])

                            # Add dup_checker and jbw confidence placeholder to checked pages list
                            #domain_dup = dup_checker_f(domain)
                            #checkedurls_man_list.append([domain_dup, None])

                            # Increment queue length to use as progress report
                            #total_count.value += 1

                    # Skip to next URL on fatal error
                    continue

                '''
                # Get HTML and redirected URL
                html = html_url_t[0]
                red_url = html_url_t[1]
                #print(os.getpid(), 'origandred:', workingurl, red_url)

                # Prevent trivial changes (eg: https upgrade) from being viewed as different urls
                workingurl_dup = dup_checker_f(workingurl)
                red_url_dup = dup_checker_f(red_url)

                # Follow redirects
                if workingurl_dup != red_url_dup:
                    print(os.getpid(), 'Redirect from/to:', workingurl, red_url)

                    # Skip checked pages using redirected URL
                    add_to_queue_b = False
                    proceed_pass = proceed_f(red_url, working_list, checkedurls_man_list, skipped_pages, current_crawl_level, all_urls_q, total_count, add_to_queue_b)

                    # Skip if redirected URL has been checked already
                    if not proceed_pass: continue

                    # Update checked pages conf value to redirected
                    conf_val = 'redirected'
                    outcome(checkedurls_man_list, workingurl, conf_val)

                    # Assign new redirected url
                    workingurl = red_url
                '''
                
                if html == True or html == False: 
                    print('how???', workingurl)
                    continue

                # Select body
                soup = BeautifulSoup(html, 'html5lib')
                soup = soup.find('body')

                # Clear old html to free up memory
                html = None

                if soup is None:
                    print(os.getpid(), '__Empty soup0:', workingurl)
                    continue

                # Keep a soup for finding links and another for saving visible text
                vis_soup = soup

                # Remove script, style, and empty elements
                for i in vis_soup(["script", "style"]):
                    i.decompose()

                ## unn
                # Iterate through and remove all of the hidden style attributes
                r = vis_soup.find_all('', {"style" : style_reg})
                for x in r:
                    #print(os.getpid(), 'Decomposed:', workingurl, x)
                    x.decompose()

                # Type="hidden" attribute
                r = vis_soup.find_all('', {"type" : 'hidden'})
                for x in r:
                    #print(os.getpid(), 'Decomposed:', workingurl, x)
                    x.decompose()

                # Hidden section(s) and dropdown classes
                for x in vis_soup(class_=class_reg):
                    #print(os.getpid(), 'Decomposed:', workingurl, x)
                    x.decompose()

                
                ## This preserves whitespace across lines. Prevents: 'fire departmentapparatuscode compliance'
                # Remove unnecessary whitespace. eg: multiple newlines, spaces, and all tabs
                vis_soup = str(vis_soup.text)

                ##
                vis_soup = re.sub("\s{2,}", " ", vis_soup)
                '''
                regex here
                '''


                # Use lowercase visible text for comparisons
                vis_soup = vis_soup.lower()

                if vis_soup is None:
                    print(os.getpid(), '__Empty soup1:', workingurl)

                    ## there may be links to get
                    continue


                # Set jbw type based on portal jbw type
                if working_list[3] == 'civ':
                    jobwords_high_conf = jobwords_civ_high
                    jobwords_low_conf = jobwords_civ_low
                else:
                    jobwords_high_conf = jobwords_su_high
                    jobwords_low_conf = jobwords_su_low

                # Count jobwords on the page
                jbw_count = 0
                for i in jobwords_low_conf:
                    if i in vis_soup: jbw_count += 1
                for i in jobwords_high_conf:
                    if i in vis_soup: jbw_count += 2


                # Append URL and jobword confidence to portal URL dict key
                with lock:
                    if portalurl in sort_dict.keys():
                        prev_item = sort_dict[portalurl]
                        prev_item.append([workingurl, jbw_count])
                        sort_dict[portalurl] = prev_item

                    else:
                        sort_dict[portalurl] = [[workingurl, jbw_count]]

                


                '''
                ## Catch multiple matches?
                # Attach jbw conf to URL in checkedurls_man_list
                with lock:
                    for i in checkedurls_man_list:
                        if i[0] == red_url_dup:

                            # Manager will not be aware of updates to items. Must append new item.
                            checkedurls_man_list.remove(i)
                            new_i = [red_url_dup, jbw_count]
                            checkedurls_man_list.append(new_i)
                            print(os.getpid(), i)
                            break

                    # Catch no match
                    else: print(os.getpid(), red_url_dup, 'not found in checkedurls_man_list. __Error__\n\n', 'cml=', checkedurls_man_list)
                '''




                # Search for pagination class before checking crawl level
                for i in soup.find_all(class_='pagination'):

                    # Find anchor tags
                    for ii in i.find_all('a'):

                        # Find "next" page url
                        if ii.text.lower() == 'next':

                            #Get absolute url
                            abspath = urllib.parse.urljoin(domain, ii.get('href'))

                            # Add to queue
                            print(os.getpid(), workingurl, 'Adding pagination url:', abspath)
                            add_to_queue_b = True
                            proceed_f(abspath, working_list, checkedurls_man_list, skipped_pages, current_crawl_level, all_urls_q, total_count, add_to_queue_b)



                # Start relavent crawler
                if current_crawl_level >= max_crawl_depth:
                    continue

                # Increment crawl level
                print(os.getpid(), 'Starting crawler:', working_list)
                current_crawl_level += 1

                # Seperate soup into anchor tags
                alltags = []
                for i in soup.find_all('a'):

                    # Build list of anchors and parents of single anchors
                    pp = i.parent
                    if len(pp.find_all('a')) == 1:
                        alltags.append(pp)
                    else:
                        alltags.append(i)


                # Free up some memory
                soup = None

                # Set jbws confidence based on element content
                for tag in alltags:

                    # Get element content
                    bs_contents = str(tag.text).lower()

                    # Set high conf if match is found
                    if any(www in bs_contents for www in jobwords_high_conf):
                        #print(os.getpid(), 'High conf found:', workingurl, bs_contents)
                        jobwords_ephemeral = jobwords_high_conf
                        break
                    else:
                        jobwords_ephemeral = jobwords_low_conf


                # Parse elements
                fin_l = []
                for tag in alltags:

                    # Skip elements without content
                    if tag.name == 'a':
                        if not tag.text.strip():
                            continue
                    else:
                        if not tag.a.text.strip():
                            continue

                    # Help worst offenders
                    if tag.name == 'a':
                        tag.insert(0, '>')
                        tag.insert(4, '<')
                    else:
                        tag.a.insert(0, '>')
                        tag.a.insert(4, '<')

                    # Use lower tag for bunkwords search only
                    lower_tag = str(tag).lower()

                    # Get the tag contents
                    bs_contents = str(tag.text).lower()

                    # Skip these exclusions if all links is invoked
                    ## all links should remain as an option
                    #if not all_links_arg:

                    # Proceed if the tag contents contain a high confidence jobword
                    if not any(xxx in bs_contents for xxx in jobwords_ephemeral):
                        #print(os.getpid(), 'No job words detected:', workingurl, bs_contents[:99])
                        continue
                    #else: print(os.getpid(), 'jbw match:', workingurl, bs_contents)

                    # Exclude if the tag contains a bunkword
                    if any(yyy in lower_tag for yyy in bunkwords):
                        print(os.getpid(), 'Bunk word detected:', workingurl, lower_tag[:99])
                        continue

                    # Build list of successful anchors
                    fin_l.append(tag)


                # Prepare the URL for entry into the queue
                for fin_tag in fin_l:

                    lower_tag = str(fin_tag).lower()

                    # Jbw tally
                    for i in jobwords_low_conf:
                        if i in lower_tag:
                            with lock:
                                jbw_tally_man_l.append(i)

                    for i in jobwords_high_conf:
                        if i in lower_tag:
                            with lock:
                                jbw_tally_man_l.append(i)

                    # Get url from anchor tag
                    if fin_tag.name == 'a':
                        bs_url = fin_tag.get('href')

                    # Get url from child anchor tag
                    else:
                        bs_url = fin_tag.find('a').get('href')

                    # Convert relative paths to absolute
                    abspath = urllib.parse.urljoin(domain, bs_url)

                    # Add to queue
                    add_to_queue_b = True
                    proceed_f(abspath, working_list, checkedurls_man_list, skipped_pages, current_crawl_level, all_urls_q, total_count, add_to_queue_b)




            # Catch all other errors
            except Exception as errex:
                print(os.getpid(), os.getpid(), '---- Unknown error detected. Skipping...', str(traceback.format_exc()), workingurl)
                add_errorurls_f(workingurl, 'jj_error 1', str(errex), current_crawl_level, jbw_type, portalurl, errorurls_man_dict)
                prev_item = errorurls_man_dict[workingurl]
                prev_item.append('jj_final_error')
                conf_val = 'jj_error 1'
                outcome(checkedurls_man_list, workingurl, conf_val)
                continue


            # Declare the task has finished
            finally:
                prog_count.value += 1





# Multiprocessing
if __name__ == '__main__':

    all_list = [

['City of Albany', 'https://jobs.albanyny.gov/jobopps', 'http://www.albanyny.org', (42.6573000189, -73.7464300179)],
['City of Amsterdam', '', 'http://www.amsterdamny.gov/', (42.9387508724, -74.1884322486)],
['City of Auburn', 'http://www.auburnny.gov/public_documents/auburnny_civilservice/index', 'http://www.auburnny.gov', (42.9173899379, -76.5582099703)],
['City of Batavia', 'http://www.batavianewyork.com/fire-department/pages/employment', 'http://www.batavianewyork.com', (42.9969599591, -78.2176699417)],
['City of Beacon', 'http://www.cityofbeacon.org/index.php/employment-opportunities/', 'http://www.cityofbeacon.org', (41.4929950346, -73.9591150045)],
['City of Binghamton', '', 'http://www.cityofbinghamton.com', (42.096111616, -75.9118477851)],
['County of Bronx', '', '', (40.8261051448, -73.9233181992)],
['County of Kings', '', '', (40.6938822504, -73.9892071663)],
['City of Buffalo', 'https://www.buffalony.gov/jobs.aspx', 'http://www.city-buffalo.com', (42.8817749713, -78.8815099994)],
['City of Canandaigua', 'http://www.canandaiguanewyork.gov/index.asp?SEC=90DF6C01-C88B-48D6-9985-A3703944D7D3&Type=B_BASIC', 'http://www.canandaiguanewyork.gov', (42.8455649254, -77.3076599588)],
['City of Cohoes', 'http://www.cohoes.com', 'http://www.cohoes.com', (42.7746069035, -73.6996130879)],
['City of Corning', 'http://www.cityofcorning.com/employment', 'http://www.cityofcorning.com', (42.1302750887, -77.0356949537)],
['City of Cortland', '', 'http://www.cortland.org/', (42.5990905595, -76.1783437374)],
['City of Dunkirk', 'http://www.dunkirktoday.com/city-offices/personnel', 'http://www.dunkirktoday.com/', (42.4811850595, -79.3101899642)],
['City of Elmira', 'http://www.cityofelmira.net/personnel', 'http://cityofelmira.net', (42.0915386753, -76.8030461605)],
['City of Fulton', '', 'http://www.cityoffulton.com', (43.3208530475, -76.4154790307)],
['City of Geneva', '', 'http://visitgenevany.com', (42.8676953111, -76.9826892272)],
['City of Glen Cove', 'http://www.cityofglencoveny.org/', 'http://www.glencove-li.com/', (40.8641440348, -73.6314768796)],
['City of Glens Falls', 'http://www.cityofglensfalls.com/index.aspx?nid=55', 'http://www.cityofglensfalls.com', (43.3108212205, -73.6442385422)],
['City of Gloversville', 'http://www.cityofgloversville.com/government/employment/', 'http://www.cityofgloversville.com', (43.0511472971, -74.348809909)],
['City of Hornell', '', 'http://www.cityofhornell.com', (42.3277498303, -77.6614328321)],
['City of Hudson', '', 'http://www.cityofhudson.org', (42.2492858918, -73.785717693)],
['City of Ithaca', '', 'http://www.ci.ithaca.ny.us/', (42.4388861499, -76.4984806831)],
['City of Jamestown', 'http://www.jamestownny.net/employment-opportunities/', 'http://www.jamestownny.net', (42.0963517584, -79.238406786)],
['City of Johnstown', '', 'http://www.cityofjohnstown-ny.com', (43.007121272, -74.3700183349)],
['City of Kingston', 'http://kingston-ny.gov/employment', 'http://www.kingston-ny.gov', (41.927146491, -73.9961675891)],
['City of Lackawanna', 'http://www.lackawannany.gov/departments/civil-service', 'http://www.lackawannany.gov/', (42.8258990287, -78.8248276162)],
['City of Little Falls', '', 'http://cityoflittlefalls.net/', (43.0445112722, -74.8555181491)],
['City of Lockport', '', 'http://elockport.com/city-index.php', (43.1695629342, -78.695646266)],
['City of Long Beach', 'http://www.longbeachny.org/index.asp?type=b_basic&amp;sec={9c88689c-135f-4293-a9ce-7a50346bea23}', 'http://www.longbeachny.org', (40.5900218115, -73.6656186719)],
['County of New York', '', '', (40.7137100168, -74.0084949972)],
['City of Mechanicville', '', 'http://www.mechanicvilleny.gov', (42.9036815273, -73.6852842975)],
['City of Middletown', 'http://www.middletown-ny.com/departments/civil-service.html?_sm_au_=ivvrlpv4fvqpnjqj', 'http://www.middletown-ny.com', (41.4458479641, -74.4213628065)],
['City of Mount Vernon', 'http://cmvny.com/departments/civil-service/job-postings/', 'http://www.cmvny.com', (40.9117545133, -73.8392403148)],
['City of Newburgh', 'http://www.cityofnewburgh-ny.gov/civil-service', 'http://www.CityofNewburgh-ny.gov', (41.4996853241, -74.0100472883)],
['City of New Rochelle', 'http://www.newrochelleny.com/index.aspx?nid=362', 'http://newrochelleny.com/', (40.9200100003, -73.7861600252)],
['City of New York City', '', 'http://www.nyc.gov', (0.0, 0.0)],
['City of Niagara Falls', 'http://niagarafallsusa.org/government/city-departments/human-resources-department', 'http://www.niagarafallsusa.org', (43.0958918917, -79.0551239216)],
['City of North Tonawanda', '', 'http://www.northtonawanda.org/', (43.029631249, -78.8698685116)],
['City of Norwich', 'http://www.norwichnewyork.net/human_resources.html', 'http://www.norwichnewyork.net', (42.5472650104, -75.5339550684)],
['City of Ogdensburg', 'http://www.ogdensburg.org/index.aspx?nid=97', 'http://www.ogdensburg.org', (44.6983160149, -75.4920106633)],
['City of Olean', 'http://www.cityofolean.org/jobs.html', 'http://www.cityofolean.org/', (42.0701950675, -78.4165549339)],
['City of Oneida', 'http://oneidacity.com/civil-servic', 'http://www.oneidacity.com/', (43.0964362165, -75.6532163874)],
['City of Oneonta', 'http://www.oneonta.ny.us/departments/personnel', 'http://www.oneonta.ny.us', (42.4550014772, -75.0601782007)],
['City of Oswego', 'http://www.oswegony.org/government/personnel', 'http://www.oswegony.org', (43.4554020797, -76.511214423)],
['City of Peekskill', 'http://www.cityofpeekskill.com/human-resources/pages/about-human-resources', 'http://www.cityofpeekskill.com', (41.2916486594, -73.9224745274)],
['City of Plattsburgh', '', 'http://www.cityofplattsburgh.com', (44.6922362704, -73.4544196285)],
['City of Port Jervis', 'https://www.portjervisny.org/city-resources/job-project-postings/', 'http://www.portjervisny.org', (41.3750386924, -74.6909888012)],
['City of Poughkeepsie', 'http://cityofpoughkeepsie.com/personnel', 'http://www.cityofpoughkeepsie.com', (41.7070900861, -73.9280500496)],
['County of Queens', '', '', (40.7047341302, -73.8091406243)],
['City of Rensselaer', 'https://rensselaerny.gov/police-department/employment', 'http://www.rensselaerny.gov', (42.6386513986, -73.7450785548)],
['City of Rochester', 'http://www.cityofrochester.gov/article.aspx?id=8589936759', 'http://www.cityofrochester.gov/', (43.1570755002, -77.6150790944)],
['City of Rome', 'https://romenewyork.com/civil-service', 'http://www.romenewyork.com', (43.2121413109, -75.4587679929)],
['City of Rye', 'http://www.ryeny.gov', 'http://www.ryeny.gov', (40.9811187479, -73.6842288189)],
['City of Salamanca', '', 'http://www.salmun.com', (42.1568122724, -78.7074083921)],
['City of Saratoga Springs', 'http://www.saratoga-springs.org/jobs.aspx', 'http://www.saratoga-springs.org', (43.0833372744, -73.7840689417)],
['City of Schenectady', 'http://www.cityofschenectady.com/208/human-resources', 'http://www.cityofschenectady.com', (42.8159999546, -73.9424600046)],
['City of Sherrill', '', 'http://www.sherrillny.org', (43.0690666949, -75.6018829703)],
['County of Richmond', '', '', (40.6430332331, -74.0771124146)],
['City of Syracuse', '', 'http://www.syrgov.net/', (43.0499913768, -76.1490777002)],
['City of Tonawanda', '', 'http://www.ci.tonawanda.ny.us/', (43.0197513973, -78.8869886541)],
['City of Troy', 'http://www.troyny.gov/departments/personnel-department', 'http://www.troyny.gov', (42.7371713848, -73.6873786047)],
['City of Utica', 'http://www.cityofutica.com/departments/civil-service/index', 'http://www.cityofutica.com', (43.1017328064, -75.2363561071)],
['City of Watertown', 'https://www.watertown-ny.gov/index.asp?nid=791', 'http://www.watertown-ny.gov/', (43.9725894821, -75.9100070734)],
['City of Watervliet', 'http://watervliet.com/city/civil-service.htm', 'http://www.watervliet.com', (42.7257595931, -73.6999508073)],
['City of White Plains', 'https://www.cityofwhiteplains.com/98/Personnel', 'http://www.cityofwhiteplains.com', (41.0333599116, -73.7655056043)],
['City of Yonkers', 'http://www.yonkersny.gov/work/jobs-civil-service-exams', 'http://www.yonkersny.gov', (40.9317428094, -73.8972508174)],
['Town of Berne', '', 'http://berneny.org', (42.6211800914, -74.2250550942)],
['Town of Bethlehem', 'http://www.townofbethlehem.org/137/human-resources?_sm_au_=ivv8z8lp1wffsnv6', 'http://www.townofbethlehem.org', (42.6202071962, -73.8396694786)],
['Village of Ravena', '', 'http://www.villageofRavena.com', (42.4730475749, -73.8148364099)],
['Town of Coeymans', '', 'http://www.coeymans.org', (42.4693388844, -73.8091313941)],
['Village of Colonie', '', 'http://www.colonievillage.org', (42.7209845616, -73.8323003383)],
['Village of Menands', '', 'http://www.villageofmenands.com', (42.6932700928, -73.7236974306)],
['Town of Colonie', 'https://www.colonie.org/departments/civilservice', 'http://www.colonie.org', (42.7194463695, -73.7560201183)],
['Village of Green Island', 'http://www.villageofgreenisland.com/employment/', 'http://www.villageofgreenisland.com/village/', (42.7420715022, -73.692098092)],
['Town of Green Island', '', 'http://www.villageofgreenisland.com/town/', (42.741554656, -73.6910802677)],
['Village of Altamont', '', 'http://www.altamontvillage.org/', (42.7030407847, -74.0247829213)],
['Town of Knox', '', 'http://www.knoxny.org', (42.6699854459, -74.1189933789)],
['Village of Voorheesville', '', 'http://www.villageofvoorheesville.com/', (42.6517985725, -73.9282599671)],
['Town of New Scotland', '', 'http://www.townofnewscotland.com', (42.6313429755, -73.9078152892)],
['Town of Rensselaerville', '', 'http://www.rensselaerville.com', (42.4568758048, -74.1369822302)],
['Town of Westerlo', '', 'http://townofwesterlony.com', (42.5098452965, -74.0463150929)],
['County of Albany', 'http://www.albanycounty.com/civilservice', 'http://www.albanycounty.com', (42.6500423313, -73.7542171363)],
['Village of Alfred', '', 'http://www.alfredny.org', (42.2537259067, -77.7912654453)],
['Town of Alfred', '', 'http://www.townofalfred.com/', (42.2534100076, -77.7674649392)],
['Town of Allen', '', 'http://www.alleganyco.com/local_govt/Allen/', (42.3494299997, -77.987814909)],
['Town of Alma', '', 'http://www.townofalma.org', (42.0844100067, -78.0641449635)],
['Village of Almond', 'http://www.alleganyco.com/departments/human-resources-civil-service/', 'http://www.alleganyco.com/local_govt/villages/Almond/', (42.3107450281, -77.8451049549)],
['Town of Almond', '', 'http://www.almondny.us', (42.3167121717, -77.7412362542)],
['Village of Belmont', '', 'http://www.belmontny.org/', (42.2229763901, -78.0344413242)],
['Town of Amity', '', 'http://www.townofamity-ny.com', (42.22322186, -78.0345899342)],
['Village of Andover', '', 'http://www.alleganyco.com/local_govt/villages/Andover/', (42.1529200271, -77.8014599238)],
['Town of Andover', '', 'http://www.alleganyco.com/local_govt/Andover/', (42.157626977, -77.7952459146)],
['Village of Angelica', '', 'http://www.angelicany.com/', (42.3066039785, -78.0157489249)],
['Town of Angelica', '', 'http://www.alleganyco.com/local_govt/Angelica/', (42.3494299997, -77.987814909)],
['Town of Belfast', 'https://www.alleganyco.com/departments/employment-and-training/', 'http://www.alleganyco.com/local_govt/Belfast/', (42.3440569704, -78.1136709551)],
['Town of Birdsall', '', 'http://www.alleganyco.com/local_govt/Birdsall/', (42.4169000308, -77.8567649246)],
['Village of Bolivar', '', 'http://www.alleganyco.com/local_govt/villages/Bolivar/', (42.0541500429, -78.1058649788)],
['Village of Richburg', '', 'http://www.alleganyco.com/local_govt/villages/Richburg/', (42.0885000223, -78.1528299965)],
['Town of Bolivar', '', 'http://www.townofbolivar.com', (42.0678309988, -78.1673581523)],
['Village of Canaseraga', '', 'http://www.alleganyco.com/local_govt/villages/Canseraga/', (42.4605070836, -77.7839228939)],
['Town of Burns', '', 'http://www.townofburnsny.com', (42.4169000308, -77.8567649246)],
['Town of Caneadea', 'https://towncaneadea.digitaltowpath.org:10139/content/JobCategories', 'http://townofcaneadea.org/', (42.3878185214, -78.1534238663)],
['Town of Centerville', '', 'http://centerville.wordpress.com/', (42.4797900838, -78.2497449156)],
['Town of Clarksville', '', 'http://www.alleganyco.com/local_govt/Clarksville/', (42.2709550195, -78.3352249491)],
['Village of Cuba', '', 'http://www.cubany.org/html/vofficials.html', (42.2709550195, -78.3352249491)],
['Town of Cuba', '', 'http://www.cubany.org/', (42.2709550195, -78.3352249491)],
['Town of Friendship', '', 'http://www.townoffriendship-ny.com/', (42.1914700176, -78.1464299168)],
['Town of Genesee', '', 'http://www.alleganyco.com/local_govt/Genesee/', (41.999889095, -78.2663889579)],
['Town of Granger', '', 'http://www.grangerny.org/', (42.5241450893, -78.1724199194)],
['Town of Grove', '', 'http://townofgrove.com/', (42.4891666171, -77.9510257746)],
['Town of Hume', '', 'http://www.humetown.org', (42.4663161199, -78.1118385647)],
['Town of Independence', '', 'http://independenceny.org', (42.0365899209, -77.7682863267)],
['Town of New Hudson', '', 'http://www.newhudsonny.org', (42.2859900341, -78.2533949147)],
['Town of Rushford', '', 'http://www.rushfordny.org', (42.3839600177, -78.2481499118)],
['Town of Scio', '', 'http://townofsciony.org/', (42.1556350441, -78.0261149249)],
['Town of Ward', '', 'http://www.alleganyco.com/local_govt/Ward/', (42.2460150903, -77.9812799385)],
['Village of Wellsville', 'http://wellsvilleny.com/html/humanresources.html', 'http://wellsvilleny.com', (42.1223672121, -77.9487899052)],
['Town of Wellsville', '', 'http://townofwellsvilleny.org', (42.1187388795, -77.9512214399)],
['Town of West Almond', '', 'http://www.alleganyco.com/local_govt/WAlmond/', (42.3107450281, -77.8451049549)],
['Town of Willing', '', 'http://willingny.org', (42.0575165342, -77.9161613671)],
['Town of Wirt', '', 'http://www.alleganyco.com/local_govt/Wirt/', (42.1914700176, -78.1464299168)],
['County of Allegany', 'http://www.alleganyco.com/departments/human-resources-civil-service', 'http://www.alleganyco.com', (42.2460150903, -77.9812799385)],
['Town of Barker', '', 'http://www.gobroomecounty.com/files/community/pdfs/TownofBarker.pdf', (42.2531900918, -75.9071249281)],
['Town of Binghamton', '', 'http://www.townofbinghamton.com', (42.0686416183, -75.9110877708)],
['Town of Chenango', 'http://townofchenango.com/?page_id=12', 'http://www.townofchenango.com/', (42.1744271365, -75.8861303927)],
['Town of Colesville', '', 'http://townofcolesville.org/', (42.2646950057, -75.673000038)],
['Town of Conklin', '', 'http://www.townofconklin.org', (42.0331000009, -75.8186400293)],
['Village of Port Dickinson', '', 'http://www.portdickinsonny.us/', (42.1383415793, -75.8951578505)],
['Town of Dickinson', '', 'http://www.townofdickinson.com', (42.1192815531, -75.9109978392)],
['Town of Fenton', '', 'http://www.townoffenton.com', (42.1985900785, -75.7638950331)],
['Town of Kirkwood', '', 'http://www.townofkirkwood.org', (42.0904780165, -75.823344977)],
['Village of Lisle', '', '', (42.3332200204, -76.0438549349)],
['Town of Lisle', '', 'http://www.gobroomecounty.com/community/municipalities/lisle', (42.3332200204, -76.0438549349)],
['Town of Maine', '', 'http://townofmaine.org/', (42.2364600713, -76.0557149238)],
['Town of Nanticoke', '', 'http://townofnanticokeny.com', (42.2364600713, -76.0557149238)],
['Village of Deposit', '', 'http://www.villageofdeposit.org/', (42.0604616119, -75.4256780975)],
['Town of Sanford', '', '', (42.0604616119, -75.4256780975)],
['Village of Whitney Point', '', 'http://www.whitneypoint.org', (42.3355450776, -75.9413549145)],
['Town of Triangle', '', 'http://www.gobroomecounty.com/files/legis/County%20Guides/TOWN%20OF%20TRIANGLE.pdf', (42.3290650823, -75.9656850214)],
['Village of Endicott', 'https://endicottny.com/departments/employment/', 'http://www.endicottny.com', (42.0977455903, -76.0502180091)],
['Village of Johnson City', '', 'http://www.villageofjc.com/', (42.1153868841, -75.9552031604)],
['Town of Union', 'http://www.townofunion.com', 'http://www.townofunion.com', (42.1063786671, -76.0262464043)],
['Town of Vestal', 'http://www.vestalny.com/departments/human_resources/job_opportunities.php', 'http://www.vestalny.com/', (42.0826216281, -76.0652077881)],
['Village of Windsor', '', '', (42.0579599995, -75.5658100352)],
['Town of Windsor', '', 'http://www.windsorny.org', (42.0779615648, -75.6394680088)],
['County of Broome', 'http://www.gobroomecounty.com/personnel/cs', 'http://www.gobroomecounty.com', (42.0965522359, -75.910754661)],
['Village of Allegany', '', 'http://www.allegany.org/index.php?Village%20of%20Allegany', (42.0866911608, -78.4897490579)],
['Town of Allegany', '', 'http://www.allegany.org/index.php?Town%20of%20Allegany', (42.0912623873, -78.4956287121)],
['Town of Ashford', '', 'http://ashfordny.org', (42.4214000838, -78.6416749168)],
['Town of Carrollton', '', 'http://www.carrolltonny.org/index.htm', (42.0491000722, -78.6465699268)],
['Town of Coldspring', '', 'http://www.cold-springny.org/', (42.1103805301, -78.9037920001)],
['Town of Conewango', '', '', (42.1486850452, -78.9442349873)],
['Village of South Dayton', '', '', (42.3605150822, -79.0837199675)],
['Town of Dayton', '', 'http://daytonny.org', (42.3975141603, -79.0011372859)],
['Town of East Otto', '', 'http://www.eastottony.org/', (42.3910997966, -78.754543364)],
['Village of Ellicottville', '', 'http://www.ellicottvillegov.com', (42.2753569189, -78.6732948711)],
['Town of Ellicottville', '', 'http://www.ellicottvillegov.com', (42.2753569189, -78.6732948711)],
['Town of Farmersville', '', 'http://farmersvilleny.org', (42.3863171837, -78.3774224167)],
['Village of Franklinville', '', 'http://franklinvilleny.org', (42.3322479936, -78.461222759)],
['Town of Franklinville', '', 'http://franklinvilleny.org', (42.3336850136, -78.4333549939)],
['Town of Freedom', '', 'http://www.freedomny.org', (42.4980672618, -78.3705102901)],
['Town of Great Valley', '', 'http://www.greatvalleyny.org', (42.1943500062, -78.6579789542)],
['Town of Hinsdale', '', 'http://hinsdaleny.org', (42.2538621085, -78.4154698957)],
['Town of Humphrey', '', 'http://humphreytownship.com', (42.2132550189, -78.595034911)],
['Town of Ischua', '', '', (42.2054550602, -78.4066399194)],
['Town of Leon', '', 'http://www.leonny.org', (42.2223850153, -79.0717098986)],
['Village of Little Valley', '', 'http://www.villageoflittlevalley.org/', (42.2488904361, -78.7988972638)],
['Town of Little Valley', '', 'http://www.littlevalleyny.org/', (42.2495188986, -78.7963717379)],
['Town of Lyndon', '', 'http://lyndontown.org', (42.305111125, -78.3494486226)],
['Town of Machias', '', 'http://www.machiasny.org/', (42.4189658219, -78.4951916735)],
['Town of Mansfield', '', 'http://mansfieldny.org', (42.2360400371, -78.8135349038)],
['Town of Napoli', '', 'http://www.napoliny.org/', (42.2030549332, -78.8914773577)],
['Village of Cattaraugus', '', 'http://www.cattaraugusny.org/html/vgov.html', (42.330066068, -78.8686291691)],
['Town of New Albion', '', 'http://www.cattaraugusny.org/html/tgove.html', (42.330066068, -78.8686291691)],
['Town of Olean', '', '', (42.0627022203, -78.4423418414)],
['Town of Otto', '', 'http://www.ottony.org/', (42.4353880298, -78.8376479306)],
['Town of Perrysburg', '', 'http://www.perrysburgny.org/', (42.45648108, -79.00406993)],
['Village of Gowanda', '', 'http://www.villageofgowanda.com', (42.4634697488, -78.9343601051)],
['Town of Persia', '', 'http://www.persiany.org/', (42.4627883432, -78.9356114561)],
['Village of Portville', '', 'http://www.portvilleny.net/', (42.0385176769, -78.3401795447)],
['Town of Portville', '', 'http://www.portville-ny.org', (42.0415100242, -78.3313999027)],
['Town of Randolph', '', 'http://randolphny.net/', (42.1627566482, -78.973160715)],
['Town of Red House', '', '', (42.0535950252, -78.8093599693)],
['Town of Salamanca', '', 'http://townofsalamanca.org', (42.0535950252, -78.8093599693)],
['Town of South Valley', '', 'http://southvalleyny.org', (42.032853544, -78.9946116554)],
['Village of Delevan', '', '', (42.4300180233, -78.4843919237)],
['Town of Yorkshire', '', 'http://yorkshireny.org', (42.5271512307, -78.4699741233)],
['County of Cattaraugus', 'http://www.cattco.org/jobs', 'http://www.cattco.org', (42.2521553173, -78.8005762825)],
['Village of Cayuga', 'https://mycivilservice.cayugacounty.us/exams', 'http://www.cayugacounty.us/towns/A-G/VillageofCayuga.aspx', (42.9178123288, -76.7298148094)],
['Town of Aurelius', '', 'http://www.cayugacounty.us/portals/1/Aurelius/', (42.9173899379, -76.5582099703)],
['Village of Weedsport', '', 'http://villageofweedsport.org/', (43.0479236644, -76.5612696579)],
['Town of Brutus', 'https://townbrutus.digitaltowpath.org:10148/content/JobCategories', 'http://townofbrutus.org/', (43.0543711922, -76.5591678415)],
['Village of Cato', '', 'http://www.villageofcatony.com/', (43.1830999263, -76.5682399762)],
['Village of Meridian', '', '', (43.1664523476, -76.5411349915)],
['Town of Cato', '', 'http://www.cayugacounty.us/portals/1/Townofcato', (43.157537901, -76.5470230161)],
['Town of Conquest', '', 'http://www.cayugacounty.us/portals/1/conquest', (43.058139911, -76.6582449516)],
['Town of Fleming', '', 'http://www.cayugacounty.us/portals/1/fleming', (42.861587053, -76.5787164409)],
['Town of Genoa', '', 'http://www.cayugacounty.us/portals/1/genoa', (42.6769843437, -76.5875818602)],
['Town of Ira', '', 'http://www.cayugacounty.us/portals/1/ira', (43.1830999263, -76.5682399762)],
['Village of Aurora', '', 'http://www.auroranewyork.us/', (42.7580387155, -76.7032500194)],
['Town of Ledyard', '', 'http://www.cayugacounty.us/towns/H-P/Ledyard.aspx', (42.7356632048, -76.6668674628)],
['Town of Locke', '', 'http://www.cayugacounty.us/portals/1/locke', (42.6172200655, -76.4924449414)],
['Village of Port Byron', '', '', (43.0350670149, -76.6232129574)],
['Town of Mentz', '', 'http://www.townofmentz.com/', (43.058139911, -76.6582449516)],
['Town of Montezuma', '', 'http://www.cayugacounty.us/portals/1/montezuma/', (43.0103919408, -76.7013727203)],
['Village of Moravia', '', 'http://www.cayugacounty.us/portals/1//villageofmoravia', (42.7519949842, -76.3924849035)],
['Town of Moravia', '', 'http://www.cayugacounty.us/towns/H-P/TownofMoravia.aspx', (42.7519949842, -76.3924849035)],
['Town of Niles', '', 'http://www.cayugacounty.us/portals/1/niles', (42.7982349588, -76.3496888077)],
['Town of Owasco', '', 'http://www.cayugacounty.us/towns/H-P/Owasco.aspx', (42.9183585504, -76.5450114511)],
['Town of Scipio', '', 'http://www.cayugacounty.us/portals/1/scipio', (42.7834287413, -76.5578285915)],
['Town of Sempronius', '', 'http://www.cayugacounty.us/portals/1/sempronius', (42.7519949842, -76.3924849035)],
['Town of Sennett', '', 'http://www.cayugacounty.us/portals/1/sennett', (42.9173899379, -76.5582099703)],
['Village of Union Springs', '', 'http://unionspringsny.com/', (42.8426355443, -76.6966262298)],
['Town of Springport', '', 'http://www.cayugacounty.us/portals/1/springport', (42.8590378096, -76.6821271759)],
['Village of Fair Haven', '', 'http://www.cayugacounty.us/portals/1/fairhaven', (43.3162849352, -76.7046749342)],
['Town of Sterling', '', 'http://www.cayugacounty.us/portals/1/sterling', (43.3235037372, -76.6471275581)],
['Town of Summerhill', '', 'http://www.cayugacounty.us/portals/1/summerhill', (42.6431432985, -76.343528268)],
['Town of Throop', '', 'http://www.cayugacounty.us/portals/1/throop', (42.9956849064, -76.6774568853)],
['Town of Venice', '', 'http://www.cayugacounty.us/portals/1/venice/', (42.7464800152, -76.6759099624)],
['Town of Victory', '', 'http://www.cayugacounty.us/portals/1/townofvictory/', (43.2494549386, -76.7366299155)],
['County of Cayuga', 'http://www.cayugacounty.us/community/civilservicecommission/examannouncementsvacancies.aspx', 'http://www.cayugacounty.us/', (42.9296365304, -76.5697542093)],
['Town of Arkwright', '', 'http://www.arkwrightny.org', (42.3926916755, -79.2357567333)],
['Village of Lakewood', '', 'http://www.lakewoodny.com', (42.1036416945, -79.3284567676)],
['Town of Busti', '', 'http://www.townofbusti.com', (42.10206311, -79.3256404693)],
['Town of Carroll', '', 'http://carrollny.org/', (42.0529141909, -79.1599119511)],
['Village of Sinclairville', '', '', (42.263671665, -79.2588367032)],
['Town of Charlotte', '', 'http://www.charlotteny.org/', (42.263009019, -79.2583801208)],
['Village of Mayville', '', 'http://www.villageofmayville.com/', (42.2374150269, -79.5003899753)],
['Town of Chautauqua', '', 'http://www.townofchautauqua.com/', (42.2536116964, -79.5047366211)],
['Village of Cherry Creek', '', '', (42.3091400317, -79.1395299292)],
['Town of Cherry Creek', '', 'http://cherrycreekny.org/', (42.3091400317, -79.1395299292)],
['Town of Clymer', '', 'http://www.townofclymer.org/', (42.0208140612, -79.6278259288)],
['Town of Dunkirk', '', 'http://www.dunkirkny.org/', (42.4641042489, -79.3683189189)],
['Village of Bemus Point', '', 'http://www.bemuspointny.org/', (42.157798107, -79.3934899864)],
['Town of Ellery', '', 'http://www.elleryny.org', (42.159260957, -79.3907878507)],
['Village of Celoron', '', 'http://celoronny.org/', (42.1098600859, -79.2819999891)],
['Village of Falconer', '', 'http://falconerny.org/', (42.11741174, -79.1992667464)],
['Town of Ellicott', 'http://www.townofellicott.com/html/jobs.html', 'http://www.townofellicott.com', (42.1163817232, -79.1924267821)],
['Town of Ellington', '', 'http://ellingtonny.org', (42.2169500752, -79.1077749786)],
['Town of French Creek', '', 'http://frenchcreekny.org', (42.0516000768, -79.6695299528)],
['Town of Gerry', '', 'http://gerryny.us/', (42.2272750209, -79.1734199104)],
['Village of Forestville', '', '', (42.4711016351, -79.1801467718)],
['Village of Silver Creek', '', 'http://www.silvercreekny.com/', (42.5456716108, -79.1694566975)],
['Town of Hanover', '', 'http://www.townofhanover.org', (42.5239200857, -79.1708899292)],
['Village of Panama', '', 'http://www.panamany.org/', (42.0750052239, -79.4805407269)],
['Town of Harmony', '', 'http://thetownofharmony.com', (42.0438176931, -79.4125474131)],
['Town of Kiantone', '', 'http://kiantoneny.org', (42.0639317596, -79.2060667857)],
['Town of Turin', '', '', (43.6275423897, -75.4098533951)],
['Town of Mina', '', 'http://www.townofmina.info/', (42.1245950703, -79.7401149527)],
['Town of North Harmony', '', 'http://www.townofnorthharmony.com', (42.1550150911, -79.406039923)],
['Town of Poland', '', 'http://www.polandny.org/', (42.1582217389, -79.1014368089)],
['Village of Fredonia', '', '', (42.4138950659, -79.3277049103)],
['Town of Pomfret', '', 'http://www.townofpomfretny.com/', (42.4408616576, -79.3313166939)],
['Village of Brocton', '', 'http://www.villageofbrocton.com/', (42.3972730962, -79.4521148693)],
['Town of Portland', '', 'http://www.town.portland.ny.us/', (42.382120035, -79.4334249001)],
['Town of Ripley', '', 'http://www.ripley-ny.com/', (42.2285750799, -79.6962149495)],
['Town of Sheridan', '', '', (42.4879350443, -79.2371199445)],
['Village of Sherman', '', '', (42.1567863239, -79.5972793356)],
['Town of Sherman', '', '', (42.1598450514, -79.6002499052)],
['Village of Cassadaga', '', 'http://www.cassadaganewyork.org/', (42.3425300248, -79.3111541755)],
['Town of Stockton', '', '', (42.3454716652, -79.3082567058)],
['Town of Villenova', '', '', (42.3751560759, -79.1262230217)],
['Village of Westfield', '', 'http://www.villageofwestfield.org/', (42.3222016965, -79.5760065773)],
['Town of Westfield', '', 'http://www.townofwestfield.org', (42.3222016965, -79.5760065773)],
['County of Chautauqua', 'http://www.co.chautauqua.ny.us/314/human-resources', 'http://www.co.chautauqua.ny.us', (42.2542873629, -79.505121387)],
['Village of Wellsburg', '', 'http://villageofwellsburg.com/blog/', (42.0115259327, -76.7287556661)],
['Town of Ashland', '', 'http://www.townofashland.net', (42.0220900548, -76.7656799332)],
['Town of Baldwin', 'https://www.chemungcountyny.gov/departments/a_-_f_departments/civil_service_personnel/job_opening_calendar.php', 'http://www.chemungcounty.com/index.asp?pageId=231', (42.0900150877, -76.692244932)],
['Town of Big Flats', '', 'http://www.bigflatsny.gov', (42.1410521878, -76.9350312079)],
['Town of Catlin', '', 'http://townofcatlin.com', (42.2526830657, -77.0340368918)],
['Town of Chemung', '', 'http://www.townofchemung.com', (42.0723193921, -76.5773407709)],
['Village of Elmira Heights', '', 'http://www.elmiraheights.org/', (42.1278013373, -76.8221350781)],
['Town of Elmira', '', 'http://www.townofelmira.com', (42.0778886082, -76.8443424656)],
['Town of Erin', '', 'http://townoferin.org', (42.1789459081, -76.692547363)],
['Village of Horseheads', '', 'http://horseheads.org/', (42.1666852708, -76.8205623367)],
['Town of Horseheads', '', 'http://www.townofhorseheads.org', (42.189701836, -76.8247573485)],
['Town of Southport', '', 'http://townofsouthport.com/', (42.0554070686, -76.8184223825)],
['Village of Van Etten', '', '', (42.2526600623, -76.6294349116)],
['Town of Van Etten', '', 'http://www.chemungcounty.com/index.asp?pageId=242', (42.2526600623, -76.6294349116)],
['Village of Millport', '', 'http://vlgmillport-ny.webs.com/', (42.2640133848, -76.8341197242)],
['Town of Veteran', '', '', (42.252195001, -76.8265438763)],
['County of Chemung', 'http://www.chemungcountyny.gov/departments/a_-_f_departments/civil_service_personnel/index.php', 'http://www.chemungcounty.com', (42.090074049, -76.8020720024)],
['Village of Afton', '', '', (42.2248651946, -75.5283303376)],
['Town of Afton', '', 'http://townofafton.com', (42.2403750327, -75.5434350608)],
['Village of Bainbridge', '', 'http://bainbridgeny.org/', (42.2940429101, -75.4786615592)],
['Town of Bainbridge', '', 'http://bainbridgeny.org', (42.2940429101, -75.4786615592)],
['Town of Columbus', '', 'http://www.columbusny.us/', (42.6828800835, -75.4590800354)],
['Town of Coventry', '', 'http://townofcoventryny.com/', (42.3105728597, -75.6385938941)],
['Town of German', '', '', (42.5068100881, -75.7730950625)],
['Village of Greene', '', 'http://www.nygreene.com/villageofgreene.htm', (42.3784250739, -75.868599911)],
['Town of Greene', '', 'http://www.nygreene.com/', (42.3297871951, -75.7709636724)],
['Town of Guilford', 'https://www.guilfordny.com/government/help_wanted', 'http://www.guilfordny.com/', (42.4020415061, -75.4531280101)],
['Town of Lincklaen', '', '', (42.6594150689, -75.7700200595)],
['Town of McDonough', '', 'http://mcdonoughny.com', (42.5068100881, -75.7730950625)],
['Village of New Berlin', '', 'http://thevillageofnewberlin.org/', (42.6022050317, -75.3575400824)],
['Town of New Berlin', '', 'http://www.townofnewberlin.org', (42.6237311531, -75.3323014041)],
['Town of North Norwich', '', '', (42.6166150947, -75.5270900909)],
['Town of Norwich', '', 'http://www.townofnorwich.homestead.com', (42.5205477763, -75.5106178428)],
['Town of Otselic', '', '', (42.6475115011, -75.7846578611)],
['Village of Oxford', '', 'http://www.oxfordny.com/government/village/index.php', (42.440460069, -75.6294900965)],
['Town of Oxford', 'http://www.townofoxfordny.com/employment.php', 'http://www.townofoxfordny.com', (42.440460069, -75.6294900965)],
['Town of Pharsalia', '', '', (42.6181650396, -75.6629850223)],
['Town of Pitcher', '', '', (42.5991500145, -75.8400849184)],
['Town of Plymouth', '', '', (42.5972447348, -75.5923254743)],
['Town of Preston', '', '', (42.5051256423, -75.5973663456)],
['Village of Earlville', '', '', (42.7402425003, -75.5449032275)],
['Village of Sherburne', '', 'http://www.sherburne.org', (42.6782768738, -75.4999970008)],
['Town of Sherburne', '', 'http://www.townofsherburne.net/', (42.6788514318, -75.5001079766)],
['Town of Smithville', 'http://smithvilleny.com/employment.html', 'http://smithvilleny.com', (42.4421050338, -75.8732699219)],
['Village of Smyrna', '', '', (42.6836600063, -75.6225500848)],
['Town of Smyrna', '', '', (42.6836600063, -75.6225500848)],
['County of Chenango', 'http://www.co.chenango.ny.us/personnel/examinations', 'http://www.co.chenango.ny.us', (42.5472650104, -75.5339550684)],
['Town of Altona', '', 'http://www.townofaltonany.com/', (44.8540849847, -73.6535900305)],
['Village of Keeseville', '', 'http://www.co.essex.ny.us/keeseville.asp', (44.5050099083, -73.5240900963)],
['Town of Ausable', '', '', (44.5046206188, -73.4829774354)],
['Town of Beekmantown', '', 'http://townofbeekmantown.com', (44.7750539963, -73.4801651811)],
['Town of Black Brook', '', '', (44.4424876159, -73.6746890752)],
['Village of Champlain', '', 'http://www.vchamplain.com', (44.983472492, -73.445344456)],
['Village of Rouses Point', '', 'http://www.rousesptny.com', (44.9921349273, -73.3720450307)],
['Town of Champlain', '', '', (44.9619199256, -73.439565011)],
['Town of Chazy', '', 'http://www.townofchazy.com', (44.8871625643, -73.4369157927)],
['Town of Clinton', '', 'http://www.townofclinton.com', (44.9558861473, -73.9282292229)],
['Village of Dannemora', '', 'http://www.villageofdannemora.com/', (44.7191156936, -73.7239459385)],
['Town of Dannemora', '', 'http://www.townofdannemora.org', (44.7224699078, -73.7168650456)],
['Town of Ellenburg', '', 'http://www.nnyacgs.com/town_of_ellenburgh.html', (44.8940249646, -73.838045075)],
['Town of Mooers', '', 'http://www.mooersny.com', (44.9596049518, -73.576320087)],
['Town of Peru', '', 'http://www.perutown.com', (44.5821033279, -73.5239635555)],
['Town of Plattsburgh', '', 'http://townofplattsburgh.com', (44.7054116351, -73.5402666892)],
['Town of Saranac', '', 'http://www.townofsaranac.com', (44.6416920204, -73.7496456087)],
['Town of Schuyler Falls', '', 'http://www.schuylerfallsny.com', (44.6904610419, -73.5611959403)],
['County of Clinton', 'http://www.clintoncountygov.com/departments/personnel/personnelhomepage.htm', 'http://www.clintoncountygov.com', (44.6991863371, -73.4539137749)],
['Town of Ancram', '', 'http://www.townofancram.org', (42.0806850715, -73.6552250891)],
['Town of Austerlitz', '', 'http://www.austerlitzny.com', (42.3176250948, -73.4910200906)],
['Town of Canaan', '', 'http://www.canaannewyork.org', (42.4072000406, -73.4253600693)],
['Village of Chatham', '', 'http://www.villageofchatham.com', (42.3636263566, -73.594797144)],
['Town of Chatham', '', 'http://www.chathamnewyork.us/', (42.4790150601, -73.6635050318)],
['Village of Philmont', '', 'http://www.philmont.org/', (42.2494829071, -73.648551709)],
['Town of Claverack', '', 'http://www.townofclaverack.com', (42.2162100289, -73.7086900071)],
['Town of Clermont', '', 'http://www.clermontny.org', (42.0868587674, -73.8252404562)],
['Town of Copake', '', 'http://townofcopake.org/', (42.1113584739, -73.5567071322)],
['Town of Gallatin', 'https://gallatin.yourtownhub.com/category/jobs/', 'http://www.gallatin-ny.org', (42.0867050963, -73.7556200535)],
['Town of Germantown', '', 'http://www.germantownny.org', (42.1219250088, -73.8590800243)],
['Town of Ghent', '', 'http://townofghent.org', (42.2969750046, -73.6406850448)],
['Town of Greenport', '', 'http://www.townofgreenport.com', (42.2562749185, -73.7588276667)],
['Town of Hillsdale', '', 'http://hillsdaleny.com', (42.2110400634, -73.5386400331)],
['Village of Kinderhook', '', 'http://villageofkinderhook.org/', (42.3956527131, -73.697588012)],
['Village of Valatie', '', 'http://www.valatievillage.com/', (42.4134025896, -73.6728977092)],
['Town of Kinderhook', '', 'http://www.kinderhook-ny.gov', (42.4428035992, -73.6635574639)],
['Town of Livingston', '', 'http://livingstontown.com', (42.1422400946, -73.7783600142)],
['Town of New Lebanon', '', 'http://www.townofnewlebanon.com', (42.4784438456, -73.3742657188)],
['Town of Stockport', '', 'http://townofstockport.org', (42.2869671206, -73.7474060922)],
['Town of Stuyvesant', '', 'http://www.stuyvesantny.us/', (42.3895900749, -73.7776022414)],
['Town of Taghkanic', '', 'http://www.taghkanic.org', (42.0867050963, -73.7556200535)],
['County of Columbia', 'https://sites.google.com/a/columbiacountyny.com/civilservice', 'http://www.columbiacountyny.com', (42.2520890389, -73.7869867318)],
['Town of Cincinnatus', '', 'http://www.cortland-co.org/Towns/Cincinnatus.htm', (42.5453970238, -75.9041289393)],
['Village of Homer', 'https://www.homerny.org/government/jobs/', 'http://www.homerny.org', (42.6345615223, -76.1787241408)],
['Village of McGraw', '', 'http://www.cortland-co.org/towns/Mcgrawvillage.htm', (42.6027250772, -76.0640349282)],
['Town of Cortlandville', '', 'http://www.cortlandville.org/', (42.5807410972, -76.2102795201)],
['Town of Cuyler', '', 'http://www.cortland-co.org/towns/Cuyler.htm', (42.7560549193, -75.9280499856)],
['Town of Freetown', '', 'http://www.cortland-co.org/towns/Freetown.htm', (42.5217422356, -76.0364855967)],
['Town of Harford', '', 'http://www.cortland-co.org/towns/Harford.htm', (42.4269005957, -76.2283205081)],
['Town of Homer', '', 'http://www.townofhomer.org/', (42.6360652893, -76.1785501315)],
['Town of Lapeer', '', 'http://www.cortland-co.org/towns/Lapeer.htm', (42.4478050312, -76.0754699027)],
['Village of Marathon', '', 'http://www.cortland-co.org/towns/Marathonvillage.htm', (42.4427382852, -76.0393814303)],
['Town of Marathon', '', 'http://www.cortland-co.org/towns/Marathon.htm', (42.4478050312, -76.0754699027)],
['Town of Preble', '', 'http://www.preble-ny.org', (42.74118403, -76.1459639901)],
['Town of Scott', '', 'http://townofscott.org', (42.7327623547, -76.2443772716)],
['Town of Solon', '', 'http://www.cortland-co.org/towns/Solon.htm', (42.6027250772, -76.0640349282)],
['Town of Taylor', '', 'http://www.cortland-co.org/towns/Taylor.htm', (42.5609550109, -75.9476149203)],
['Town of Truxton', '', 'http://townoftruxton.com/', (42.7106400455, -75.9766349791)],
['Town of Virgil', '', 'http://www.virgilny.com', (42.5086887088, -76.1981164684)],
['Town of Willet', '', 'http://www.cortland-co.org/towns/Willet.htm', (42.5609550109, -75.9476149203)],
['County of Cortland', 'http://www.cortland-co.org/263/personnel-civil%20service', 'http://www.cortland-co.org/', (42.6011975211, -76.1768105767)],
['Town of Andes', '', 'http://townofandes.com', (42.1904416478, -74.7872194641)],
['Town of Bovina', '', 'http://www.bovinany.org', (42.2753150897, -74.7428550162)],
['Town of Colchester', '', 'http://www.colchesterchamber.com/', (42.0591300755, -75.0174800933)],
['Town of Davenport', '', 'http://www.delawarecounty.org/davenport.lasso', (42.4615150111, -74.8824500056)],
['Village of Delhi', '', 'http://www.co.delaware.ny.us/external/villages/delhivillage.htm', (42.3063450843, -74.9248850898)],
['Town of Delhi', '', 'http://townofdelhiny.com/', (42.2721151238, -74.9212571887)],
['Town of Deposit', '', 'http://www.delawarecounty.org/deposit.lasso', (42.0780250056, -75.4633700729)],
['Village of Franklin', '', 'http://www.co.delaware.ny.us/external/villages/franklinvillage.htm', (42.3694350548, -75.1827050963)],
['Town of Franklin', '', 'http://www.townoffranklin.com', (42.3694350548, -75.1827050963)],
['Town of Hamden', '', 'http://www.hamdenny.com', (42.138350008, -74.9731900326)],
['Village of Hancock', '', 'http://www.co.delaware.ny.us/external/villages/hancockvillage.htm', (41.9539545685, -75.2775754579)],
['Town of Hancock', '', 'http://www.hancockny.org', (41.9563795833, -75.2937408259)],
['Village of Stamford', 'https://stamfordny.com/employment-opportunities/', 'http://www.stamfordny.com', (42.4085860437, -74.6170301692)],
['Town of Harpersfield', '', 'http://www.delawarecounty.org/harpersfield.lasso', (42.4429050335, -74.6985700573)],
['Town of Kortright', '', 'http://www.delawarecounty.org/kortright.lasso', (42.3686350596, -74.790680079)],
['Town of Masonville', '', 'http://www.masonville-ny.us/', (42.2500800235, -75.2573850043)],
['Town of Meredith', '', 'http://townofmeredith.com', (42.4236450207, -74.8312650861)],
['Village of Fleischmanns', 'https://www.mtctelcom.com/employment', 'http://www.catskill.net/fleisch', (42.1830300213, -74.5412150382)],
['Village of Margaretville', '', '', (42.1597350485, -74.6665650163)],
['Town of Middletown', '', 'http://middletowndelawarecountyny.org', (42.1391390894, -74.6602740649)],
['Town of Roxbury', '', 'http://www.roxburyny.com', (42.2952000548, -74.5812300495)],
['Village of Sidney', '', '', (42.3164895875, -75.3903805974)],
['Town of Sidney', '', 'http://www.sidneychamber.org/', (42.3221350379, -75.3956900218)],
['Village of Hobart', '', 'http://www.co.delaware.ny.us/external/villages/hobartvillage.htm', (42.3331400882, -74.6459900663)],
['Town of Stamford', '', 'http://townofstamfordny.us/', (42.3686350596, -74.790680079)],
['Town of Tompkins', '', 'http://townoftompkins.org', (42.1644600052, -75.1664750267)],
['Village of Walton', '', 'http://www.villageofwalton.com/', (42.1688318878, -75.128287858)],
['Town of Walton', '', 'http://www.townofwalton.org', (42.1676170573, -75.128930986)],
['County of Delaware', 'http://www.co.delaware.ny.us/departments/pers/jobs.htm', 'http://www.co.delaware.ny.us', (42.2775092032, -74.9160315161)],
['Town of Amenia', '', 'http://www.ameniany.gov', (41.8631900059, -73.5644650848)],
['Town of Beekman', 'http://www.townofbeekman.com/index.asp?Type=B_BASIC&SEC={03E912D9-3F74-4E1F-8BE3-FAB7141BE80F}', 'http://www.townofbeekman.com', (41.6106931389, -73.6804454511)],
['Town of Clinton', '', 'http://www.townofclinton.com', (44.9558861473, -73.9282292229)],
['Town of Dover', 'http://www.TownofDoverNY.us/employmentopportunities.cfm', 'http://www.TownofDoverNY.us', (41.6971665644, -73.5778413253)],
['Town of East Fishkill', 'http://www.eastfishkillny.org/government/employment.htm', 'http://www.eastfishkillny.org', (41.5733857347, -73.8067873589)],
['Village of Fishkill', '', 'http://www.vofishkill.com', (41.5356456714, -73.9028927917)],
['Town of Fishkill', '', 'http://www.fishkill-ny.gov', (41.5261876574, -73.9224022956)],
['Town of Hyde Park', '', 'http://www.hydeparkny.us', (41.7796900263, -73.9204350286)],
['Town of LaGrange', '', 'http://www.lagrangeny.org', (41.6618733165, -73.7964687716)],
['Town of Milan', '', 'http://www.milan-ny.gov', (41.9550242074, -73.7655031529)],
['Village of Millerton', '', 'http://www.villageofmillerton.com/', (41.9552465996, -73.5097033308)],
['Town of North East', '', 'http://www.townofnortheastny.gov', (41.9974650529, -73.5453650384)],
['Village of Pawling', '', 'http://www.villageofpawling.org/', (41.5624500776, -73.600667761)],
['Town of Pawling', '', 'http://www.pawling.org', (41.5691937853, -73.5995282143)],
['Town of Pine Plains', '', 'http://www.pineplains-ny.gov', (41.9724844107, -73.6327752702)],
['Town of Pleasant Valley', '', 'http://pleasantvalley-ny.gov', (41.7427226147, -73.82839409)],
['Village of Wappingers Falls', '', 'http://www.wappingersfallsny.gov/', (41.5970243403, -73.9175311838)],
['Town of Poughkeepsie', 'http://www.townofpoughkeepsie.com/human_resources/index.html?_sm_au_=ivv8z8lp1wffsnv6', 'http://www.townofpoughkeepsie.com', (41.6934697227, -73.8886993083)],
['Village of Red Hook', '', 'http://www.redhooknyvillage.org/', (41.9792069627, -73.8831240169)],
['Village of Tivoli', '', 'http://www.tivoliny.org', (42.0524549591, -73.9113811057)],
['Town of Red Hook', '', 'http://www.redhook.org', (41.9792069627, -73.8831240169)],
['Town of Stanford', '', 'http://www.townofstanford.org', (41.8699776708, -73.7038511328)],
['Town of Wappinger', 'http://townofwappingerny.gov/employment-opportunities/', 'http://www.townofwappinger.us', (41.5852810099, -73.9183699215)],
['Village of Millbrook', '', 'http://www.village.millbrook.ny.us/', (41.7866626033, -73.6921995111)],
['Town of Washington', '', 'http://www.washingtonny.org', (41.7896150258, -73.678160088)],
['County of Dutchess', 'https://www.dutchessny.gov/CivilServiceInformationSystem/ApplicantWeb/frmAnnouncementList.aspx', 'http://www.dutchessny.gov', (41.7035996228, -73.9296264246)],
['Village of Alden', '', 'http://www2.erie.gov/village_alden/', (42.9001712214, -78.4910883099)],
['Town of Alden', 'http://www2.erie.gov/alden/index.php?q=employment-opportunities', 'http://www.alden.erie.gov', (42.9396224062, -78.548675907)],
['Village of Williamsville', 'http://walkablewilliamsville.com/government/employment/', 'http://www.village.williamsville.ny.us', (42.9624030704, -78.7457478671)],
['Town of Amherst', 'http://www.amherst.ny.us', 'http://www.amherst.ny.us', (42.9625609177, -78.7447535978)],
['Village of East Aurora', '', 'http://www.east-aurora.ny.us', (42.7676955077, -78.6134360486)],
['Town of Aurora', '', 'http://www.townofaurora.com', (42.7599617828, -78.6123372215)],
['Town of Boston', '', 'http://www.townofboston.com', (42.6523899673, -78.7445255027)],
['Village of Farnham', '', '', (42.5932091339, -79.0830689469)],
['Town of Brant', '', 'http://brantny.com', (42.5887297556, -79.0135760829)],
['Village of Depew', '', 'http://www.villageofdepew.org/', (42.9047156665, -78.6862756783)],
['Village of Sloan', 'http://www.villageofsloan.org/emply.htm', 'http://www.villageofsloan.org/', (42.8953534819, -78.7937737094)],
['Town of Cheektowaga', '', 'http://tocny.org', (42.9035640605, -78.7525961014)],
['Town of Clarence', 'http://www2.erie.gov/clarence/index.php?q=jobs', 'http://www2.erie.gov/clarence/', (42.9887349781, -78.6086899406)],
['Town of Colden', 'http://www.townofcolden.com/employment/', 'http://townofcolden.com', (42.6434242255, -78.6846651717)],
['Town of Collins', '', 'http://www.townofcollins.com', (42.5047950539, -78.8725099862)],
['Village of Springville', '', 'http://www.villageofspringvilleny.com/', (42.5088250316, -78.6675810286)],
['Town of Concord', '', 'http://townofconcordny.com/', (42.5095087985, -78.6662587197)],
['Town of Eden', '', 'http://www.edenny.gov', (42.652218051, -78.8954131397)],
['Town of Elma', 'http://www.elmanewyork.com/job_openings.html', 'http://www.elmanewyork.com', (42.8144495427, -78.6386479206)],
['Village of Angola', '', 'http://www.villageofangola.org/', (42.6375457755, -79.028767845)],
['Town of Evans', 'http://townofevans.org/employment.html', 'http://townofevans.org', (42.6465615815, -79.0418825569)],
['Town of Grand Island', '', 'http://www.grand-island.ny.us', (43.0228965799, -78.9650837465)],
['Village of Blasdell', '', 'http://wwvillageofblasdell.com', (42.7979907414, -78.8301465474)],
['Village of Hamburg', 'http://www.villagehamburg.com/employmentopportunities', 'http://www.villagehamburg.com', (42.716052715, -78.8333786123)],
['Town of Hamburg', '', 'http://www.townofhamburgny.com/', (42.7295660126, -78.8254812756)],
['Town of Holland', '', 'http://www.townofhollandny.com', (42.642860282, -78.5422023955)],
['Village of Lancaster', '', 'http://www.lancastervillage.org/', (42.9003064951, -78.6701676619)],
['Town of Lancaster', '', 'http://www.lancasterny.gov', (42.9011803771, -78.6700997753)],
['Town of Marilla', '', 'http://townofmarilla.com', (42.8277969312, -78.5548739844)],
['Village of Akron', '', 'http://www.erie.gov/akron', (43.0197698751, -78.5018929943)],
['Town of Newstead', 'http://www2.erie.gov/newstead/index.php?q=legal-notices-job-postings', 'http://www.erie.gov/newstead', (43.0121069072, -78.5032533414)],
['Village of North Collins', '', 'http://www.northcollinsny.org/', (42.5948492044, -78.9405290148)],
['Town of North Collins', '', 'http://www.northcollinsny.org', (42.5941035007, -78.9406039587)],
['Village of Orchard Park', '', 'http://www.orchardparkvillage.org/', (42.7665492307, -78.7434387695)],
['Town of Orchard Park', 'http://www.orchardparkny.org/employment/', 'http://www.orchardparkny.org', (42.7665492115, -78.743438805)],
['Town of Sardinia', 'http://www2.erie.gov/sardinia/index.php?q=employment', 'http://www.erie.gov/sardinia/', (42.5428912805, -78.5087036506)],
['Village of Kenmore', '', 'http://www.villageofkenmore.org/', (42.9636910128, -78.8697615625)],
['Town of Tonawanda', '', 'http://www.tonawanda.ny.us/', (42.9636910128, -78.8697615625)],
['Town of Wales', '', 'http://www.townofwales.com', (42.7684139896, -78.5332259367)],
['Town of West Seneca', 'http://www.westseneca.net/jobs', 'http://www.westseneca.net', (42.8334249546, -78.7547809834)],
['County of Erie', 'http://www.erie.gov/employment', 'http://www2.erie.gov/', (42.8840200109, -78.876696021)],
['Town of Chesterfield', '', 'http://www.co.essex.ny.us/chesterfield.asp', (44.5032949446, -73.4808040496)],
['Town of Crown Point', '', 'http://townofcrownpoint.com/', (43.9572549501, -73.5189050382)],
['Town of Elizabethtown', '', 'http://etownny.com/', (44.2148610309, -73.5938684886)],
['Town of Essex', '', 'http://www.essexnewyork.org', (44.3094459904, -73.3516430421)],
['Town of Jay', 'http://townofjayny.gov/employment-opportunity-4/', 'http://www.jayny.com', (44.4391169518, -73.6777500385)],
['Town of Keene', '', 'http://www.townofkeeneny.com/', (44.2653849381, -73.7956100828)],
['Town of Lewis', '', 'http://www.lewisny.com', (44.2761210406, -73.5626885381)],
['Town of Minerva', '', 'http://www.townofminerva.com', (43.8560599874, -74.0418000911)],
['Village of Port Henry', '', 'http://www.porthenrymoriah.com/living-here/village-port-henry', (44.0344089422, -73.4622130751)],
['Town of Moriah', '', 'http://www.townofmoriah.com/', (44.043178603, -73.4582392108)],
['Town of Newcomb', '', 'http://www.newcombny.com/', (44.0048299293, -74.1379450763)],
['Village of Lake Placid', '', 'http://villageoflakeplacid.ny.gov/', (44.2822734829, -73.9824911064)],
['Village of Saranac Lake', 'http://saranaclakeny.gov/index.php?section=about-careers', 'http://www.saranaclakeny.gov/', (44.3241392077, -74.1319860191)],
['Town of North Elba', 'http://www.northelba.org/?page=government/human-resources', 'http://www.northelba.org', (44.2823310033, -73.9823284079)],
['Town of North Hudson', '', 'http://northhudsonny.com', (43.998849973, -73.7997100944)],
['Town of Schroon', '', 'http://www.schroon.net/', (43.8367049578, -73.7611950669)],
['Town of St Armand', '', 'http://www.co.essex.ny.us/starmand.asp', (44.4078096998, -74.0866613061)],
['Town of Ticonderoga', '', 'http://www.townofticonderoga.com', (43.8488190028, -73.4237901363)],
['Town of Westport', '', 'http://www.westportny.net', (44.1858079741, -73.435536252)],
['Town of Willsboro', '', 'http://www.townofwillsboro.com', (44.3714509733, -73.3966785941)],
['Town of Wilmington', '', 'http://www.townofwilmington.org', (44.3779249515, -73.8409750013)],
['County of Essex', 'http://www.co.essex.ny.us/jobs.asp', 'http://www.co.essex.ny.us/', (44.2071799834, -73.6125850881)],
['Town of Bangor', '', '', (44.7870149025, -74.4135700726)],
['Town of Bellmont', '', 'http://www.nnyacgs.com/town_of_belmont.html', (44.8580349274, -74.0336850122)],
['Town of Bombay', '', 'http://www.bombayny.us', (44.9231578063, -74.5770906645)],
['Town of Brandon', '', 'http://www.nnyacgs.com/town_of_brandon.html', (44.7870149025, -74.4135700726)],
['Town of Brighton', 'http://www.townofbrighton.org/index.aspx?nid=219&amp;_sm_au_=ivv8z8lp1wffsnv6', 'http://www.townofbrighton.org', (44.4763099718, -74.3058500443)],
['Village of Burke', '', '', (44.9033154295, -74.1728924443)],
['Town of Burke', '', '', (44.9214526174, -74.1477666963)],
['Village of Chateaugay', '', '', (44.8194049979, -74.0589850282)],
['Town of Chateaugay', '', 'http://www.chateaugayny.org', (44.9260760231, -74.087217152)],
['Town of Constable', '', '', (44.9527299835, -74.3204550377)],
['Town of Dickinson', '', 'http://www.townofdickinson.com', (42.1192815531, -75.9109978392)],
['Town of Duane', '', 'http://www.duaneny.com', (44.7281199535, -74.2771800816)],
['Town of Fort Covington', '', '', (44.9653699951, -74.4897251)],
['Town of Franklin', '', 'http://www.townoffranklin.com', (42.3694350548, -75.1827050963)],
['Town of Harrietstown', '', 'http://www.harrietstown.org/', (44.3253577883, -74.1321720121)],
['Village of Malone', '', '', (44.8490919613, -74.2962903014)],
['Town of Malone', '', 'http://www.malonetown.com', (44.7281199535, -74.2771800816)],
['Village of Brushton', '', '', (44.8330739036, -74.5043348779)],
['Town of Moira', '', 'http://www.porthenrymoriah.com/', (44.8506500007, -74.5775500747)],
['Town of Santa Clara', '', 'http://www.townofsantaclara.com', (44.3480913621, -74.322654055)],
['Village of Tupper Lake', '', 'https://tupper-lake.com/about/village-of-tupper-lake-2/', (44.2227488064, -74.4662337308)],
['Town of Tupper Lake', '', 'https://tupper-lake.com/about/town-of-tupper-lake-2/', (44.23532357, -74.4680676287)],
['Town of Waverly', '', '', (44.6277099034, -74.6384900398)],
['Town of Westville', '', '', (44.7281199535, -74.2771800816)],
['County of Franklin', '', 'http://www.franklincony.org', (44.8491624234, -74.2953066759)],
['Town of Bleecker', '', '', (43.119739991, -74.3656600918)],
['Village of Broadalbin', '', '', (43.0858199419, -74.159490091)],
['Town of Broadalbin', '', 'http://www.townofbroadalbin.org', (43.070544736, -74.174969821)],
['Town of Caroga', '', 'http://www.carogalakeny.com', (43.1834549203, -74.5095500149)],
['Town of Ephratah', '', 'http://www.ephratah-town.org', (43.0106899219, -74.3890800489)],
['Town of Johnstown', '', 'http://townofjohnstown.org/', (43.0106899219, -74.3890800489)],
['Village of Mayfield', '', 'http://www.villageofmayfield.com', (43.1021912939, -74.2614483559)],
['Town of Mayfield', '', 'http://www.mayfieldny.org', (43.1095512734, -74.2641483569)],
['Village of Northville', '', '', (43.2214916489, -74.1692770592)],
['Town of Northampton', '', 'http://www.townofnorthampton.com', (43.2259029539, -74.1719270349)],
['Village of Dolgeville', '', 'http://www.villageofdolgeville.org', (43.1033112525, -74.770558175)],
['Town of Oppenheim', '', '', (43.1160249541, -74.7892900917)],
['Town of Perth', '', 'http://www.perthny.com', (43.0181249708, -74.1919499228)],
['Town of Stratford', '', 'http://www.stratfordny.com', (43.1801512839, -74.6914782211)],
['County of Fulton', 'http://www.fultoncountyny.gov/node/5', 'http://www.fultoncountyny.gov/', (43.0067712509, -74.3749383393)],
['Town of Alabama', '', '', (43.1361199312, -78.2972099858)],
['Village of Alexander', '', '', (42.9020665513, -78.2598826586)],
['Village of Attica', '', 'http://attica.org', (42.8646144894, -78.2833312528)],
['Town of Alexander', '', 'http://www.townofalexander.com', (42.9013421147, -78.2033574316)],
['Town of Batavia', '', 'http://www.townofbatavia.com', (43.0096574647, -78.2288414304)],
['Village of Bergen', '', 'http://www.villageofbergen.com', (43.0852348872, -77.9425705803)],
['Town of Bergen', '', 'http://www.bergenny.org', (43.0893604488, -77.9420138994)],
['Town of Bethany', '', 'http://www.townofbethany.com', (42.9079524287, -78.1332831467)],
['Town of Byron', '', 'http://www.byronny.com', (43.0719731557, -78.0643826226)],
['Town of Darien', '', 'http://www.townofdarienny.com', (42.9025618346, -78.3889795005)],
['Village of Elba', '', 'http://www.villageofelba.com', (43.093294979, -78.162479935)],
['Town of Elba', '', 'http://www.elbanewyork.com', (43.0799025416, -78.1886338147)],
['Village of LeRoy', '', '', (42.9774882, -77.9926633561)],
['Town of LeRoy', '', 'http://www.leroyny.org', (42.977995369, -77.9959999729)],
['Village of Oakfield', '', 'http://www.oakfield.govoffice.com', (43.0670924789, -78.2721935842)],
['Town of Oakfield', '', 'http://www.townofoakfieldny.com', (43.066024946, -78.2707299748)],
['Town of Pavilion', '', 'http://www.townofpavilion.com', (42.8769580547, -78.0266407909)],
['Village of Corfu', '', 'http://www.corfuny.com', (42.96251911, -78.390990369)],
['Town of Pembroke', '', 'http://www.townofpembroke.org', (42.9933508729, -78.404704449)],
['Town of Stafford', '', 'http://www.townofstafford.com', (42.9744949638, -78.0800749953)],
['County of Genesee', 'http://www.co.genesee.ny.us/departments/humanresources/index.html', 'http://www.co.genesee.ny.us', (42.9969599591, -78.2176699417)],
['Town of Ashland', '', 'http://www.townofashland.net', (42.0220900548, -76.7656799332)],
['Village of Athens', '', 'http://www.visithistoricathens.com', (42.2625297051, -73.8107996943)],
['Town of Athens', '', 'http://www.townofathensny.com', (42.2625297051, -73.8107996943)],
['Town of Cairo', '', 'http://www.townofcairo.com', (42.3004822968, -73.999480681)],
['Village of Catskill', '', 'http://www.villageofcatskill.net', (42.2204724953, -73.8657920414)],
['Town of Catskill', '', 'http://www.townofcatskillny.gov', (42.2210373069, -73.8664642865)],
['Village of Coxsackie', '', 'http://www.villageofcoxsackie.com', (42.3560198426, -73.8074971667)],
['Town of Coxsackie', '', 'http://www.coxsackie.org', (42.3515917238, -73.796347747)],
['Town of Durham', '', 'http://www.durhamny.com', (42.3960270521, -74.1541039801)],
['Town of Greenville', '', 'http://www.townofgreenvilleny.com', (42.4542350944, -74.0298050163)],
['Town of Halcott', '', 'http://www.townofhalcott.org', (42.1830300213, -74.5412150382)],
['Village of Hunter', '', 'http://villageofhunterny.org', (42.2325750723, -74.2616950624)],
['Village of Tannersville', '', 'http://tannersvilleny.org/', (42.1957418834, -74.1313971342)],
['Town of Hunter', '', 'http://www.townofhuntergov.com', (42.2132000617, -74.1190800226)],
['Town of Jewett', '', 'http://www.townofjewett.com', (42.2691950618, -74.2847200646)],
['Town of Lexington', '', 'http://www.lexingtonny.com', (42.2446830781, -74.3800102536)],
['Town of New Baltimore', '', 'http://www.townofnewbaltimore.org', (42.465070094, -73.9571550177)],
['Town of Prattsville', '', 'http://www.prattsville.org', (42.3254600231, -74.4843200407)],
['Town of Windham', '', 'http://www.townofwindham.com/', (42.2912817502, -74.2176252378)],
['County of Greene', '', 'http://www.discovergreene.com', (42.2199935943, -73.866162019)],
['Town of Arietta', '', 'http://www.townofarietta.com', (0.0, 0.0)],
['Town of Benson', '', 'http://www.hamiltoncounty.com/municipalities/benson', (43.3247849795, -74.2919950885)],
['Town of Hope', '', 'http://www.hamiltoncounty.com/municipalities/hope', (43.3247849795, -74.2919950885)],
['Town of Indian Lake', '', 'http://townofindianlake.org', (43.7862589542, -74.2726030657)],
['Town of Inlet', '', 'http://www.townofinlet.org/', (43.7687019169, -74.813163071)],
['Village of Speculator', '', 'http://villageofspeculator.org/', (43.5018409244, -74.3643339462)],
['Town of Lake Pleasant', '', 'http://www.lakepleasantny.org', (43.4799537702, -74.3917670968)],
['Town of Long Lake', '', 'http://mylonglake.com/long-lake/ll-local-government/', (43.9791899103, -74.5669050195)],
['Town of Morehouse', '', 'http://www.townofmorehouse.com/', (43.390904999, -74.7167450088)],
['Town of Wells', '', 'http://townofwells.org', (43.466014937, -74.2936700171)],
['County of Hamilton', 'http://www.hamiltoncounty.com/government/departments-services', 'http://www.hamiltoncounty.com', (43.4704694876, -74.4121458971)],
['Town of Columbia', '', 'http://www.townofcolumbia.org', (42.9685999314, -75.078485092)],
['Town of Danube', '', 'http://www.townofdanube.com', (42.9849612717, -74.8051282288)],
['Village of Middleville', '', '', (43.1410499042, -74.9008000059)],
['Town of Fairfield', '', 'http://townoffairfieldny.org', (43.0971349154, -74.9268450722)],
['Village of Frankfort', '', 'http://villageoffrankfortny.org/', (43.0389046005, -75.0700936141)],
['Town of Frankfort', '', 'http://www.townoffrankfort.com', (43.0492249305, -75.1167000806)],
['Village of Ilion', '', 'http://www.ilionny.com/', (43.0147194427, -75.0376818372)],
['Village of Mohawk', '', '', (43.0079578436, -75.0056116128)],
['Town of German Flatts', '', '', (42.9666399551, -74.9399450822)],
['Village of Herkimer', '', 'http://village.herkimer.ny.us/', (43.0269267628, -74.9869378288)],
['Town of Herkimer', '', 'http://www.townofherkimer.org/', (43.0254300838, -74.9877377941)],
['Town of Litchfield', '', 'http://www.townoflitchfield.com', (42.8481799361, -75.2723750588)],
['Town of Little Falls', '', 'http://townoflittlefalls.com', (42.9666399551, -74.9399450822)],
['Town of Manheim', '', 'http://www.townofmanheim.org/', (43.1003412564, -74.7742682158)],
['Village of Newport', '', 'http://www.villageofnewportny.org/', (42.5936950958, -75.1930650091)],
['Village of Poland', '', 'http://villageofpolandny.org/', (43.2133749847, -75.0948400458)],
['Town of Newport', '', 'http://www.townofnewport.net', (43.1776085343, -75.0154771266)],
['Town of Norway', '', 'http://www.townofnorway.net/', (43.2048813027, -74.9451781526)],
['Town of Ohio', '', 'http://www.ohiony.us/', (43.3120390581, -74.961798701)],
['Village of Cold Brook', '', '', (43.3417399107, -74.94255509)],
['Town of Russia', '', 'http://www.townofrussia.com', (43.2278104221, -75.0642902505)],
['Town of Salisbury', '', '', (43.1717149127, -74.7587600638)],
['Town of Schuyler', '', 'http://townofschuyler.com', (43.1117779674, -75.1905382263)],
['Town of Stark', '', '', (42.8736899607, -74.8494100764)],
['Town of Warren', '', '', (42.9307113419, -74.9649481012)],
['Town of Webb', '', 'http://townofwebb.org', (43.8384799055, -75.0771200917)],
['Village of West Winfield', '', '', (42.8481799361, -75.2723750588)],
['Town of Winfield', '', '', (42.8481799361, -75.2723750588)],
['County of Herkimer', '', 'http://herkimercounty.org/content', (43.0289612799, -74.9882181643)],
['Village of Adams', '', '', (43.8075042158, -76.0249969415)],
['Town of Adams', '', 'http://www.townofadams.com', (43.8075041889, -76.0249969286)],
['Village of Alexandria Bay', '', 'http://www.alexandria-bay.ny.us/', (44.2873949391, -75.9307549129)],
['Town of Alexandria', '', 'http://townofalexandria.org', (44.2873949391, -75.9307549129)],
['Village of Antwerp', '', 'http://villageofantwerp.net/', (44.1995081897, -75.6076119428)],
['Town of Antwerp', '', '', (44.1995081897, -75.6076119428)],
['Village of Brownville', '', 'http://www.villageofbrownvilleny.org/', (44.0034449451, -75.98317494)],
['Village of Dexter', '', 'http://www.villageofdexterny.com/', (44.0056139218, -76.0436746959)],
['Village of Glen Park', '', '', (44.0034449451, -75.98317494)],
['Town of Brownville', '', '', (44.0034449451, -75.98317494)],
['Village of Cape Vincent', '', 'http://www.villageofcapevincent.org/', (44.1350299521, -76.2777199433)],
['Town of Cape Vincent', '', 'http://townofcapevincent.org', (44.1193434491, -76.3317976279)],
['Village of West Carthage', '', 'http://villageofwestcarthage.org/', (43.9696578123, -75.623328698)],
['Town of Champion', '', 'http://www.racog.org', (43.9680023209, -75.6235034754)],
['Village of Clayton', '', 'http://www.villageofclayton.org', (44.2209399136, -76.1006049675)],
['Town of Clayton', '', 'http://www.townofclayton.com', (44.242551102, -76.0867775901)],
['Village of Ellisburg', '', '', (43.7376749073, -76.1510499272)],
['Village of Mannsville', '', '', (43.7125985696, -76.0638464604)],
['Town of Ellisburg', '', '', (43.729072214, -76.1413827558)],
['Town of Henderson', '', 'http://townofhendersonny.org/', (43.8425311493, -76.1809296131)],
['Village of Sackets Harbor', '', 'http://sacketsharborny.com/', (43.9162249313, -76.0892698995)],
['Town of Hounsfield', '', 'http://townofhounsfield-ny.gov', (43.9369943171, -76.0712015804)],
['Village of Black River', '', 'http://www.blackriverny.org/', (44.0108429516, -75.7952602544)],
['Village of Evans Mills', '', 'http://townofleray.org/evansmillsmap.htm', (44.091334965, -75.8152650783)],
['Town of LeRay', '', 'http://www.townofleray.org', (44.091334965, -75.8152650783)],
['Town of Lorraine', '', 'http://townoflorraine.com', (43.7666053584, -75.9543599504)],
['Village of Chaumont', '', '', (44.0949199275, -76.1140349794)],
['Town of Lyme', '', 'http://townoflyme.com', (44.0657104087, -76.1278814768)],
['Town of Orleans', '', 'http://www.townoforleans.com', (44.1931275173, -75.9614603531)],
['Town of Pamelia', '', '', (43.9757850004, -75.9168199264)],
['Village of Philadelphia', '', '', (44.1574387371, -75.704884102)],
['Town of Philadelphia', '', '', (44.1513449419, -75.7037850442)],
['Town of Rodman', '', 'http://www.townofrodmanny.org', (43.8406699841, -75.8970599595)],
['Town of Rutland', '', '', (43.9527472247, -75.8005944078)],
['Village of Theresa', '', '', (44.2150402262, -75.7976348343)],
['Town of Theresa', '', 'http://www.townoftheresany.com', (44.2147856747, -75.7966473138)],
['Town of Watertown', '', 'http://www.townofwatertownny.org/', (43.961915894, -75.9421972395)],
['Village of Carthage', '', '', (43.9772128424, -75.6089895221)],
['Village of Deferiet', '', 'http://www.villageofdeferiet.com/', (44.0394949312, -75.6839900004)],
['Village of Herrings', '', '', (44.0238899588, -75.653305967)],
['Town of Wilna', '', '', (43.9790277145, -75.6078495533)],
['Town of Worth', '', '', (43.7848458663, -75.8774314226)],
['County of Jefferson', 'http://www.co.jefferson.ny.us', 'http://www.co.jefferson.ny.us', (43.9754343642, -75.9136642003)],
['Village of Croghan', '', 'http://croghanny.org/', (43.89197891, -75.3860804966)],
['Town of Croghan', '', 'http://www.townofcroghan.com/', (43.9573999233, -75.2787750539)],
['Village of Castorland', '', 'http://villageofcastorlandny.org/', (43.8867548956, -75.5138967038)],
['Village of Copenhagen', '', 'http://villageofcopenhagen.org/', (43.8943199398, -75.7595550332)],
['Town of Denmark', '', 'http://townofdenmarkny.com', (43.7797499126, -75.4977950884)],
['Village of Harrisville', '', 'http://villageofharrisvilleny.org/', (44.1900299236, -75.2707450855)],
['Town of Diana', '', '', (44.1900299236, -75.2707450855)],
['Town of Greig', '', 'http://townofgreig.org/', (43.6896049599, -75.2919500924)],
['Town of Harrisburg', '', 'http://www.tughillcouncil.com/harrisburg.htm', (43.7797499126, -75.4977950884)],
['Town of Lewis', '', 'http://www.lewisny.com', (44.2761210406, -73.5626885381)],
['Village of Port Leyden', '', '', (43.5862647096, -75.3482185016)],
['Town of Leyden', '', 'http://townofleyden.org/', (43.5344512541, -75.3678598847)],
['Village of Lowville', '', 'http://villageoflowville.org/', (43.7970731828, -75.4846706337)],
['Town of Lowville', '', 'http://www.lowville.ny.us/', (43.7967317031, -75.4845093474)],
['Village of Lyons Falls', '', 'http://villageoflyonsfalls.webs.com/', (43.6308725897, -75.3727616618)],
['Town of Lyonsdale', '', '', (43.6035599467, -75.337100041)],
['Town of Sodus', '', 'http://sodusny.org/', (43.2353229236, -77.062021085)],
['Town of Martinsburg', '', 'http://townofmartinsburg.org/', (43.737376878, -75.4686475043)],
['Town of Montague', '', '', (43.7797499126, -75.4977950884)],
['Town of New Bremen', '', 'http://townofnewbremen.weebly.com', (43.8851049165, -75.4578400199)],
['Town of Osceola', '', '', (43.3468499283, -75.8840249866)],
['Town of Pinckney', '', 'http://townofpinckney.org', (43.8943199398, -75.7595550332)],
['Village of Turin', '', '', (43.6275423989, -75.4098533332)],
['Town of Watson', '', 'http://www.townofwatsonny.com/', (43.804123207, -75.3633010631)],
['Village of Constableville', '', '', (43.5634089599, -75.4303710867)],
['Town of West Turin', '', '', (43.5796300011, -75.5322300899)],
['County of Lewis', '', 'http://www.lewiscountyny.org', (43.7907877556, -75.4956221444)],
['Village of Avon', '', 'http://www.avon-ny.org/index_village.html', (42.9106842722, -77.7455381086)],
['Town of Avon', '', 'http://www.avon-ny.org/index_town.html', (42.9108705074, -77.7467971022)],
['Village of Caledonia', '', 'http://www.villageofcaledoniany.org/', (42.9733003089, -77.8547870372)],
['Town of Caledonia', '', 'http://www.townofcaledoniany.com/', (42.9689027269, -77.8635351457)],
['Town of Conesus', '', 'http://www.town.conesus.ny.us', (42.7190851379, -77.6762748566)],
['Village of Geneseo', '', 'http://www.geneseony.org/', (42.7951616152, -77.8166298643)],
['Town of Geneseo', '', 'http://www.geneseony.org/', (42.7951616152, -77.8166298643)],
['Town of Groveland', '', 'http://www.grovelandny.org', (42.7128210561, -77.7781275954)],
['Village of Leicester', '', 'http://www.villageofleicester.org/', (42.7715305239, -77.8941871566)],
['Town of Leicester', '', 'http://www.townofleicester.org', (42.7720154498, -77.8985785669)],
['Village of Lima', '', 'http://www.townoflima.org', (42.9055102027, -77.6105948229)],
['Town of Lima', '', 'http://www.townoflima.org', (42.9055102027, -77.6105948229)],
['Village of Livonia', '', 'http://www.livoniany.org/contactus.html', (42.8192225966, -77.6695509425)],
['Town of Livonia', '', 'http://www.livoniany.com', (42.8191958781, -77.6688604289)],
['Village of Mount Morris', '', 'http://www.villageofmountmorris.com', (42.7242205616, -77.8725493255)],
['Town of Mount Morris', '', 'http://mtmorrisny.com', (42.7245582824, -77.87308765)],
['Village of Dansville', '', 'http://www.dansvilleny.org', (42.5595878548, -77.6956915149)],
['Town of North Dansville', '', '', (42.5594662469, -77.6951473827)],
['Village of Nunda', '', 'http://www.nundany.org/', (42.5827883309, -77.9351919231)],
['Town of Nunda', '', 'http://www.town.nunda.ny.us', (42.5929850233, -77.8878699495)],
['Town of Ossian', '', 'http://www.townofossianny.us/', (42.5211151311, -77.7788414369)],
['Town of Portage', '', '', (42.5531460313, -77.9794779722)],
['Town of Sparta', '', 'http://www.sparta-ny.org/', (42.6210408075, -77.6993545745)],
['Town of Springwater', '', 'http://www.townofspringwaterny.org', (42.6348980925, -77.5972425025)],
['Town of West Sparta', '', 'http://townofwestsparta.org/', (42.6209426648, -77.7915095238)],
['Town of York', '', 'http://www.yorkny.org', (42.8719848954, -77.8856876401)],
['County of Livingston', '', 'http://www.livingstoncounty.us', (42.8004697824, -77.8165874932)],
['Town of Brookfield', '', 'http://www.brookfieldny.com', (42.815924921, -75.3510700486)],
['Village of Cazenovia', '', 'http://villageofcazenovia.com/', (42.900889911, -75.9074249714)],
['Town of Cazenovia', '', 'http://www.townofcazenovia.org', (42.9302806892, -75.8585452755)],
['Village of De Ruyter', '', 'http://www.deruyteronline.com/', (42.7557150467, -75.8925469791)],
['Town of De Ruyter', '', 'http://www.deruyternygov.us/', (42.7589398119, -75.8847234592)],
['Village of Morrisville', '', 'https://www.madisoncounty.ny.gov/village-morrisville/home', (42.9223899508, -75.6713550822)],
['Town of Eaton', '', 'http://townofeaton.com/', (42.9223899508, -75.6713550822)],
['Town of Fenner', '', 'http://townoffenner.com/', (42.8748411968, -75.8486994517)],
['Town of Georgetown', '', 'https://www.madisoncounty.ny.gov/town-georgetown/home', (42.7716449511, -75.7731100486)],
['Village of Hamilton', '', 'http://www.hamilton-ny.gov/', (42.8272051622, -75.5429114351)],
['Town of Hamilton', '', 'http://www.townofhamiltonny.org/', (42.8262972417, -75.5442926766)],
['Town of Lebanon', '', 'http://townoflebanon.org/', (42.7219250452, -75.558380058)],
['Village of Canastota', '', 'http://www.canastota.com/', (43.0778015803, -75.7519133751)],
['Village of Wampsville', '', 'http://wampsvillecny.com/', (43.0779771124, -75.7066635133)],
['Town of Lenox', '', 'http://www.lenoxny.com/', (43.0778015803, -75.7519133751)],
['Town of Lincoln', '', 'http://townoflincoln.org/', (43.0430182941, -75.7449198489)],
['Village of Madison', '', '', (42.891997956, -75.5115050669)],
['Town of Madison', '', 'http://townofmadisonny.org/', (42.9432649513, -75.5360300527)],
['Town of Nelson', '', 'http://www.townofnelson-ny.com/', (42.900889911, -75.9074249714)],
['Town of Smithfield', '', 'http://townofsmithfield.org/', (42.9311829704, -75.6899890259)],
['Village of Munnsville', '', 'http://www.madisoncounty.ny.gov/village-munnsville/home', (42.974114998, -75.5941350034)],
['Town of Stockbridge', '', 'https://www.madisoncounty.ny.gov/town-stockbridge/home', (42.9679739993, -75.6340620806)],
['Village of Chittenango', '', 'http://www.chittenango.org', (43.0449679636, -75.865706325)],
['Town of Sullivan', '', 'http://townofsullivan.org/', (43.0865684927, -75.8728907169)],
['County of Madison', 'https://www.madisoncounty.ny.gov/287/personnel', 'http://www.madisoncounty.ny.gov/', (43.080710403, -75.7073141012)],
['Town of Brighton', 'http://www.townofbrighton.org/index.aspx?nid=219&amp;_sm_au_=ivv8z8lp1wffsnv6', 'http://www.townofbrighton.org', (44.4763099718, -74.3058500443)],
['Town of Chili', 'http://www.townofchili.org/notice-category/job-postings', 'http://www.townofchili.org', (43.0997223857, -77.7594437243)],
['Town of Clarkson', '', 'http://www.clarksonny.org', (43.2326680961, -77.9276512803)],
['Village of East Rochester', '', 'http://www.eastrochester.org', (43.112759322, -77.4862160545)],
['Town of East Rochester', '', 'http://www.eastrochester.org', (43.112759322, -77.4862160545)],
['Town of Gates', '', 'http://www.townofgates.org', (43.1492768245, -77.6944677253)],
['Town of Greece', 'http://greeceny.gov/residents/employment-opportunities', 'http://www.greeceny.gov', (43.2682899232, -77.6773599523)],
['Town of Hamlin', '', 'http://www.hamlinny.org', (43.2970693254, -77.9201608719)],
['Town of Henrietta', '', 'http://www.townofhenrietta.org', (43.0661955215, -77.6262489622)],
['Town of Irondequoit', 'http://www.irondequoit.org/town-departments/human-resources/town-employment-opportunities?_sm_au_=ivv8z8lp1wffsnv6', 'http://www.irondequoit.org', (43.2118981185, -77.5829511109)],
['Village of Honeoye Falls', '', 'http://www.villageofhoneoyefalls.org/', (42.9557410052, -77.5898193192)],
['Town of Mendon', '', 'http://www.townofmendon.org', (42.9522464613, -77.5916010694)],
['Village of Spencerport', '', 'http://www.vil.spencerport.ny.us', (43.1915231574, -77.8020851088)],
['Town of Ogden', '', 'http://www.ogdenny.com', (43.1707325216, -77.8022248886)],
['Village of Hilton', '', 'http://www.hiltonny.org', (43.289044936, -77.7979899666)],
['Town of Parma', '', 'http://www.parmany.org', (43.2523171096, -77.7898968832)],
['Town of Penfield', 'http://www.penfield.org', 'http://www.penfield.org', (43.1608837079, -77.4461733913)],
['Village of Fairport', '', 'http://www.village.fairport.ny.us/', (43.1006477575, -77.4415786951)],
['Town of Perinton', 'http://www.perinton.org/departments/finpers', 'http://www.perinton.org/', (43.0819537538, -77.4312292729)],
['Village of Pittsford', '', 'http://www.villageofpittsford.org', (43.091849366, -77.5151747088)],
['Town of Pittsford', 'http://www.townofpittsford.org/home-hr?_sm_au_=ivv8z8lp1wffsnv6', 'http://www.townofpittsford.org', (43.0906078629, -77.5157510365)],
['Village of Churchville', '', 'http://www.churchville.net', (43.104018921, -77.8834818213)],
['Town of Riga', '', 'http://www.townofriga.org', (43.1041553527, -77.8844606132)],
['Town of Rush', '', 'http://www.townofrush.com', (42.995410265, -77.6463440896)],
['Village of Brockport', '', 'http://www.brockportny.org', (43.2143455828, -77.9363985831)],
['Town of Sweden', '', 'http://www.townofsweden.org', (43.2140922764, -77.9378582505)],
['Village of Webster', '', 'http://www.villageofwebster.com', (43.2119854657, -77.4314136534)],
['Town of Webster', 'http://www.ci.webster.ny.us/index.aspx?nid=85&amp;_sm_au_=ivv8z8lp1wffsnv6', 'http://www.ci.webster.ny.us', (43.2091622431, -77.4584098633)],
['Village of Scottsville', '', 'http://www.scottsvilleny.org/', (43.0200522772, -77.7496272308)],
['Town of Wheatland', '', 'http://www.townofwheatland.org', (43.0200522772, -77.7496272308)],
['County of Monroe', 'http://www2.monroecounty.gov/employment-index.php', 'http://www.monroecounty.gov', (43.1551462954, -77.6135791343)],
['Village of Fort Johnson', '', '', (42.961831966, -74.2460720764)],
['Village of Hagaman', '', 'https://www.co.montgomery.ny.us/sites/public/municipal/Municipal_Development/VillageOfHagaman.aspx', (42.9773826555, -74.1512989502)],
['Town of Amsterdam', '', 'http://www.townofamsterdam.org/', (42.9127999668, -74.2028650475)],
['Village of Ames', '', 'https://www.co.montgomery.ny.us/sites/public/municipal/Municipal_Development/VillageOfAmes.aspx', (42.8250199442, -74.6709350821)],
['Village of Canajoharie', '', 'http://villageofcanajoharie.org/', (42.8250199442, -74.6709350821)],
['Village of Fort Plain', '', 'http://villageoffortplain.com/', (42.9338144313, -74.6247270839)],
['Village of Remsen', '', 'http://villageofremsen.org/', (43.3256973732, -75.1854178294)],
['Town of Canajoharie', '', 'https://www.co.montgomery.ny.us/sites/public/municipal/Municipal_Development/TownOfCanajoharie.aspx', (42.9056988634, -74.5722436797)],
['Town of Charleston', '', 'http://www.townofcharleston.org/', (42.8423199698, -74.4540400894)],
['Town of Florida', '', 'http://www.co.montgomery.ny.us/florida/', (42.9127999668, -74.2028650475)],
['Village of Fultonville', '', 'http://fultonville.org/', (42.9469299883, -74.3711090249)],
['Town of Glen', '', 'https://www.co.montgomery.ny.us/sites/public/municipal/Municipal_Development/TownOfGlen.aspx', (42.8826549962, -74.3610350419)],
['Town of Minden', '', 'http://townofminden.org/', (42.9284284994, -74.6426757148)],
['Village of Fonda', '', 'http://villageoffonda.ny.gov/', (42.9545480117, -74.3743210914)],
['Town of Mohawk', '', 'http://www.townofmohawkny.com/', (42.9904149042, -74.4646250123)],
['Village of Nelliston', '', 'https://www.co.montgomery.ny.us/sites/public/municipal/Municipal_Development/VillageOfNelliston.aspx', (42.9334399688, -74.6123900217)],
['Village of Palatine Bridge', '', 'http://www.co.montgomery.ny.us/vpalatine/', (42.9197349854, -74.5376100078)],
['Town of Palatine', '', 'http://www.co.montgomery.ny.us/tpalatine/', (42.9128572821, -74.5816303452)],
['Town of Root', '', 'https://www.co.montgomery.ny.us/sites/public/municipal/Municipal_Development/TownOfRoot.aspx', (42.8021815411, -74.468706497)],
['Village of St Johnsville', '', 'http://www.stjohnsville.com/VillageIndex.htm', (42.9995707453, -74.6771303771)],
['Town of St Johnsville', '', 'http://stjohnsville.com/Town.htm', (42.9979320632, -74.683248165)],
['County of Montgomery', 'https://www.co.montgomery.ny.us/web/sites/departments/personnel/default.asp', 'http://www.co.montgomery.ny.us/', (42.9904149042, -74.4646250123)],
['Village of Atlantic Beach', '', 'http://www.villageofatlanticbeach.com', (40.5886018019, -73.737418682)],
['Village of Bellerose', '', 'http://www.bellerosevillage.org/', (40.7338600495, -73.7076500255)],
['Village of Cedarhurst', '', 'http://www.cedarhurst.gov/', (40.6236517759, -73.7245086697)],
['Village of East Rockaway', '', 'http://www.villageofeastrockaway.org/', (40.6463017711, -73.6638987045)],
['Village of Floral Park', '', 'http://www.fpvillage.org/', (40.7265900207, -73.7086600362)],
['Village of Freeport', '', 'http://www.freeportny.com/', (40.6583017609, -73.5865786865)],
['Village of Garden City', '', 'http://www.gardencityny.net/', (40.7261417474, -73.638528701)],
['Village of Hempstead', '', 'http://www.villageofhempstead.org', (40.7102217999, -73.6227286987)],
['Village of Hewlett Bay Park', '', '', (40.6384017722, -73.6999486664)],
['Village of Hewlett Harbor', '', 'http://www.hewlettharbor.org/', (40.6353217752, -73.6762887257)],
['Village of Hewlett Neck', '', '', (40.6384017722, -73.6999486664)],
['Village of Island Park', '', 'http://www.villageofislandpark.com/', (40.6010617988, -73.6556087519)],
['Village of Lawrence', '', 'http://www.villageoflawrence.org', (40.6140218047, -73.7372587226)],
['Village of Lynbrook', '', 'http://www.lynbrookvillage.com', (40.6577314742, -73.6741536904)],
['Village of Malverne', '', 'http://www.malvernevillage.org', (40.675911757, -73.6676387124)],
['Village of Mineola', '', 'http://www.mineola-ny.gov', (40.7478617487, -73.6417987415)],
['Village of New Hyde Park', '', 'http://www.vnhp.org', (40.7331617496, -73.6804387141)],
['Village of Rockville Centre', 'http://www.rvcny.us/jobs.html?_sm_au_=ivv8z8lp1wffsnv6', 'http://www.rvcny.us', (40.6595717428, -73.6454587589)],
['Village of South Floral Park', '', 'http://www.southfloralpark.org/', (40.7139917707, -73.7002687391)],
['Village of Stewart Manor', '', 'http://www.stewartmanor.us', (40.7201728586, -73.6886141536)],
['Village of Valley Stream', 'http://www.vsvny.org/index.asp?type=b_job&amp;sec=%7b05c716c7-40ee-49ee-b5ee-14efa9074ab9%7d&amp;_sm_au_=ivv8z8lp1wffsnv6', 'http://www.vsvny.org/', (40.6638017768, -73.7076186832)],
['Village of Woodsburgh', '', '', (40.6384017722, -73.6999486664)],
['Town of Hempstead', 'http://www.townofhempstead.org/civil-service-commission?_sm_au_=ivv8z8lp1wffsnv6', 'http://www.townofhempstead.org', (40.7058149917, -73.620000541)],
['Village of Baxter Estates', '', 'http://www.baxterestates.org/', (40.8354784426, -73.6999055022)],
['Village of East Hills', '', 'http://www.villageofeasthills.org/', (40.7947188734, -73.6370747528)],
['Village of East Williston', '', 'http://www.eastwilliston.org/', (40.7568079968, -73.6381880458)],
['Village of Flower Hill', '', 'http://www.villageflowerhill.org/', (40.8093917288, -73.6768887218)],
['Village of Great Neck', '', 'http://www.greatneckvillage.org/', (40.8007416194, -73.7283127312)],
['Village of Great Neck Estates', '', 'http://www.vgne.com/', (40.7864150623, -73.7287750904)],
['Village of Great Neck Plaza', '', 'http://www.greatneckplaza.net/', (40.7873700221, -73.7229600933)],
['Village of Kensington', '', 'http://www.villageofkensingtonny.gov/', (40.7903917512, -73.7298886515)],
['Village of Kings Point', '', 'http://www.villageofkingspoint.org/', (40.8151610778, -73.7567349244)],
['Village of Lake Success', '', 'http://www.villageoflakesuccess.com', (40.7654217369, -73.7127986556)],
['Village of Manor Haven', '', 'http://www.manorhaven.org/', (40.8426517396, -73.7094386745)],
['Village of Munsey Park', '', 'http://www.munseypark.org', (40.7954317399, -73.6795087071)],
['Village of North Hills', '', 'http://www.villagenorthhills.com/', (40.7642117335, -73.6711486821)],
['Village of Old Westbury', '', 'http://www.villageofwestbury.org', (40.7802625127, -73.6053268102)],
['Village of Plandome', '', 'http://www.plandomevillage.com/', (40.8075917673, -73.700238679)],
['Village of Plandome Heights', '', 'http://www.plandomeheights-ny.gov/', (40.7985462862, -73.698708724)],
['Village of Plandome Manor', '', 'http://plandomemanor.com/', (40.8130021922, -73.702826621)],
['Village of Port Washington North', '', 'http://www.portwashingtonnorth.org', (40.8392309303, -73.7032137289)],
['Village of Roslyn', '', 'http://www.historicroslyn.org', (40.8007417229, -73.652348721)],
['Village of Roslyn Estates', '', 'http://www.villageofroslynestates.com', (40.7879720916, -73.6597893744)],
['Village of Roslyn Harbor', '', 'http://www.roslynharbor.org', (40.8152923626, -73.6357709819)],
['Village of Russell Gardens', '', 'http://www.russellgardens.com', (40.7774817719, -73.728108729)],
['Village of Saddle Rock', '', 'http://www.saddlerock.org', (40.7968790745, -73.751532882)],
['Village of Sands Point', '', 'http://www.sandspoint.org', (40.851647021, -73.7187260931)],
['Village of Thomaston', '', 'http://www.villageofthomaston.org/', (40.7918017609, -73.7101286943)],
['Village of Westbury', '', 'http://www.villageofwestbury.org', (40.7570617651, -73.5865187113)],
['Village of Williston Park', '', 'http://www.villageofwillistonpark.org/', (40.7574377895, -73.6452707388)],
['Town of North Hempstead', 'http://www.northhempstead.com/employment-opportunities', 'http://www.northhempstead.com', (40.7958826244, -73.6989985374)],
['Village of Bayville', '', 'http://bayvilleny.gov/', (40.9097432485, -73.5664919959)],
['Village of Brookville', '', 'http://www.villageofbrookville.com/', (40.8195299535, -73.5862175043)],
['Village of Centre Island', '', 'http://centreisland.org/', (40.8594550096, -73.5063150786)],
['Village of Cove Neck', '', 'http://www.coveneck.org/', (40.8594550096, -73.5063150786)],
['Village of Farmingdale', '', 'http://www.farmingdalevillage.com/', (40.7283557631, -73.4446952043)],
['Village of Lattingtown', '', 'http://villageoflattingtown.org', (0.0, 0.0)],
['Village of Laurel Hollow', '', 'http://laurelhollow.org/', (40.8732246919, -73.4843109224)],
['Village of Massapequa Park', '', 'http://masspk.com', (40.6780922359, -73.4545240041)],
['Village of Matinecock', '', 'http://www.matinecockvillage.org', (40.8810450775, -73.58947006)],
['Village of Mill Neck', '', 'http://millneckvillage.com', (40.8789075039, -73.5631802988)],
['Village of Muttontown', '', 'http://www.villageofmuttontown.com', (40.8329235844, -73.5287653716)],
['Village of Old Brookville', '', 'http://www.oldbrookville.net', (40.8278824094, -73.6153102836)],
['Village of Oyster Bay Cove', '', 'http://www.oysterbaycove.net/', (40.8717717014, -73.530418766)],
['Village of Sea Cliff', '', 'http://www.seacliff-ny.gov', (40.8493464304, -73.6476203581)],
['Village of Upper Brookville', '', 'http://www.upperbrookville.org', (40.8594550096, -73.5063150786)],
['Town of Oyster Bay', 'http://oysterbaytown.com/departments/human-resources', 'http://www.oysterbaytown.com', (40.8732424986, -73.5319410337)],
['County of Nassau', '', 'http://www.nassaucountyny.gov', (40.7379207812, -73.6398427983)],
['Town of Cambria', '', 'http://www.townofcambria.com', (43.1640264425, -78.8188710451)],
['Village of Middleport', '', 'http://villageofmiddleport.org/', (43.2121577079, -78.476738889)],
['Town of Hartland', '', 'http://townofhartland.org/', (43.2420914911, -78.5327258015)],
['Village of Lewiston', '', 'http://www.villageoflewiston.net/', (43.1740893318, -79.0450002357)],
['Town of Lewiston', '', 'http://www.townoflewiston.us/', (43.1794827167, -78.9844651237)],
['Town of Lockport', '', 'http://elockport.com/town-index.php', (43.1316137203, -78.6771089047)],
['Town of Newfane', '', 'http://www.olcott-newfane.com', (43.275963832, -78.6969059854)],
['Town of Niagara', '', 'http://www.townofniagara.com', (43.1217154166, -78.9843049491)],
['Town of Pendleton', '', 'http://www.pendletonny.us', (43.108716894, -78.7738978018)],
['Village of Youngstown', '', 'http://youngstownnewyork.us/', (43.2507448418, -79.0468322824)],
['Town of Porter', '', 'http://www.townofporter.net', (43.2575914875, -79.0085567319)],
['Town of Royalton', '', 'http://www.townofroyalton.org', (43.1617537932, -78.5391888411)],
['Village of Barker', '', 'http://villageofbarker.org/content', (43.3298469495, -78.5531334257)],
['Town of Somerset', '', 'http://www.somersetny.org', (43.3369966785, -78.550125081)],
['Town of Wheatfield', '', 'http://www.wheatfield.ny.us', (43.0859619114, -78.8936704048)],
['Village of Wilson', '', 'http://villageofwilson.org/', (43.3073230111, -78.8264346036)],
['Town of Wilson', '', 'http://www.wilsonnewyork.com', (43.3073230111, -78.8264346036)],
['County of Niagara', 'http://www.niagaracounty.com/departments/civilservice.aspx', 'http://www.niagaracounty.com', (43.1691840351, -78.6990601492)],
['Town of Annsville', '', 'http://townofannsville.org', (43.2934877083, -75.6103137385)],
['Village of Oriskany Falls', '', 'http://villageoforiskanyfalls.org/', (42.9401713663, -75.4605279728)],
['Town of Augusta', '', '', (42.9400742679, -75.4597494961)],
['Town of Ava', '', 'http://townofava.org', (43.4162703996, -75.4805978208)],
['Village of Boonville', '', 'http://village.boonville.ny.us', (43.4759815542, -75.3159845526)],
['Town of Boonville', '', 'http://townofboonville.org/', (43.4759815542, -75.3159845526)],
['Village of Bridgewater', '', 'http://villageofbridgewater.org', (42.8782299764, -75.2511500707)],
['Town of Bridgewater', '', 'http://townofbridgewaterny.org/', (42.8782299764, -75.2511500707)],
['Village of Camden', '', 'http://www.camdenny.com', (43.3360508112, -75.7461276683)],
['Town of Camden', '', 'http://www.camdenny.com', (43.3362719154, -75.7466426331)],
['Town of Deerfield', '', 'http://www.townofdeerfield.org', (43.1670441245, -75.1462688766)],
['Town of Florence', '', '', (43.3468499283, -75.8840249866)],
['Town of Floyd', '', 'http://town.floyd.ny.us', (43.2215612891, -75.336478035)],
['Town of Forestport', '', 'http://www.townofforestport.org', (43.434063891, -75.1981311763)],
['Village of Clinton', '', 'http://village.clinton.ny.us/', (43.0418949594, -75.3803200049)],
['Town of Kirkland', '', 'http://townofkirkland.org', (43.0418949594, -75.3803200049)],
['Town of Lee', '', 'http://townofleeny.org', (43.3017223262, -75.5028065145)],
['Town of Marcy', '', 'http://www.townofmarcy.org', (43.1571912864, -75.2846479915)],
['Village of Waterville', '', 'http://www.watervilleny.com/vilofwaterville.htm', (42.9299088831, -75.3773039014)],
['Town of Marshall', '', 'http://townofmarshall.com', (42.9922881016, -75.4295335832)],
['Village of New Hartford', '', 'http://www.villageofnewhartford.com', (43.0733713082, -75.2886280627)],
['Village of New York Mills', '', 'http://nymills.com/', (43.1035720665, -75.2928887237)],
['Town of New Hartford', '', 'http://www.newhartfordtown.com', (43.0733713082, -75.2886280627)],
['Village of Clayville', '', '', (42.9778599019, -75.2489510087)],
['Town of Paris', '', 'http://town.paris.ny.us/', (43.0002599699, -75.2678050686)],
['Town of Remsen', '', 'http://town.remsen.ny.us/', (43.3345749538, -75.1888130265)],
['Town of Sangerfield', '', 'http://www.sangerfieldny.com', (42.9328542436, -75.3752096598)],
['Town of Steuben', '', 'http://www.town.steuben.ny.us', (43.3493149708, -75.1904850787)],
['Village of Barneveld', '', 'http://villageofbarneveld.org/', (43.2371299525, -75.1647700247)],
['Village of Holland Patent', '', 'http://village.holland-patent.ny.us/', (43.2771349672, -75.2867400706)],
['Village of Prospect', '', 'http://villageofprospect.org/', (43.3028700024, -75.1532500221)],
['Town of Trenton', '', 'http://www.town.trenton.ny.us', (43.2371299525, -75.1647700247)],
['Village of Oneida Castle', '', '', (43.0805612901, -75.6374079029)],
['Village of Vernon', '', 'http://www.villageofvernonny.org/', (43.0882349187, -75.5124650201)],
['Town of Vernon', '', 'http://www.townofvernon.com', (43.0882349187, -75.5124650201)],
['Town of Verona', '', 'http://townverona.org', (43.1712013288, -75.6479794269)],
['Village of Sylvan Beach', '', 'http://villageofsylvanbeach.org/', (43.2094424498, -75.7200197438)],
['Town of Vienna', '', 'http://www.townofvienna.ny.gov', (43.2296149358, -75.7494950543)],
['Town of Western', '', 'http://townofwestern-ny.org', (43.3535049926, -75.3396050102)],
['Town of Westmoreland', '', 'http://www.town.westmoreland.ny.us', (43.1170659561, -75.400580079)],
['Village of Oriskany', '', 'http://villageoforiskany.org/', (43.1578312621, -75.3331080152)],
['Village of Whitesboro', '', 'http://www.village.whitesboro.ny.us', (43.1248212852, -75.2946480534)],
['Village of Yorkville', '', 'http://villageofyorkvilleny.org/', (43.1116516893, -75.2786318818)],
['Town of Whitestown', '', 'http://www.town.whitestown.ny.us', (43.1061759329, -75.322202118)],
['County of Oneida', 'http://ocgov.net/personnel', 'http://www.ocgov.net/', (43.098943097, -75.2294480167)],
['Village of Camillus', '', 'http://villageofcamillus-ny.gov', (43.0388848488, -76.3088317489)],
['Town of Camillus', '', 'http://townofcamillus.com', (43.0455713598, -76.248657635)],
['Village of North Syracuse', '', 'http://www.northsyracuse.org', (43.132494313, -76.1280154253)],
['Town of Cicero', '', 'http://ciceronewyork.net', (43.1692813081, -76.1150276585)],
['Town of Clay', '', 'http://www.townofclay.org', (43.1862998865, -76.2124651698)],
['Village of East Syracuse', '', 'http://www.villageofeastsyracuse.com', (43.0647013456, -76.0705476422)],
['Town of Dewitt', '', 'http://www.townofdewitt.com', (43.0459554454, -76.0504756308)],
['Village of Elbridge', '', 'http://www.villageofelbridge.com', (43.0345613537, -76.4523075852)],
['Village of Jordan', '', 'http://www.villageofjordan.org', (43.0656713492, -76.4721775498)],
['Town of Elbridge', '', 'http://www.townofelbridge.com', (43.1147299866, -76.5078499362)],
['Village of Fabius', '', '', (42.842504906, -75.9745299163)],
['Town of Fabius', '', 'http://www.fabius-ny.gov', (42.8745259312, -75.9865440024)],
['Village of Solvay', '', 'http://villageofsolvay.com', (43.0610043153, -76.2128751725)],
['Town of Geddes', '', 'http://www.townofgeddes.com', (43.060297426, -76.2127475561)],
['Town of LaFayette', '', 'http://www.townoflafayette.com', (42.8969549777, -76.106824493)],
['Village of Baldwinsville', '', 'http://www.baldwinsville.org', (43.1590313681, -76.3339076199)],
['Town of Lysander', '', 'http://townoflysander.org', (43.1715949056, -76.302700533)],
['Village of Fayetteville', '', 'http://www.fayettevilleny.com', (43.0302713385, -76.0053077446)],
['Village of Manlius', '', 'http://www.villageofmanlius.org', (43.0024999063, -75.977759983)],
['Village of Minoa', '', 'http://www.villageofminoa.com', (43.080061464, -75.9979769168)],
['Town of Manlius', '', 'http://www.townofmanlius.org', (43.0320713472, -76.0128477025)],
['Village of Marcellus', '', 'http://villageofmarcellus.com', (42.9828113923, -76.3413976149)],
['Town of Marcellus', '', 'http://www.marcellusny.com', (42.9816513954, -76.3394075823)],
['Town of Onondaga', '', 'http://www.townofonondagany.com/', (43.0174113213, -76.1957876316)],
['Town of Otisco', '', '', (42.8824913392, -76.2347176089)],
['Town of Pompey', '', 'http://townofpompey.com', (42.9232129428, -75.9494660134)],
['Village of Liverpool', '', 'http://www.villageofliverpool.org', (43.1042313367, -76.2091876456)],
['Town of Salina', '', 'http://www.salina.ny.us', (43.0875713364, -76.1838376326)],
['Village of Skaneateles', '', 'http://www.villageofskaneateles.com', (42.9453613504, -76.4277675278)],
['Town of Skaneateles', '', 'http://www.townofskaneateles.com', (42.9468613585, -76.4289275342)],
['Town of Spafford', '', 'http://www.townofspafford.com', (42.8688824193, -76.3386669043)],
['Village of Tully', '', 'http://www.tullyny.org', (42.7912658664, -76.1160651335)],
['Town of Tully', '', 'http://townoftully.org', (42.7912658664, -76.1160651335)],
['Town of Van Buren', '', 'http://www.townofvanburen.com', (43.1368513325, -76.3230075441)],
['County of Onondaga', 'http://www.ongov.net/employment/civilservice.html', 'http://www.ongov.net', (43.0464711154, -76.1487290419)],
['Town of Bristol', '', 'http://www.townofbristol.org', (42.8093944403, -77.3932537213)],
['Town of Canadice', '', 'http://www.canadice.org', (42.673928094, -77.5693429884)],
['Town of Canandaigua', '', 'http://www.townofcanandaigua.org', (42.8455649254, -77.3076599588)],
['Village of Bloomfield', '', 'http://www.bloomfieldny.org', (42.9017374252, -77.4210885105)],
['Town of East Bloomfield', '', 'http://www.townofeastbloomfield.com', (42.898114949, -77.4319357292)],
['Town of Farmington', '', 'http://www.townoffarmingtonny.com', (42.9905132961, -77.3262965098)],
['Town of Geneva', '', 'http://www.townofgeneva.com', (42.759144915, -77.0847899919)],
['Village of Rushville', '', 'http://villageofrushville.com', (42.7602684112, -77.226362979)],
['Town of Gorham', '', 'http://www.gorham-ny.com', (42.7986949278, -77.1321599597)],
['Town of Hopewell', '', 'http://www.townofhopewell.org', (42.9001787203, -77.1842066602)],
['Village of Clifton Springs', '', 'http://cliftonspringsny.org', (42.9612673731, -77.1384079361)],
['Village of Manchester', '', 'http://www.villageofmanchester.org', (42.9686372037, -77.2335205985)],
['Village of Shortsville', '', 'http://www.villageofshortsvilleny.us', (42.9740099893, -77.2823849252)],
['Town of Manchester', '', 'http://manchesterny.org', (42.958414963, -77.1445899627)],
['Village of Naples', '', '', (42.6149974832, -77.4024553893)],
['Town of Naples', '', 'http://www.naplesny.us', (42.6596900205, -77.4949499176)],
['Village of Phelps', '', 'http://www.phelpsny.com/community/village/', (42.9575110384, -77.0571978988)],
['Town of Phelps', '', 'http://www.phelpsny.com/community/town/', (42.9573000068, -77.0572958575)],
['Town of Richmond', '', 'http://townofrichmond.org/', (42.7442350184, -77.5043829605)],
['Town of Seneca', '', 'http://www.townofseneca.com', (42.7583549061, -77.1470349138)],
['Town of South Bristol', '', 'http://www.southbristolny.org', (42.6596900205, -77.4949499176)],
['Village of Victor', '', 'http://www.victorny.org/index.aspx?NID=92', (42.9825531776, -77.4100291523)],
['Town of Victor', '', 'http://www.victorny.org/index.aspx?NID=27', (42.9823670925, -77.4077468063)],
['Town of West Bloomfield', '', 'http://townofwestbloomfield.org', (42.9018616857, -77.5390679245)],
['County of Ontario', 'http://www.co.ontario.ny.us/jobs.aspx', 'http://www.co.ontario.ny.us', (42.8887393265, -77.2803893571)],
['Village of South Blooming Grove', '', 'http://villageofsouthbloominggrove.com/1.html', (41.3680677233, -74.1890270054)],
['Village of Washingtonville', '', 'http://www.washingtonville-ny.gov', (41.4265443869, -74.1687175392)],
['Town of Blooming Grove', '', 'http://www.townofbloominggroveny.com', (41.4081100631, -74.1922491201)],
['Village of Chester', '', 'http://www.villageofchester.com', (41.3619278123, -74.2724851876)],
['Town of Chester', '', 'http://thetownofchester.org', (41.3398490744, -74.2755453151)],
['Village of Cornwall-on-Hudson', '', 'http://www.cornwall-on-hudson.org', (41.4452431202, -74.015311027)],
['Town of Cornwall', '', 'http://www.cornwallny.gov', (41.4389486333, -74.0282085873)],
['Town of Crawford', '', 'http://townofcrawford.org/Home.aspx', (41.6226450428, -74.3996300084)],
['Town of Deerpark', '', 'http://www.townofdeerpark.org', (41.4429950825, -74.6524650841)],
['Village of Goshen', '', 'http://www.villageofgoshen-ny.gov', (41.4055074323, -74.317130571)],
['Town of Goshen', '', 'http://www.townofgoshen.org', (41.4028645865, -74.3237681734)],
['Town of Greenville', '', 'http://www.townofgreenvilleny.com', (42.4542350944, -74.0298050163)],
['Village of Maybrook', '', 'http://www.villageofmaybrook.com', (41.4908353279, -74.2098191419)],
['Town of Hamptonburgh', '', 'http://townofhamptonburgh.org', (41.4571660257, -74.2721050926)],
['Village of Highland Falls', '', 'http://www.highlandfallsny.org', (41.3705692222, -73.9653983934)],
['Town of Highlands', '', 'http://www.highlands-ny.gov', (41.3693820754, -73.9658446834)],
['Village of Unionville', '', 'http://www.unionvilleny.org', (41.3015600115, -74.5620600563)],
['Town of Minisink', '', 'http://www.townofminisink.com', (41.3316950895, -74.5426850568)],
['Village of Harriman', '', 'http://www.orangecountygov.com/content/124/1362/1460/10182/10438/10684.aspx', (41.3042700361, -74.1458450506)],
['Village of Kiryas Joel', '', 'http://www.orangecountygov.com/content/124/1362/1460/10182/10438/10684.aspx', (41.3172100848, -74.1998650868)],
['Village of Monroe', '', 'http://www.villageofmonroe.org', (41.3280941477, -74.1873298715)],
['Town of Monroe', 'https://www.monroeny.org/doc-center/town-of-monroe-job-opportunities.html', 'http://www.monroeny.org', (41.3282354283, -74.1871966569)],
['Village of Montgomery', '', 'http://www.villageofmontgomery.org/index.php/links.html', (41.526206766, -74.2367095838)],
['Village of Walden', '', 'http://www.villageofwalden.org', (41.5655900799, -74.1735051021)],
['Town of Montgomery', '', 'http://www.townofmontgomery.com', (41.5221628037, -74.1992864829)],
['Village of Otisville', '', 'http://www.villageofotisville.com', (41.4667640805, -74.5384714061)],
['Town of Mount Hope', '', 'http://townofmounthope.org', (41.467690033, -74.5390400543)],
['Town of Newburgh', '', 'http://townofnewburgh.org', (41.5322430845, -74.0632817699)],
['Town of New Windsor', '', 'http://www.town.new-windsor.ny.us', (41.483006661, -74.0622960302)],
['Village of Tuxedo Park', '', 'http://www.tuxedopark-ny.gov', (41.2123131188, -74.1993468712)],
['Town of Tuxedo', '', 'http://www.tuxedogov.org', (41.2055650941, -74.2254500514)],
['Town of Wallkill', 'http://www.townofwallkill.com/index.php/departments/human-resources', 'http://www.townofwallkill.com', (41.4669643847, -74.3749822178)],
['Village of Florida', '', 'http://villageoffloridany.org', (41.3335960249, -74.3575568847)],
['Village of Greenwood Lake', '', 'http://www.villageofgreenwoodlake.org', (41.2211170211, -74.2914580488)],
['Village of Warwick', '', 'http://www.villageofwarwick.org', (41.2584108073, -74.3583920644)],
['Town of Warwick', '', 'http://www.townofwarwick.org/', (41.2576325245, -74.3588055956)],
['Town of Wawayanda', '', 'http://www.townofwawayanda.com', (41.3848150024, -74.474500046)],
['Village of Woodbury', '', 'http://villageofwoodbury.com/home', (41.3666250583, -74.0923900338)],
['Town of Woodbury', '', 'http://www.townofwoodbury.com', (41.3471740713, -74.1264622829)],
['County of Orange', '', 'http://www.co.orange.ny.us', (41.4052285038, -74.3184049043)],
['Village of Albion', '', 'http://www.vil.albion.ny.us', (43.2479351017, -78.1931631342)],
['Town of Albion', '', 'http://www.townofalbion.com', (43.2386624955, -78.178039816)],
['Town of Barre', '', 'http://www.townofbarreny.com', (43.1732861559, -78.1978115329)],
['Town of Carlton', '', 'http://www.townofcarlton.com', (43.3232618885, -78.1925113059)],
['Town of Clarendon', '', 'http://www.townofclarendon.org', (43.1914938327, -78.0596794975)],
['Town of Gaines', '', 'http://www.townofgaines.org', (43.2328749797, -78.2127899127)],
['Town of Kendall', '', 'http://www.townofkendall.com', (43.3464891453, -78.0560084465)],
['Village of Holley', '', 'http://www.villageofholley.org', (43.2252205431, -78.0250840456)],
['Town of Murray', '', 'http://www.townofmurray.org', (43.2447949923, -78.0909529909)],
['Village of Medina', '', 'http://villagemedina.org/', (43.2189100305, -78.3874062654)],
['Town of Ridgeway', '', 'http://www.townridgeway.org', (43.2213272569, -78.3898839449)],
['Town of Shelby', '', 'http://www.townofshelbyny.org', (43.2146713351, -78.4113624799)],
['Village of Lyndonville', '', '', (43.3211861502, -78.3890092326)],
['Town of Yates', '', 'http://townofyates.org', (43.3210820288, -78.3890378689)],
['County of Orleans', 'http://www.orleansny.com/departments/operations/personnel.aspx', 'http://www.orleansny.com', (43.2455918571, -78.1930056819)],
['Town of Albion', '', 'http://www.townofalbion-ny.us', (43.2386624955, -78.178039816)],
['Town of Amboy', '', 'http://www.townofamboy-ny.us', (43.3952799615, -75.936684916)],
['Town of Boylston', '', '', (43.6568293951, -75.9946213427)],
['Village of Cleveland', '', 'http://www.norcog.org/cleveland/', (43.2742749782, -75.8868598981)],
['Town of Constantia', '', 'http://www.townconstantia.org', (43.2492940616, -76.0017558737)],
['Town of Granby', '', 'http://www.towngranby.org', (43.2849518821, -76.4634187768)],
['Village of Hannibal', '', '', (43.3168429118, -76.5744139285)],
['Town of Hannibal', '', 'http://hannibalny.org', (43.3134449267, -76.5498799814)],
['Village of Central Square', '', 'http://www.villageofcentralsquare-ny.us', (43.2845085909, -76.1370902254)],
['Town of Hastings', '', 'http://www.hastingsny.org', (43.2587099244, -76.2092949447)],
['Village of Mexico', '', 'http://mexicovillage.net', (43.4599424769, -76.2272480481)],
['Town of Mexico', '', 'http://town.mexicony.net', (43.4546109379, -76.229080875)],
['Town of Minetto', '', 'http://www.townofminetto.net', (43.3969786598, -76.4729236997)],
['Town of New Haven', '', 'http://newhavenny.com', (43.4796658453, -76.3172680457)],
['Town of Orwell', '', 'http://www.townoforwell-ny.us', (43.5745266766, -75.9962528496)],
['Town of Oswego', '', 'http://www.townofoswego.com', (43.4154167336, -76.5332370747)],
['Town of Palermo', '', 'http://www.townofpalermo.com/', (43.3954488568, -76.3090797422)],
['Village of Parish', '', 'http://www.villageofparish-ny.us', (43.4062950752, -76.1244968379)],
['Town of Parish', '', 'http://www.townofparish-ny.us/index.shtml', (43.4062950752, -76.1244968379)],
['Town of Redfield', '', '', (43.5299776853, -75.8194859508)],
['Village of Pulaski', '', 'http://www.villagepulaski.org', (43.5701167412, -76.1254029131)],
['Town of Richland', '', 'http://www.townofrichland.org', (43.5656609281, -76.1290299128)],
['Village of Lacona', '', '', (43.6418579007, -76.0704469291)],
['Village of Sandy Creek', '', '', (43.6412078354, -76.0864284793)],
['Town of Sandy Creek', '', 'http://www.sandycreekny.us', (43.643944393, -76.0782035222)],
['Village of Phoenix', '', 'http://villageofphoenix-ny.gov', (43.2292966204, -76.2990427303)],
['Town of Schroeppel', '', 'http://www.townofschroeppel.com', (43.223145975, -76.2840910614)],
['Town of Scriba', '', 'http://scribany.org/home.html', (43.4682313439, -76.4298529675)],
['Town of Volney', '', 'http://www.townofvolney.com', (43.3421817327, -76.3585668303)],
['Town of West Monroe', '', 'http://www.townofwestmonroe-ny.us', (43.284063184, -76.0650874017)],
['Town of Williamstown', '', '', (43.4249214833, -75.889074291)],
['County of Oswego', '', 'http://www.oswegocounty.com/rpts.shtml', (43.4576318017, -76.5061447062)],
['Town of Burlington', '', 'http://www.townofburlingtonny.com', (42.7456792033, -75.1831343805)],
['Village of Gilbertsville', '', 'http://www.gilbertsville.com', (42.4404550772, -75.3648950344)],
['Town of Butternuts', '', 'http://www.gilbertsville.com/butternuts/offices.htm', (42.4230870607, -75.3690399897)],
['Village of Cherry Valley', '', 'http://cherryvalleyny.us', (42.7969819495, -74.7542270831)],
['Town of Cherry Valley', '', 'http://cherryvalleyny.us', (42.8632199399, -74.7526350355)],
['Town of Decatur', '', '', (42.6101200893, -74.7274300436)],
['Town of Edmeston', '', 'http://www.edmestonny.org', (42.6979614678, -75.2442780544)],
['Town of Exeter', '', '', (42.8481799361, -75.2723750588)],
['Town of Hartwick', '', 'http://www.townofhartwick.org', (42.6600291528, -75.0440912484)],
['Village of Laurens', '', '', (42.5490450478, -75.1433250373)],
['Town of Laurens', '', '', (42.5490450478, -75.1433250373)],
['Town of Maryland', '', 'http://www.marylandny.com/', (42.5475126752, -74.8291441664)],
['Village of Cooperstown', '', 'http://www.cooperstownny.org', (42.7001796838, -74.9226674811)],
['Town of Middlefield', '', 'http://www.middlefieldny.com', (42.719310039, -74.9029500189)],
['Village of Milford', '', '', (42.5891563398, -74.9462510356)],
['Town of Milford', '', 'http://townofmilford.org', (42.5378850408, -74.9674500615)],
['Village of Morris', '', '', (42.5497898193, -75.2405564403)],
['Town of Morris', '', '', (42.5266100303, -75.2587100462)],
['Town of New Lisbon', '', 'http://townofnewlisbon.com', (42.6491900303, -75.1862550857)],
['Town of Oneonta', '', 'http://www.townofoneonta.org', (42.4703715126, -75.112138174)],
['Village of Otego', '', '', (42.3967615328, -75.1784581554)],
['Town of Otego', '', 'http://townofotego.com', (42.372535044, -75.2057300047)],
['Town of Otsego', '', 'http://townofotsego.com', (42.7240002579, -74.9805190359)],
['Town of Pittsfield', '', '', (42.6022050317, -75.3575400824)],
['Town of Plainfield', '', 'http://townofplainfieldny.org/', (42.835891574, -75.1943032525)],
['Village of Richfield Springs', '', 'http://www.villageofrichfieldsprings-ny.com', (42.8538216724, -74.9882603486)],
['Town of Richfield', '', '', (42.8311549615, -75.0218850298)],
['Town of Roseboom', '', 'http://www.townofroseboom.com', (42.8632199399, -74.7526350355)],
['Town of Springfield', '', '', (42.829534506, -74.8742835842)],
['Village of Unadilla', '', '', (42.2929050661, -75.3172400242)],
['Town of Unadilla', '', '', (42.3313658619, -75.2988479864)],
['Town of Westford', '', 'http://www.westfordny.com', (42.5862400355, -74.836295073)],
['Town of Worcester', '', 'http://www.townofworcesterny.com', (42.5923860965, -74.7513485488)],
['County of Otsego', 'http://www.otsegocounty.com/depts/per', 'http://www.otsegocounty.com', (42.7010696557, -74.9303678868)],
['Town of Carmel', '', 'http://www.carmelny.org', (41.3812450326, -73.7523200503)],
['Town of Kent', '', 'http://www.townofkentny.gov/', (41.479231507, -73.6697730666)],
['Town of Patterson', '', 'http://www.pattersonny.org/', (41.5138545308, -73.6046303818)],
['Village of Cold Spring', '', 'http://users.bestweb.net/~vcsclerk/', (41.4178516519, -73.9579185307)],
['Village of Nelsonville', '', 'http://www.villageofnelsonville.org', (41.4239416327, -73.9487985904)],
['Town of Philipstown', '', 'http://www.philipstown.com', (41.4229216381, -73.9508285691)],
['Town of Putnam Valley', '', 'http://www.putnamvalley.com', (41.3675016789, -73.8669986181)],
['Village of Brewster', '', 'http://www.brewstervillage-ny.gov/', (41.3952915971, -73.6070186469)],
['Town of Southeast', '', 'http://www.southeast-ny.gov', (41.3944116555, -73.6193986956)],
['County of Putnam', '', 'http://www.putnamcountyny.gov', (41.4262934574, -73.6788680935)],
['Town of Berlin', '', 'http://berlin-ny.us/', (42.6795750816, -73.3310850431)],
['Town of Brunswick', '', 'http://www.townofbrunswick.org', (42.7379805481, -73.6080992528)],
['Town of East Greenbush', '', 'http://www.eastgreenbush.org', (42.617351421, -73.7312185505)],
['Town of Grafton', '', 'http://www.townofgraftonny.org', (42.7694499754, -73.4498250199)],
['Village of Hoosick Falls', '', 'http://www.hoosickfalls.com/', (42.9008212828, -73.3502687224)],
['Town of Hoosick', '', 'http://townofhoosick.org', (42.8622899602, -73.3275999961)],
['Village of East Nassau', '', 'http://villageofeastnassau.org/', (42.53216006, -73.5095000814)],
['Village of Nassau', '', 'http://www.villageofnassau.org/', (42.512811439, -73.6094286195)],
['Town of Nassau', '', 'http://townofnassau.org/', (42.5156214459, -73.6077685901)],
['Town of North Greenbush', '', 'http://www.townofng.com', (42.6957109978, -73.6398811165)],
['Town of Petersburgh', '', 'http://www.petersburgh.org', (42.7504284906, -73.3422351019)],
['Village of Valley Falls', '', 'http://www.ercswma.org/valley-falls', (42.9006612594, -73.562458625)],
['Town of Pittstown', '', 'http://pittstown.us', (42.8813349595, -73.5539000518)],
['Town of Poestenkill', '', 'http://www.poestenkillny.com', (42.6904413709, -73.5635585828)],
['Town of Sand Lake', '', 'http://www.townofsandlake.us', (42.6383013238, -73.5416386167)],
['Village of Schaghticoke', '', '', (42.8942472035, -73.5871434082)],
['Town of Schaghticoke', '', 'http://www.townofschaghticoke.org', (42.8517725911, -73.6060343706)],
['Village of Castleton-on-Hudson', '', 'http://www.castleton-on-hudson.org', (42.5292897268, -73.7574740364)],
['Town of Schodack', '', 'http://www.schodack.org', (42.5528178725, -73.674625272)],
['Town of Stephentown', '', 'http://www.townofstephentown.org', (42.5636950091, -73.3743000471)],
['County of Rensselaer', 'http://www.rensco.com/county-job-assistance', 'http://www.rensco.com', (42.7541999492, -73.5888500074)],
['Village of Nyack', '', 'http://www.nyack.org/', (41.0913916648, -73.9178886251)],
['Village of Spring Valley', '', 'http://www.villagespringvalley.org/', (41.1220317253, -74.0406685883)],
['Village of Upper Nyack', '', 'http://uppernyack-ny.us/', (41.1012319466, -73.9172493327)],
['Town of Clarkstown', '', 'http://www.town.clarkstown.ny.us', (41.1465816927, -73.9878086252)],
['Village of Haverstraw', '', 'http://www.voh-ny.com', (41.1963806918, -73.9667884742)],
['Village of Pomona', '', 'http://www.pomonavillage.com', (41.1826116961, -74.0550185985)],
['Village of West Haverstraw', '', 'http://westhaverstraw.wordpress.com/', (41.2031863712, -73.9731414396)],
['Town of Haverstraw', '', 'http://www.townofhaverstraw.us', (41.202575014, -74.0009400245)],
['Village of Grand View-on-Hudson', '', 'http://www.gvoh.net/', (41.066531708, -73.9204786123)],
['Village of Piermont', '', 'http://piermont-ny.gov/', (41.0403317502, -73.9165685798)],
['Village of South Nyack', '', 'http://southnyack.ny.gov/', (41.0812603832, -73.9206675582)],
['Town of Orangetown', 'https://www.orangetown.com/groups/department/personnel', 'http://www.orangetown.com', (41.0466917982, -73.9559522634)],
['Village of Airmont', '', 'http://www.airmont.org/', (41.1106650191, -74.0987350691)],
['Village of Chestnut Ridge', '', 'http://www.chestnutridgevillage.org/', (41.1014562262, -74.0446202967)],
['Village of Hillburn', '', 'http://www.hillburn.org', (41.1238867326, -74.1695019079)],
['Village of Kaser', '', '', (41.1147317018, -74.0706085104)],
['Village of Montebello', '', 'http://www.villageofmontebello.com/', (41.1192216894, -74.1102084968)],
['Village of New Hempstead', 'http://villageofhempstead.org/197/employment-opportunities', 'http://www.villageofhempstead.org/', (41.1466095989, -73.9847718229)],
['Village of New Square', '', '', (41.1418090765, -74.0348498425)],
['Village of Sloatsburg', '', 'http://www.sloatsburgny.com', (41.1577816686, -74.1920185207)],
['Village of Suffern', '', 'http://www.suffernvillage.com/', (41.1140716957, -74.1501885251)],
['Village of Wesley Hills', '', 'http://www.wesleyhills.org/', (41.1541261502, -74.0700849628)],
['Town of Ramapo', 'http://www.ramapo.org/page/personnel-30.html?_sm_au_=ivvt78qz5w7p2qhf', 'http://www.ramapo.org', (41.1318850055, -74.1089150403)],
['Town of Stony Point', '', 'http://www.townofstonypoint.org/', (41.2283416684, -73.984728548)],
['County of Rockland', 'http://rocklandgov.com/departments/personnel/job-opportunities/', 'http://rocklandgov.com', (41.148085745, -73.9903114639)],
['Village of Ballston Spa', '', 'http://www.saratoga.org/community/towns-cities/village-of-ballston-spa', (43.0025696294, -73.8511244599)],
['Town of Ballston', '', 'http://www.townofballstonny.org', (42.9509893099, -73.9052059994)],
['Town of Charlton', '', 'http://www.townofcharlton.org', (42.9345214477, -73.9631648669)],
['Town of Clifton Park', 'http://www.cliftonpark.org/services/employment-applications.html', 'http://www.cliftonpark.org', (42.8520949951, -73.7873100606)],
['Town of Corinth', '', 'http://townofcorinthny.org', (43.2460978083, -73.8152335318)],
['Town of Day', '', 'http://www.townofday.com', (43.3047520669, -74.0178946481)],
['Town of Edinburg', '', 'http://www.edinburgny.com', (43.2216301694, -74.103675529)],
['Village of Galway', '', '', (43.0185249622, -74.0315609556)],
['Town of Galway', '', 'http://www.townofgalway.org', (43.0469249493, -74.0423300328)],
['Town of Greenfield', '', 'http://greenfieldny.org/', (43.1282640867, -73.8457935198)],
['Town of Hadley', '', 'http://www.townofhadley.org', (43.3231749894, -74.0055050183)],
['Town of Halfmoon', '', 'http://www.townofhalfmoon.org', (42.8538289634, -73.7254720147)],
['Village of Round Lake', '', 'http://www.roundlakevillage.org', (42.9367570025, -73.7949053064)],
['Town of Malta', '', 'http://www.malta-town.org', (42.9755809676, -73.7911673553)],
['Town of Milton', '', 'http://www.townofmiltonny.org', (43.044858951, -73.8526866303)],
['Village of South Glens Falls', '', 'http://www.sgfny.com/', (43.2855699699, -73.6385150519)],
['Town of Moreau', '', 'http://www.townofmoreau.org', (43.2526791279, -73.6555730577)],
['Town of Northumberland', '', 'http://www.townofnorthumberland.org', (43.1979499061, -73.6832000692)],
['Town of Providence', '', 'http://townofprovidence.org/', (43.0469249493, -74.0423300328)],
['Village of Schuylerville', '', 'http://villageofschuylerville.org/', (43.1042449706, -73.5832180518)],
['Village of Victory', '', 'http://www.villageofvictory.org', (43.0879849392, -73.5937700925)],
['Town of Saratoga', '', 'http://www.townofsaratoga.com', (43.0998724604, -73.5796870902)],
['Village of Stillwater', '', 'http://www.stillwaterny.org/', (42.9987899531, -73.6628200392)],
['Town of Stillwater', '', 'http://stillwaterny.org/', (42.9987899531, -73.6628200392)],
['Village of Waterford', '', 'http://www.waterfordny.org', (42.8113056106, -73.6999601388)],
['Town of Waterford', '', 'http://www.town.waterford.ny.us', (42.790442278, -73.6784862383)],
['Town of Wilton', '', 'http://www.townofwilton.com', (43.1677853699, -73.7171195879)],
['County of Saratoga', 'http://www.saratogacountyny.gov/departments/personnel', 'http://www.saratogacountyny.gov', (42.9988150876, -73.8510778967)],
['Village of Delanson', '', 'http://www.delanson.net', (42.8290600004, -74.2497550275)],
['Town of Duanesburg', '', 'http://www.duanesburg.net', (42.765322018, -74.1468943128)],
['Village of Scotia', '', 'http://www.villageofscotia.org/', (42.8265969702, -73.9642569322)],
['Town of Glenville', '', 'http://www.townofglenville.org', (42.8681788917, -73.9273192032)],
['Town of Niskayuna', '', 'http://www.niskayuna.org', (42.805724958, -73.8744000943)],
['Town of Princetown', '', 'http://princetown.net', (42.7805813288, -74.0333884519)],
['Town of Rotterdam', '', 'http://www.rotterdamny.org', (42.8073549345, -74.0356150187)],
['County of Schenectady', 'https://mycivilservice.schenectadycounty.com', 'http://www.schenectadycounty.com', (42.8101512775, -73.939488482)],
['Town of Blenheim', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/townble/index.jsp', (42.4694796797, -74.4464674561)],
['Town of Broome', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/townbro/index.jsp', (42.5456900963, -74.3223650592)],
['Town of Carlisle', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/towncar/index.jsp', (42.7713999655, -74.4776500785)],
['Village of Cobleskill', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/villcob/', (42.6688214504, -74.4806582879)],
['Town of Cobleskill', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/towncob/index.jsp', (42.6807602329, -74.4167902591)],
['Town of Conesville', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/towncon/index.jsp', (42.3852743128, -74.3786540671)],
['Village of Esperance', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/villesp/index.jsp', (42.7618389671, -74.2604600106)],
['Town of Esperance', '', 'http://www.townofesperance.org/', (42.7019900331, -74.380870057)],
['Town of Fulton', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/townful/index.jsp', (42.5388574666, -74.4243936472)],
['Town of Gilboa', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/towngil/index.jsp', (42.3974253929, -74.448485961)],
['Town of Jefferson', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/townjef/index.jsp', (42.480728061, -74.6175480178)],
['Village of Middleburgh', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/villmid/index.jsp', (42.5900014279, -74.3223083845)],
['Town of Middleburgh', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/townmid/index.jsp', (42.5900014279, -74.3223083845)],
['Village of Richmondville', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/villric/index.jsp', (42.6346914376, -74.5628983349)],
['Town of Richmondville', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/townric/index.jsp', (42.6346414566, -74.5581982772)],
['Village of Schoharie', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/villsch/index.jsp', (42.6685514166, -74.309258431)],
['Town of Schoharie', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/townsch/index.jsp', (42.6641814132, -74.3111183911)],
['Town of Seward', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/townsew/index.jsp', (42.6963300931, -74.658965087)],
['Village of Sharon Springs', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/villsha/index.jsp', (42.8022499135, -74.6678500876)],
['Town of Sharon', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/townsha/index.jsp', (42.8022499135, -74.6678500876)],
['Town of Summit', '', 'http://www.schohariecounty-ny.gov/CountyWebSite/townsum/index.jsp', (42.5786914426, -74.5925782617)],
['Town of Wright', '', 'http://www.townofwright.com/', (42.6616491461, -74.2358165922)],
['County of Schoharie', 'http://www.schohariecounty-ny.gov', 'http://www.schohariecounty-ny.gov', (42.6638126019, -74.3120599911)],
['Village of Odessa', '', '', (42.367470077, -76.7718249421)],
['Town of Catharine', '', 'http://www.townofcatharine.com/', (42.3381015542, -76.7703575401)],
['Town of Cayuta', '', 'http://www.townofcayuta.org/', (42.2941216062, -76.7201874954)],
['Village of Montour Falls', '', 'http://villageofmontourfalls.com/', (42.3457315853, -76.8497474501)],
['Village of Watkins Glen', '', 'http://www.watkinsglen.us', (42.3809615816, -76.8741574265)],
['Town of Dix', '', 'http://www.townofdix.com/', (42.3489450276, -76.8336099655)],
['Village of Burdett', '', 'http://burdettny.us/', (42.4189254261, -76.8494904521)],
['Town of Hector', '', 'http://home.htva.net/~townofhector/home.html', (42.4638940003, -76.7761575596)],
['Town of Montour', '', 'http://townofmontour.com/', (42.3489450276, -76.8336099655)],
['Town of Orange', '', 'http://townoforangeny.org/', (42.3043880156, -77.0486149604)],
['Town of Reading', '', 'https://sites.google.com/site/townofreadingschuylercountyny', (42.4437300099, -76.9466049764)],
['Town of Tyrone', '', 'http://townoftyrone.org', (42.4224215636, -77.0784174493)],
['County of Schuyler', 'http://www.schuylercounty.us/index.aspx?nid=119', 'http://www.schuylercounty.us', (42.3772249335, -76.8715050926)],
['Village of Interlaken', '', 'http://www.villageofinterlaken.org/', (42.6186661694, -76.7245753487)],
['Town of Covert', '', 'http://www.townofcovert.org', (42.6138654038, -76.7242557573)],
['Village of Waterloo', '', 'http://www.waterloony.com', (42.9042404801, -76.8650435698)],
['Town of Fayette', '', 'http://www.townoffayetteny.com', (42.8501452512, -76.8682769306)],
['Town of Junius', '', 'http://www.townofjunius.org/', (42.9766440582, -76.9351749236)],
['Village of Lodi', '', '', (42.591235055, -76.8421049158)],
['Town of Lodi', '', 'http://lodiny.com/', (42.615254543, -76.8233278441)],
['Village of Ovid', '', '', (42.6804300365, -76.7995049735)],
['Town of Ovid', '', 'http://www.townofovid.org/', (42.6562040852, -76.8253580024)],
['Town of Romulus', '', 'http://www.romulustown.com/', (42.6834050234, -76.8702199558)],
['Town of Seneca Falls', '', 'http://www.senecafalls.com/', (42.9077257207, -76.8027875275)],
['Town of Tyre', '', 'http://www.tyreny.com/', (42.9679713659, -76.828555158)],
['Town of Varick', '', 'http://www.varickny.com/', (42.7946438774, -76.8438013113)],
['Town of Waterloo', '', 'http://www.townofwaterloo.org/', (42.907547007, -76.8617561853)],
['County of Seneca', '', 'http://www.co.seneca.ny.us', (42.9097847627, -76.8430784072)],
['Village of Addison', '', 'http://www.villageofaddison.info/', (42.1036266507, -77.2375809273)],
['Town of Addison', '', '', (42.1051971048, -77.2344612801)],
['Village of Avoca', '', '', (42.4094142787, -77.4207087427)],
['Town of Avoca', '', '', (42.4235850737, -77.4428249247)],
['Village of Bath', '', 'http://www.villageofbath.org/', (42.3357917422, -77.3177596631)],
['Village of Savona', '', 'http://www.villageofsavona.com/', (42.3176950264, -77.1878349309)],
['Town of Bath', '', 'http://www.townofbathny.org/', (42.3492350755, -77.3425949179)],
['Town of Bradford', '', '', (42.3771650832, -77.12495497)],
['Town of Cameron', '', '', (42.1874350617, -77.3668099826)],
['Town of Campbell', '', 'http://www.campbellny.com/', (42.2401629158, -77.1311949736)],
['Village of Canisteo', '', '', (42.2698069947, -77.6040663359)],
['Town of Canisteo', '', '', (42.2695603097, -77.6052828942)],
['Town of Caton', '', 'http://www.townofcaton.com', (42.1302750887, -77.0356949537)],
['Village of Cohocton', '', 'http://www.cohoctonny.com/', (42.4984363196, -77.4948123252)],
['Town of Cohocton', '', 'http://www.townofcohocton.com/', (42.5003414259, -77.4949525824)],
['Village of Riverside', '', '', (42.1598807199, -77.0831148058)],
['Village of South Corning', '', '', (42.1242826873, -77.0341970302)],
['Town of Corning', '', 'http://www.townofcorningny.org', (42.1219140411, -77.0348307877)],
['Town of Dansville', '', 'http://townofdansvilleny.com', (42.4486757778, -77.6543473225)],
['Village of Painted Post', '', 'http://www.paintedpostny.com/', (42.1607450624, -77.1338899449)],
['Town of Erwin', '', 'http://www.erwinny.org', (42.1607450624, -77.1338899449)],
['Town of Fremont', '', 'http://www.fremontnewyork.us/', (42.3944973631, -77.6270583018)],
['Town of Greenwood', '', 'http://greenwoodny.org/', (42.1563300393, -77.6889199159)],
['Town of Hartsville', '', '', (42.2501224316, -77.6887930122)],
['Town of Hornby', '', '', (42.2337880031, -77.0492278964)],
['Village of Arkport', '', 'http://www.arkportvillage.com/', (42.3925222996, -77.6944192536)],
['Village of North Hornell', '', 'http://www.northhornell.com/', (42.3444570514, -77.6617919075)],
['Town of Hornellsville', '', 'http://www.townofhornellsville.com', (42.3929722826, -77.6953175107)],
['Town of Howard', '', '', (42.4235850737, -77.4428249247)],
['Town of Jasper', '', '', (42.121631601, -77.5037645746)],
['Town of Lindley', '', '', (42.0206800917, -77.1223649441)],
['Town of Prattsburgh', '', '', (0.0, 0.0)],
['Town of Pulteney', '', 'http://www.pulteneyny.com', (42.5248700555, -77.16160993)],
['Town of Rathbone', '', 'http://www.townofrathbone.com', (42.1874350617, -77.3668099826)],
['Town of Thurston', '', 'http://www.townofthurston.com', (42.223053176, -77.2638665454)],
['Town of Troupsburg', '', '', (42.0465250243, -77.5676249882)],
['Town of Tuscarora', '', '', (42.0541454894, -77.2716955076)],
['Village of Hammondsport', '', 'http://www.hammondsport.com/', (42.4078155048, -77.2234664412)],
['Town of Urbana', '', 'http://www.townofurbana.com', (42.3895430343, -77.2596848314)],
['Village of Wayland', '', '', (42.5680950195, -77.5916361949)],
['Town of Wayland', '', 'http://townofwayland.org', (42.5395700563, -77.6281949636)],
['Town of Wayne', '', 'http://www.townofwayneny.com', (42.4671990577, -77.1580389643)],
['Town of West Union', '', '', (42.0432900628, -77.7516849695)],
['Town of Wheeler', '', '', (42.4304566093, -77.3318165818)],
['Town of Woodhull', '', 'http://www.woodhullny.com/', (42.0564350415, -77.4332999743)],
['County of Steuben', 'http://www.steubencony.org/pages.asp?pgid=32', 'http://steubencony.org', (42.3326293563, -77.3174667559)],
['Town of Brasher', '', '', (44.8084826407, -74.7734247823)],
['Village of Canton', '', 'http://www.cantonnewyork.us/government/elected-village/', (44.5951492186, -75.1710957447)],
['Village of Rensselaer Falls', '', 'http://www.cantonnewyork.us/', (44.6195649466, -75.3068200589)],
['Town of Canton', '', 'http://www.cantonnewyork.us', (44.5800399073, -75.1491600139)],
['Town of Clare', '', '', (44.3828199523, -75.0341150071)],
['Town of Clifton', '', 'http://townofcliftonny.org', (44.222988224, -74.8370819722)],
['Town of Colton', '', 'http://www.townofcolton.com', (44.5146099818, -74.9347850096)],
['Village of Richville', '', '', (44.4090799278, -75.3641600699)],
['Town of Dekalb', '', 'http://townofdekalb.org/content', (44.5047529654, -75.2732458263)],
['Town of De Peyster', '', '', (44.4857949536, -75.4881000815)],
['Town of Edwards', '', '', (44.3076149045, -75.2452100785)],
['Town of Fine', '', 'http://www.townoffine.org', (44.1647367012, -75.0459947301)],
['Town of Fowler', '', 'http://www.fowlerny.com/', (44.3095949683, -75.4464100448)],
['Village of Gouverneur', '', 'http://www.villageofgouverneur.org/', (44.3361837338, -75.4699697093)],
['Town of Gouverneur', '', 'http://gouverneurny.com', (44.19434993, -75.5312700317)],
['Village of Hammond', '', '', (44.3479849025, -75.7748100594)],
['Town of Hammond', '', 'http://townofhammondny.com', (44.4495407618, -75.6944492927)],
['Village of Hermon', '', '', (44.4267499295, -75.2505950625)],
['Town of Hermon', '', '', (44.4663028287, -75.2298404552)],
['Town of Hopkinton', '', 'http://www.townofhopkinton.com/', (44.6981340685, -74.7016675458)],
['Town of Lawrence', '', '', (44.7786949974, -74.7110300278)],
['Town of Lisbon', '', 'http://www.lisbonny.net/', (44.7405949121, -75.2789400014)],
['Village of Massena', '', 'http://www.massenaworks.com/village/', (44.9312448013, -74.8932627886)],
['Town of Louisville', '', 'http://www.louisvillenewyork.com/', (44.934344906, -74.9018300114)],
['Town of Macomb', '', '', (44.3479849025, -75.7748100594)],
['Town of Madrid', '', 'http://townofmadrid.org', (44.7725049297, -75.1547400273)],
['Town of Massena', '', 'http://www.massenaworks.com/town/index.asp', (44.9312448013, -74.8932627886)],
['Village of Morristown', '', '', (44.5843731914, -75.6462141706)],
['Town of Morristown', '', 'http://www.townofmorristownny.org', (44.5843899918, -75.6455150379)],
['Village of Norwood', '', 'http://www.norwoodny.org', (44.753349927, -74.9858900965)],
['Town of Norfolk', '', 'http://www.norfolkny.us', (44.7995588725, -74.9869234912)],
['Village of Heuvelton', '', 'http://www.heuveltonny.com/', (44.6188339973, -75.41173311)],
['Town of Oswegatchie', '', 'http://townofoswegatchie.org/', (44.6208753707, -75.4114050832)],
['Town of Parishville', '', 'http://www.parishvilleny.us', (44.6286974898, -74.813548546)],
['Town of Piercefield', '', '', (44.2305331838, -74.5652734736)],
['Town of Pierrepont', '', 'http://www.townofpierrepont.com', (44.5417881882, -75.0105178864)],
['Town of Pitcairn', '', 'http://www.townofpitcairn.com', (44.1817448678, -75.2817615815)],
['Village of Potsdam', '', 'http://www.vi.potsdam.ny.us/', (44.6694172899, -74.9826266144)],
['Town of Potsdam', '', 'http://www.potsdamny.us', (44.669637821, -74.9871715551)],
['Town of Rossie', '', '', (44.3244899048, -75.7983450174)],
['Town of Russell', '', 'http://www.russellny.org', (44.3828199523, -75.0341150071)],
['Town of Stockholm', '', 'http://stockholm-ny.com', (44.7920343643, -74.7903652894)],
['Village of Waddington', '', 'http://www.villageofwaddington.org', (44.8606821423, -75.2056282562)],
['Town of Waddington', '', 'http://www.waddingtonny.us', (44.8575499465, -75.1626550763)],
['County of St Lawrence', '', 'http://www.stlawco.org', (44.5800399073, -75.1491600139)],
['Village of Amityville', '', 'http://www.amityville.com', (40.6787717347, -73.4182588387)],
['Village of Babylon', '', 'http://www.villageofbabylonny.gov', (40.695738023, -73.3262341102)],
['Village of Lindenhurst', '', 'http://villageoflindenhurst.com', (40.6818117383, -73.3670388264)],
['Town of Babylon', '', 'http://www.townofbabylon.com', (40.7053417345, -73.374818826)],
['Village of Belle Terre', '', 'http://www.belleterre.us', (40.950063881, -73.0614434751)],
['Village of Bellport', '', 'http://www.bellportvillage.org', (40.756281706, -72.9378489839)],
['Village of Lake Grove', '', 'http://www.lakegroveny.gov', (40.8581550521, -73.117560096)],
['Village of Mastic Beach', '', 'http://www.masticbeachvillageny.gov', (0.0, 0.0)],
['Village of Old Field', '', 'http://www.oldfieldny.org', (40.9350400234, -73.1065000879)],
['Village of Patchogue', '', 'http://www.patchoguevillage.org', (40.7616517427, -73.0121888736)],
['Village of Poquott', '', 'http://www.poquott.org', (40.9350400234, -73.1065000879)],
['Village of Port Jefferson', '', 'http://www.portjeff.com', (40.9458138392, -73.0717174142)],
['Village of Shoreham', '', 'http://www.shorehamvillage.org', (40.9594653448, -72.9087617621)],
['Town of Brookhaven', 'http://www.brookhaven.org', 'http://www.brookhaven.org', (40.8379100036, -73.0395700848)],
['Village of East Hampton', '', 'http://www.easthamptonvillage.org', (40.9618416311, -72.1863391721)],
['Village of Sag Harbor', '', 'http://www.sagharborny.gov', (41.0009316859, -72.2948191628)],
['Town of East Hampton', '', 'http://www.town.east-hampton.ny.us', (40.9682116617, -72.1719491303)],
['Village of Asharoken', '', 'http://www.asharoken.com', (40.9181916246, -73.3512283136)],
['Village of Huntington Bay', '', 'http://www.huntingtonbay.org', (40.8991850722, -73.4658250873)],
['Village of Lloyd Harbor', '', 'http://lloydharbor.org', (40.8858917472, -73.4585187644)],
['Village of Northport', '', 'http://www.northportny.gov', (40.9005217314, -73.3473587773)],
['Town of Huntington', 'http://www.huntingtonny.gov/content/13753/13757/17478/17508/default.aspx?_sm_au_=ivvt78qz5w7p2qhf', 'http://www.huntingtonny.gov', (40.8736417062, -73.4189188142)],
['Village of Brightwaters', '', 'http://www.villageofbrightwaters.com', (40.7303017914, -73.2718188298)],
['Village of Islandia', '', 'http://newvillageofislandia.com', (40.8068117224, -73.1640888404)],
['Village of Ocean Beach', '', 'http://www.villageofoceanbeach.org', (40.6487900475, -73.1578100904)],
['Village of Saltaire', '', 'http://www.saltaire.org', (40.640378576, -73.198257468)],
['Town of Islip', '', 'http://www.isliptown.org', (40.7297844354, -73.2108808664)],
['Town of Riverhead', 'http://www.townofriverheadny.gov/pview.aspx?id=2481&amp;catid=118&amp;_sm_au_=ivvt78qz5w7p2qhf', 'http://townofriverheadny.gov', (40.922791675, -72.6538089872)],
['Village of Dering Harbor', '', 'http://www.deringharborcommunity.org', (41.0829850918, -72.3545350085)],
['Town of Shelter Island', '', 'http://www.shelterislandtown.us/', (41.0698635504, -72.3389526073)],
['Village of Head Of The Harbor', '', 'http://villagehohny.org/', (0.0, 0.0)],
['Village of Nissequogue', '', 'http://nissequogueny.gov', (40.8990649717, -73.1944589142)],
['Village of The Branch', '', 'http://villageofthebranch.homestead.com/', (40.8518550724, -73.2107250872)],
['Town of Smithtown', 'http://www.smithtownny.gov/jobs.aspx?_sm_au_=ivvt78qz5w7p2qhf', 'http://www.smithtownny.gov', (40.8553029055, -73.1986474501)],
['Village of North Haven', '', 'http://northhavenny.us', (41.0314892279, -72.3123183059)],
['Village of Quogue', '', 'http://www.villageofquogue.com', (40.8167680019, -72.609998975)],
['Village of Sagaponack', '', 'http://www.sagaponackvillage.org', (0.0, 0.0)],
['Village of Southampton', '', 'http://www.southamptonvillage.org', (40.884781669, -72.3898891489)],
['Village of Westhampton Beach', '', 'http://www.westhamptonbeach.org', (40.8149630578, -72.6446080045)],
['Village of West Hampton Dunes', '', 'http://www.whdunes.org', (40.8295750107, -72.6858950336)],
['Town of Southampton', 'http://www.southamptontownny.gov/jobs.aspx', 'http://www.southamptontownny.gov', (40.8873316741, -72.3850290645)],
['Village of Greenport', '', 'http://www.greenport.com', (41.1024772094, -72.3631550374)],
['Town of Southold', '', 'http://www.southoldtownny.gov', (41.0634816932, -72.4313890551)],
['County of Suffolk', 'http://www.suffolkcountyny.gov/departments/civilservice.aspx', 'http://www.suffolkcountyny.gov', (40.9283550893, -72.6454050424)],
['Town of Bethel', '', 'http://www.town.bethel.ny.us', (41.6362050514, -74.8740500621)],
['Village of Jeffersonville', '', 'http://www.mamakating.org/villageofbloomingburg.php', (41.7843500426, -74.9365050947)],
['Town of Callicoon', '', 'http://townofcallicoon.org', (41.7833481603, -74.9316320088)],
['Town of Cochecton', '', 'http://townofcochectonny.org', (41.6797250851, -74.9350750544)],
['Town of Delaware', '', 'http://www.townofdelaware-ny.us/', (41.7812200841, -75.0225650264)],
['Village of Woodridge', '', '', (41.7072800281, -74.5740550483)],
['Town of Fallsburgh', '', 'http://www.townoffallsburg.com', (0.0, 0.0)],
['Town of Forestburgh', '', 'http://www.forestburgh.net', (41.5538100049, -74.7169650156)],
['Town of Fremont', '', 'http://www.fremontnewyork.us', (42.3944973631, -77.6270583018)],
['Town of Highland', '', 'http://www.townofhighlandny.com', (41.5400800492, -74.8979750867)],
['Village of Liberty', '', 'http://www.libertyvillageny.org', (41.8022590771, -74.7469085876)],
['Town of Liberty', '', 'http://www.townofliberty.org', (41.8012217258, -74.7473796221)],
['Town of Lumberland', '', 'http://www.townoflumberland.org', (43.2237449886, -76.4241699157)],
['Village of Bloomingburgh', '', 'http://www.mamakating.org/villageofbloomingburg.php', (41.5672250457, -74.4422900906)],
['Village of Wurtsboro', '', 'http://www.mamakating.org/villageofwurtsboro.php', (41.5844000825, -74.5212650403)],
['Town of Mamakating', '', 'http://www.mamakating.org', (41.5663718046, -74.497035879)],
['Town of Neversink', '', 'http://www.townofneversink.org', (41.847348376, -74.5481598292)],
['Town of Rockland', '', 'http://www.townofrocklandny.com', (41.8812750453, -74.8549600125)],
['Village of Monticello', '', 'http://www.villageofmonticello.com', (41.6540713416, -74.6818793853)],
['Town of Thompson', '', 'http://www.townofthompson.com', (41.6685341129, -74.672026423)],
['Town of Tusten', '', 'http://www.tusten.org', (41.5913750609, -74.9820450602)],
['County of Sullivan', '', 'http://www.co.sullivan.ny.us', (41.6584171483, -74.6918582066)],
['Village of Waverly', '', 'http://www.waverlybarton.com', (42.0009214147, -76.5390398176)],
['Town of Barton', '', 'http://www.townofbarton.org', (42.0095467986, -76.5066282696)],
['Town of Berkshire', '', 'http://www.berkshireny.net', (42.3001468109, -76.1876636973)],
['Village of Candor', '', 'http://www.tiogacountyny.com/towns-villages/candor-village-of.html', (42.2318414316, -76.3416423264)],
['Town of Candor', '', 'http://www.candorny.us', (42.2293741197, -76.339092359)],
['Village of Newark Valley', '', 'http://villagenv.com/', (42.223008223, -76.1831693907)],
['Town of Newark Valley', '', 'http://www.tiogacountyny.com/towns-villages/newark-valley.html', (42.2321974359, -76.1850349798)],
['Village of Nichols', '', 'http://www.tiogacountyny.com/towns-villages/nichols-village-of.html', (42.0229213922, -76.3671699332)],
['Town of Nichols', '', 'http://www.tiogacountyny.com/towns-villages/nichols.html', (42.0400200357, -76.323984972)],
['Village of Owego', '', 'http://www.villageofowego.com', (42.1034580303, -76.2622912756)],
['Town of Owego', '', 'http://www.townofowego.com', (42.1005500934, -76.2455839328)],
['Town of Richford', '', 'http://www.richfordny.com', (42.3827850495, -76.1953449798)],
['Village of Spencer', '', 'http://www.tiogacountyny.com/towns-villages/spencer-village-of.html', (42.3214950952, -76.5113199914)],
['Town of Spencer', '', 'http://www.tiogacountyny.com/towns-villages/spencer.html', (42.2463061144, -76.5069099936)],
['Town of Tioga', '', 'http://www.tiogacountyny.com/towns-villages/tioga.html', (42.0556350422, -76.3482999485)],
['County of Tioga', 'http://www.tiogacountyny.com/departments/personnel-civil-service', 'http://www.tiogacountyny.com', (42.1009734766, -76.2666328279)],
['Town of Caroline', '', 'http://www.townofcaroline.org', (42.4016350236, -76.3551699281)],
['Town of Danby', '', 'http://town.danby.ny.us', (42.3539607405, -76.4820580531)],
['Village of Dryden', '', 'http://www.dryden-ny.org', (42.4895547514, -76.2979435075)],
['Village of Freeville', '', 'http://freevilleny.org', (42.4988450749, -76.3572299205)],
['Town of Dryden', '', 'http://www.dryden.ny.us', (42.4912505428, -76.2861872887)],
['Town of Enfield', '', 'http://www.townofenfield.org', (42.4380752013, -76.6312150334)],
['Village of Groton', '', 'http://www.grotonny.org', (42.5911808511, -76.3660600317)],
['Town of Groton', '', 'http://www.townofgrotonny.org', (42.5902246801, -76.3696417776)],
['Village of Cayuga Heights', '', 'http://www.cayuga-heights.ny.us', (42.4454850661, -76.5180349008)],
['Town of Ithaca', '', 'http://www.town.ithaca.ny.us', (42.4411816738, -76.4966856999)],
['Village of Lansing', '', 'http://www.vlansing.org', (42.4881305536, -76.4884785439)],
['Town of Lansing', '', 'http://www.lansingtown.com', (42.6253100711, -76.5757499955)],
['Town of Newfield', '', 'http://newfieldny.org', (42.3432050642, -76.6146499777)],
['Village of Trumansburg', '', 'http://www.trumansburg-ny.gov', (42.5410809369, -76.660198577)],
['Town of Ulysses', '', 'http://www.ulysses.ny.us', (42.5412128612, -76.6612631819)],
['County of Tompkins', '', 'http://tompkinscountyny.gov/assessment', (42.4422926175, -76.4973344654)],
['Town of Denning', '', 'http://www.denning.us', (41.9042700726, -74.6024950039)],
['Town of Esopus', '', 'http://www.esopus.com', (41.9062100748, -73.981545033)],
['Town of Gardiner', '', 'http://www.townofgardiner.org', (41.6682250755, -74.1837000635)],
['Town of Hardenburgh', '', 'http://www.townofhardenburgh.org', (42.1104679772, -74.5492679916)],
['Town of Hurley', '', 'http://www.townofhurley.org', (41.9255439683, -74.0671253947)],
['Town of Kingston', '', 'http://www.townkingstonny.us', (41.9865172466, -74.033545481)],
['Town of Lloyd', '', 'http://www.townoflloyd.com', (41.7192660111, -73.9657456387)],
['Town of Marbletown', '', 'http://www.marbletown.net', (41.8701250246, -74.1759000987)],
['Town of Marlborough', '', 'http://www.marlboroughny.com', (41.637846491, -73.9626650262)],
['Village of New Paltz', '', 'http://www.villageofnewpaltz.org', (41.7543800244, -74.0934800782)],
['Town of New Paltz', '', 'http://www.townofnewpaltz.org', (41.7565202036, -74.0826452034)],
['Town of Olive', '', 'http://www.town.olive.ny.us', (41.9596900771, -74.3137250401)],
['Town of Plattekill', '', 'http://www.town.plattekill.ny.us', (41.6620350008, -74.1046800476)],
['Town of Rochester', '', 'http://www.townofrochester.net', (41.7858768207, -74.2377531624)],
['Town of Rosendale', '', 'http://www.townofrosendale.com', (41.8439895214, -74.0833997359)],
['Village of Saugerties', '', 'http://village.saugerties.ny.us/', (42.0786857722, -73.9524226186)],
['Town of Saugerties', '', 'http://www.saugerties.ny.us', (42.0815125936, -73.9588282232)],
['Town of Shandaken', '', 'http://www.shandaken.us', (42.1798050476, -74.4124950157)],
['Town of Shawangunk', '', 'http://www.shawangunk.org', (41.4640358549, -74.4114529495)],
['Town of Ulster', '', 'http://www.townofulster.org', (41.9772521382, -74.0027313973)],
['Village of Ellenville', '', 'http://villageofellenville.com', (41.6767050356, -74.4601250568)],
['Town of Wawarsing', '', 'http://www.townofwawarsing.net', (41.7174850752, -74.3929550573)],
['Town of Woodstock', '', 'http://www.woodstockny.org', (42.0373948382, -74.125684527)],
['County of Ulster', 'http://www.co.ulster.ny.us/personnel', 'http://www.co.ulster.ny.us', (41.932729673, -74.0174184447)],
['Town of Bolton', '', 'http://www.boltonnewyork.com', (43.5571611412, -73.6561785596)],
['Town of Chester', '', 'http://www.townofchesterny.org', (41.3398490744, -74.2755453151)],
['Town of Hague', '', 'http://www.townofhague.org', (43.7489164559, -73.5017231691)],
['Town of Horicon', '', 'http://www.horiconny.gov', (43.7027149616, -73.6933700398)],
['Town of Johnsburg', '', 'http://www.johnsburgny.com', (43.6688399697, -74.0550700529)],
['Village of Lake George', '', 'http://www.lakegeorgevillage.com', (43.4308285578, -73.7162533057)],
['Town of Lake George', '', 'http://www.town.lakegeorge.ny.us', (43.4313011642, -73.7167785218)],
['Town of Lake Luzerne', '', 'http://www.townoflakeluzerne.com', (43.3205309862, -73.8413160118)],
['Town of Queensbury', '', 'http://www.queensbury.net', (43.3597112246, -73.6565085884)],
['Town of Stony Creek', '', 'http://www.stonycreekny.com', (43.4243840247, -73.927427046)],
['Town of Thurman', '', 'http://www.thurman-ny.com/', (43.4855249234, -73.8842850313)],
['Town of Warrensburg', '', 'http://townofwarrensburg.org', (43.4934012009, -73.7710984584)],
['County of Warren', 'http://www.warrencountyny.gov/civilservice/exams.php', 'http://warrencountyny.gov', (43.4355784842, -73.7181883273)],
['Village of Argyle', '', 'http://www.argyle-village.org', (43.2447499688, -73.460765019)],
['Town of Argyle', '', 'http://www.argyleny.com', (43.2344692526, -73.4906566192)],
['Village of Cambridge', '', 'http://www.cambridgeny.gov', (43.0269660211, -73.3842762838)],
['Town of Cambridge', '', 'http://townofcambridgeny.org', (42.9943753139, -73.4551067304)],
['Town of Dresden', '', '', (43.6313850122, -73.4440950737)],
['Village of Greenwich', '', 'http://www.villageofgreenwich.org', (43.0914436845, -73.5030750367)],
['Town of Easton', '', 'http://eastonny.org', (43.0861849167, -73.4958350658)],
['Village of Fort Ann', '', '', (43.4450799884, -73.5070900056)],
['Town of Fort Ann', '', 'http://www.fortann.us', (43.4450799884, -73.5070900056)],
['Village of Fort Edward', '', 'http://villageoffortedward.com', (43.268029751, -73.5853614714)],
['Town of Fort Edward', '', 'http://www.fortedward.net', (43.268029751, -73.5853614714)],
['Village of Granville', '', 'http://granvillevillage.com', (43.3700350036, -73.3173200149)],
['Town of Granville', '', '', (43.408240992, -73.2581561)],
['Town of Greenwich', '', 'http://www.greenwichny.org', (43.0914925267, -73.5023876861)],
['Town of Hampton', '', 'http://www.hamptonny.org', (43.476734934, -73.2576750173)],
['Town of Hartford', '', 'http://www.hartfordny.com', (43.3717725773, -73.3886054066)],
['Town of Hebron', '', 'http://www.hebronny.com', (43.2291197698, -73.374779434)],
['Town of Jackson', '', 'http://www.townofjacksonny.com', (43.1217249563, -73.3104750243)],
['Village of Hudson Falls', '', 'http://www.villageofhudsonfalls.com', (43.3030117272, -73.5845948846)],
['Town of Kingsbury', '', 'http://www.kingsburyny.gov', (43.3024762925, -73.5851957529)],
['Town of Putnam', '', '', (43.7486999333, -73.415320081)],
['Village of Salem', '', 'http://www.salem-ny.com/governmentvillage.html', (43.1715580192, -73.3272622781)],
['Town of Salem', '', 'http://www.salem-ny.com', (43.173830229, -73.3276886304)],
['Town of White Creek', '', '', (43.0651100024, -73.3928150116)],
['Village of Whitehall', '', 'http://www.whitehallny.info/', (43.5551046876, -73.4010668271)],
['Town of Whitehall', '', '', (43.555093161, -73.4028191187)],
['County of Washington', '', 'http://www.co.washington.ny.us', (43.2638899821, -73.6209250709)],
['Village of Newark', '', 'https://www.villageofnewark.com', (43.0047699104, -77.0964549649)],
['Town of Arcadia', '', 'http://www.co.wayne.ny.us/Departments/historian/Histarcadia.htm', (43.0462114015, -77.0931673067)],
['Village of Wolcott', '', 'http://www.wolcottny.org/Village/villageindex.php', (43.2197813733, -76.8154174159)],
['Town of Butler', '', '', (43.1605120038, -76.7763019971)],
['Village of Clyde', '', 'http://www.clydeny.com', (42.9993999197, -76.9288449471)],
['Town of Galen', '', 'http://www.townofgalen.org', (43.0835713457, -76.8704774484)],
['Town of Huron', '', 'http://townofhuron.org/content', (43.2353413145, -76.8682373965)],
['Village of Lyons', '', 'http://villageoflyons.com', (43.0644713556, -76.991517398)],
['Town of Lyons', '', 'http://www.lyonsny.com/', (43.0688714002, -76.9898673417)],
['Village of Macedon', '', 'http://www.villageofmacedon.org', (43.0686162856, -77.3005181977)],
['Town of Macedon', '', 'http://macedontown.net', (43.0674613815, -77.3073972831)],
['Town of Marion', '', 'http://www.townofmarionny.com', (43.14336138, -77.1891773143)],
['Town of Ontario', '', 'http://www.ontariotown.org', (43.2235515965, -77.2916013027)],
['Village of Palmyra', '', 'http://www.palmyrany.com/government/village/home.htm', (43.0632214116, -77.2319573485)],
['Town of Palmyra', '', 'http://www.palmyrany.com/government/town/home.htm', (43.0522449673, -77.23337091)],
['Town of Rose', '', '', (43.1869992856, -76.8932465777)],
['Town of Savannah', '', '', (43.067061395, -76.7598174831)],
['Village of Sodus', '', 'http://sodusny.org/', (43.2353229236, -77.062021085)],
['Village of Sodus Point', '', 'http://www.soduspoint.info', (43.2600149791, -76.9953099632)],
['Town of Walworth', '', 'http://www.townofwalworthny.gov/', (43.1341613654, -77.2886372297)],
['Town of Williamson', '', 'http://town.williamson.ny.us', (43.231096645, -77.1870621788)],
['Village of Red Creek', '', '', (43.2494549386, -76.7366299155)],
['Town of Wolcott', '', 'http://www.wolcottny.org/townindex.php', (43.2217913443, -76.8149174236)],
['County of Wayne', 'http://web.co.wayne.ny.us', 'http://www.co.wayne.ny.us', (43.0638168019, -76.992864258)],
['Town of Bedford', '', 'http://www.bedfordny.gov', (41.2366148039, -73.7098257234)],
['Village of Buchanan', '', 'http://www.villageofbuchanan.com', (41.2610817407, -73.9393987305)],
['Village of Croton-on-Hudson', '', 'http://village.croton-on-hudson.ny.us', (41.2135550873, -73.8836050192)],
['Town of Cortlandt', 'http://www.townofcortlandt.com', 'http://www.townofcortlandt.com', (41.3097125258, -73.9039846537)],
['Village of Bronxville', '', 'http://www.villageofbronxville.com', (40.935522609, -73.831472152)],
['Village of Tuckahoe', '', 'http://www.tuckahoe.com', (40.94727019, -73.8245060746)],
['Town of Eastchester', 'http://www.eastchester.org/departments/comptoller.php', 'http://www.eastchester.org', (40.9554872275, -73.8112090597)],
['Village of Ardsley', '', 'http://www.ardsleyvillage.com', (41.011592504, -73.8460631346)],
['Village of Dobbs Ferry', '', 'http://www.dobbsferry.com', (41.0150511023, -73.8746757402)],
['Village of Elmsford', '', 'http://www.elmsfordny.org', (41.0537209845, -73.8201314932)],
['Village of Hastings-on-Hudson', '', 'http://hastingsgov.org', (40.9953080073, -73.8832390732)],
['Village of Irvington', '', 'http://www.irvingtonny.gov', (41.0391735112, -73.8669099111)],
['Village of Tarrytown', '', 'http://www.tarrytowngov.com', (41.0824700435, -73.8585500945)],
['Town of Greenburgh', 'http://www.greenburghny.com', 'http://www.greenburghny.com/', (40.9937781921, -73.8721961451)],
['Village of Harrison', '', 'http://www.harrison-ny.gov', (40.9698921729, -73.7128775359)],
['Town of Harrison', '', 'http://www.harrison-ny.gov', (40.9699023744, -73.7122665655)],
['Town of Lewisboro', '', 'http://www.lewisborogov.com', (41.2756325163, -73.5558531841)],
['Village of Larchmont', '', 'http://www.villageoflarchmont.org', (40.927780164, -73.7517106004)],
['Village of Mamaroneck', '', 'http://www.village.mamaroneck.ny.us', (40.9493177993, -73.7328772462)],
['Town of Mamaroneck', '', 'http://www.townofmamaroneck.org', (40.9428968541, -73.741382784)],
['Village of Mount Kisco', '', 'http://www.mountkisco.org', (41.2061231529, -73.7270800266)],
['Town of Mount Kisco', '', 'http://www.mountkisco.org', (41.2061231529, -73.7270800266)],
['Village of Briarcliff Manor', '', 'http://www.briarcliffmanor.org', (41.1489095589, -73.8286229423)],
['Village of Pleasantville', '', 'http://www.pleasantville-ny.gov', (41.1338347054, -73.7916926775)],
['Town of Perry', '', 'http://www.townofperryny.com', (42.7355900664, -78.0046049811)],
['Village of Sleepy Hollow', '', 'http://www.sleepyhollowny.gov', (41.0849187782, -73.8594731485)],
['Town of Mount Pleasant', '', 'http://www.mtpleasantny.com/', (41.0964495055, -73.7775992091)],
['Town of New Castle', '', 'http://www.mynewcastle.org', (41.1554186963, -73.7746266459)],
['Town of North Castle', '', 'http://www.northcastleny.com', (41.12478745, -73.7127459758)],
['Town of North Salem', '', 'http://www.northsalemny.org', (41.3291968219, -73.5979615154)],
['Village of Ossining', 'http://www.villageofossining.org/personnel-department', 'http://www.villageofossining.org', (41.1630184728, -73.8608068679)],
['Town of Ossining', 'http://www.townofossining.com/cms/resources/human-resources', 'http://www.townofossining.com', (41.1630184728, -73.8608068679)],
['Village of Pelham', '', 'http://www.pelhamgov.com', (40.9089824023, -73.8116488856)],
['Village of Pelham Manor', '', 'http://www.pelhammanor.org', (40.8900420022, -73.8040820193)],
['Town of Pelham', '', 'http://www.townofpelham.com', (40.9116938073, -73.8091812017)],
['Town of Pound Ridge', '', 'http://www.townofpoundridge.com', (41.1980566679, -73.5687685097)],
['Village of Port Chester', '', 'http://www.portchesterny.com', (40.9899257823, -73.667160346)],
['Village of Rye Brook', '', 'http://www.ryebrook.org', (41.0346831565, -73.6746420044)],
['Town of Rye', '', 'http://www.townofryeny.com', (40.9899258097, -73.6671603811)],
['Village of Scarsdale', '', 'http://www.scarsdale.com', (40.9883283374, -73.7974469368)],
['Town of Scarsdale', '', 'http://www.scarsdale.com', (40.9883283374, -73.7974469368)],
['Town of Somers', '', 'http://www.somersny.com', (41.3283527969, -73.6858080794)],
['Town of Yorktown', 'http://www.yorktownny.org/jobs', 'http://www.yorktownny.org', (41.2687279789, -73.782157324)],
['County of Westchester', 'http://humanresources.westchestergov.com/job-seekers/civil-service-exams', 'http://www.westchestergov.com/', (41.0308703166, -73.7676156989)],
['Village of Arcade', '', 'http://www.villageofarcade.org', (42.5345396553, -78.4246815014)],
['Town of Arcade', '', '', (42.5336466095, -78.4227751776)],
['Town of Attica', '', 'http://www.townofattica.net', (42.8640318327, -78.2688360407)],
['Town of Bennington', '', 'http://www.benningtonny.com', (42.8364647293, -78.3981200849)],
['Village of Castile', '', 'http://www.castileny.com', (42.6337181635, -78.0480761408)],
['Village of Perry', '', 'http://www.villageofperry.com', (42.7173563534, -78.003309395)],
['Town of Castile', '', 'http://www.castileny.com', (42.6337842763, -78.0480517605)],
['Town of Covington', '', 'http://www.townofcovington.com', (42.8541116902, -78.012997601)],
['Town of Eagle', '', 'http://www.wyomingco.net/towns/townofeagle.htm', (42.5820607702, -78.2448479767)],
['Village of Gainesville', '', 'http://www.wyomingco.net/towns/villageofgainesville.htm', (42.6382003924, -78.1312857823)],
['Village of Silver Springs', '', 'http://www.wyomingco.net/towns/villageofsilversprings.htm', (42.6603578904, -78.0834102556)],
['Town of Gainesville', '', 'http://www.wyomingco.net/towns/townofgainesville.htm', (42.6643809901, -78.0898479214)],
['Town of Genesee Falls', '', 'http://www.wyomingco.net/towns/townofgeneseefalls.htm', (42.6396451815, -77.9982565173)],
['Town of Java', '', 'http://www.wyomingco.net/towns/townofjava.htm', (42.6501365253, -78.3869213714)],
['Village of Wyoming', '', 'http://www.wyomingco.net/towns/villageofwyoming.htm', (42.8255968175, -78.0852525903)],
['Town of Middlebury', '', 'http://www.middleburyny.com', (42.7395000393, -78.1712998996)],
['Town of Orangeville', '', 'http://www.wyomingco.net/towns/townoforangeville.htm', (42.7558331925, -78.2762641015)],
['Town of Pike', '', 'http://www.wyomingco.net/towns/villageofpike.htm', (42.5543569163, -78.1562975733)],
['Town of Sheldon', '', 'http://www.townofsheldon.com', (42.7371072403, -78.3891004147)],
['Village of Warsaw', '', 'http://www.wyomingco.net/towns/villageofwarsaw.htm', (42.7395000393, -78.1712998996)],
['Town of Warsaw', '', 'http://www.villageofwarsaw.org', (42.7395000393, -78.1712998996)],
['Town of Wethersfield', '', 'http://www.wyomingco.net/towns/townofwethersfield.htm', (42.6806389243, -78.2059975166)],
['County of Wyoming', 'http://www.wyomingco.net/164/civil-service', 'http://www.wyomingco.net', (42.7430825689, -78.1330522427)],
['Town of Barrington', '', 'http://www.townofbarrington.org', (42.6673400165, -77.0521849839)],
['Village of Penn Yan', '', 'http://www.villageofpennyan.com', (42.6611115463, -77.0543174358)],
['Town of Benton', '', 'http://www.townofbenton.us', (42.6673400165, -77.0521849839)],
['Town of Italy', '', '', (42.6596900205, -77.4949499176)],
['Town of Jerusalem', '', 'http://www.jerusalem-ny.org', (42.5991015747, -77.1587473506)],
['Town of Middlesex', '', 'http://www.middlesexny.org', (42.7047668245, -77.2716504309)],
['Town of Milo', '', 'http://www.townofmilo.com', (42.662021494, -77.0538674398)],
['Town of Potter', '', '', (42.7046015571, -77.206937299)],
['Village of Dundee', '', '', (42.522791585, -76.9784874407)],
['Town of Starkey', '', '', (42.5237715151, -76.972617461)],
['Village of Dresden', '', 'http://www.dresdenny.org', (42.6825814332, -76.956127425)],
['Town of Torrey', '', 'http://www.townoftorrey.com', (42.6905650445, -76.9590149901)],
['County of Yates', 'http://www.yatescounty.org/203/personnel', 'http://www.yatescounty.org', (42.6648936058, -77.0583614689)],
['Town of Guilderland', 'http://www.townofguilderland.org/pages/guilderlandny_hr/index?_sm_au_=ivv8z8lp1wffsnv6', 'http://www.townofguilderland.org/', (42.7177425375, -73.9361582876)],
['Town of Rhinebeck', '', 'http://www.rhinebeck-ny.gov', (41.9268332466, -73.9090879389)],
['Village of Rhinebeck', '', 'http://www.rhinebeck-ny.gov', (41.926785956, -73.909715008)],
['Village of Corinth', '', 'http://www.villageofcorinthny.com', (43.2448938757, -73.8323536025)],
['Town of Union Vale', '', 'http://www.unionvaleny.us', (41.6659050068, -73.7271300366)],


]







    # Advanced options
    max_crawl_depth = 2
    num_procs = 16


    # URL queues
    all_urls_q = Queue() # Put all portal and working URLs in this queue

    # Create manager to share objects between processes
    manager = Manager()

    # Debugging
    jbw_tally_man_l = manager.list() # Used to determine the frequency that jbws are used

    # Set paths to files
    queue_path = os.path.join(dater_path, 'queue.txt')
    checked_path = os.path.join(dater_path, 'checked_pages.txt')
    error_path = os.path.join(dater_path, 'errorlog.txt')



    all_urls_q = Queue() # Put all portal and working URLs in this queue
    checkedurls_man_list = manager.list() # URLs that have been checked and their outcome. eg: jbw conf or error
    errorurls_man_dict = manager.dict() # URLs that have resulted in an error
    sort_dict = manager.dict() # Put URLs and there jbw conf

    
    # Put school URLs in queue
    for i in all_list:

        em_url = i[1]
        homepage = i[2]

        # Skip if home page is missing
        if not homepage.strip(): continue

        # Skip if em URL is present
        if em_url.strip(): continue

        # Skip if em URL is marked
        if em_url.startswith('_'): continue

        # Add scheme if necessary
        if not homepage.startswith('http'):
            homepage = 'http://' + homepage

        # Put civil service URLs, initial crawl level, portal url, and jbws type into queue
        all_urls_q.put([homepage, 0, homepage, 'sch'])

        # Put portal URL into checked pages
        dup_checker = dup_checker_f(homepage)
        checkedurls_man_list.append([dup_checker, None])






    # Integers to be shared between processes
    qlength = all_urls_q.qsize() # Length of the primary queue
    skipped_pages = Value('i', 0) # Number of pages that have been skipped
    prog_count = Value('i', 0) # Number of pages checked
    total_count = Value('i', qlength) # Number of pages to be checked
    waiting_procs = Value('i', 0) # Used to tell manager that proc is waiting


    # Create child processes
    for arb_var in range(num_procs):
        worker = Process(target=scraper, args=(all_urls_q, max_crawl_depth, checkedurls_man_list, errorurls_man_dict, skipped_pages, prog_count, total_count, jbw_tally_man_l, sort_dict))
        worker.start()

    # Wait until all tasks are done
    current_prog_c = None
    while len(active_children()) > 1:
        if current_prog_c != prog_count.value:
            #tmp = os.system('clear||cls')
            print(os.getpid(), ' Number of processes running =', len(active_children()), '\n Max crawl depth =', max_crawl_depth)
            print(os.getpid(), '\n\n\n\n Searching in:')
            print(os.getpid(), 'Civil Service')
            print(os.getpid(), 'School districts and charter schools')
            print(os.getpid(), 'Universities and colleges')

            print(os.getpid(), '\n\n Waiting for all processes to finish. Progress =', prog_count.value, 'of', total_count.value)
            current_prog_c = prog_count.value

           
        time.sleep(6)


        



    print(os.getpid(), '\n =======================  Search complete  =======================')



    '''
    # jbw tally
    for i in jobwords_civ_low:
        r_count = jbw_tally_man_l.count(i)
        print(os.getpid(), i, '=', r_count)

    for i in jobwords_su_low:
        r_count = jbw_tally_man_l.count(i)
        print(os.getpid(), i, '=', r_count)

    print(os.getpid(), '\n')

    for i in jobwords_civ_high:
        r_count = jbw_tally_man_l.count(i)
        print(os.getpid(), i, '=', r_count)

    for i in jobwords_su_high:
        r_count = jbw_tally_man_l.count(i)
        print(os.getpid(), i, '=', r_count)
    '''


    # Clear checked pages
    with open(checked_path, "w") as checked_file:
        checked_file.write('')

    # Write checked pages to file
    with open(checked_path, "a") as checked_file:
        for kk in checkedurls_man_list:
            checked_file.write(str(kk) + ',\n')


    # Clear errorlog
    with open(error_path, "w") as error_file:
        error_file.write('')

    # errorurls_man_dict contents: {workingurl = [err_code, err_desc, current_crawl_level, jbw_type, portalurl]}
    # Write errorlog
    with open(error_path, "a", encoding='utf8') as writeerrors:

        ## do you want a heading? needs updating
        #writeerrors.write(' Error Code \t\t\t Error Description \t\t\t current_crawl_level \t\t :: \t\t URL\n\n')

        # Replace superfluous characters and make pretty formatting
        for k, v in errorurls_man_dict.items():
            k = k.replace('[', '').replace(']', '').replace("'", '')
            writeerrors.write(k + ', ')

            v = str(v).replace('[', '').replace(']', '').replace("'", '')
            writeerrors.write(v)
            writeerrors.write('\n\n')

    # Calculate error rate
    try:
        error_rate = len(errorurls_man_dict) / len(checkedurls_man_list)
        if error_rate < 0.05: error_rate_desc = '(low error rate)'
        elif error_rate < 0.15: error_rate_desc = '(medium error rate)'
        else: error_rate_desc = '(high error rate)'
    except: error_rate_desc = '(error rate unavailable)'

    # Build portal URL errors list
    portal_error_list = []
    if len(errorurls_man_dict.items()) > 0:
        for v,k in errorurls_man_dict.items():

            # Must have current crawl level in every errorurls_man_dict entry or you'll get error here
            # List based on crawl level
            if k[2] < 1:
                portal_error_list.append(v)

    # Stop timer and display stats
    duration = datetime.datetime.now() - startTime
    print(os.getpid(), '\n\nPages checked =', len(checkedurls_man_list))
    #for x in checkedurls_man_list: print(os.getpid(), x)
    print(os.getpid(), 'Pages skipped =', skipped_pages.value, '\nDuration =', duration.seconds, 'seconds\nPage/sec/proc =', str((len(checkedurls_man_list) / duration.seconds) / num_procs)[:4], '\nErrors detected =', len(errorurls_man_dict), error_rate_desc, '\nPortal errors =', len(portal_error_list), '\n')

    # Display errors
    if len(errorurls_man_dict.values()) > 0:

        # Create tally vars as a batch
        error1_tally, error2_tally, error3_tally, error4_tally, error5_tally, error6_tally, error7_tally = (0,)*7

        # Tally error frequencies
        for i in errorurls_man_dict.values():
            if 'jj_error 1' in i: error1_tally += 1
            elif 'jj_error 2' in i: error2_tally += 1
            elif 'jj_error 3' in i: error3_tally += 1
            elif 'jj_error 4' in i: error4_tally += 1
            elif 'jj_error 5' in i: error5_tally += 1
            elif 'jj_error 6' in i: error6_tally += 1
            elif 'jj_error 7' in i: error7_tally += 1


        print(os.getpid(), '   Error code:     Description | Frequency')
        print(os.getpid(), '  -----------------------------|-------------')
        print(os.getpid(), '      Error 1:   Unknown error |', error1_tally)
        print(os.getpid(), '      Error 2:        Non-HTML |', error2_tally)
        print(os.getpid(), '      Error 3: Request timeout |', error3_tally)
        print(os.getpid(), '      Error 4:  HTTP 404 / 403 |', error4_tally)
        print(os.getpid(), '      Error 5:   Other request |', error5_tally)
        print(os.getpid(), '      Error 6:  Splash failure |', error6_tally)
        print(os.getpid(), '      Error 7:           Misc. |', error7_tally)


    print(sort_dict)


    # Display results
    with lock:
        for i in sort_dict:
            w_l = []

            # Display original full entry
            for orig_entry in all_list:
                if i == orig_entry[2]:
                    print("\n\n" + str(orig_entry) + ',')
                    break

            # Sort by jbw conf
            temp = sorted(sort_dict[i], key = lambda x: int(x[1]), reverse=True)

            for ii in temp: # List each em URL

                if i == ii[0]: continue # Exclude URL if same as homepage
                if ii in w_l: continue # Exclude dups
                print(ii[0]) # Exclude jbw conf
                w_l.append(ii)





'''
# Find matching URLs from old db
for i in sort_dict.items():
    print('\n\n=', i[0])
    for ii in i[1]:
        for iii in uni_list:
            if iii == ii[0]:
                print('Match:', iii)
'''


'''
# To include centralized services
# olas = omit. centralized and dynamic. all at: https://www.pnwboces.org/olas/#!/jobs
# recruitfront = omit. centralized. all at: https://monroe2boces.recruitfront.com/JobBoard
# interviewexchange = keep. decentralized. captcha prompt
# wnyric = keep. decentralized. omit all at: https://schoolapp.wnyric.org/ats/job_board?start_index=200
# use regex to determine pages = '<a href="/ats/job_board\?start_index=\d+">'

# Fetch from wnyric
if school_arg or uni_arg:
    wnyric_pages = re.findall('<a href="/ats/job_board\?start_index=\d+">', html, flags=re.DOTALL)

    for i in set(wnyric_pages):
        i = i.split('job_board')[1]
        i = i.split('"')[0]
        i = 'https://schoolapp.wnyric.org/ats/job_board' + i
        print(os.getpid(), i)

'''
















