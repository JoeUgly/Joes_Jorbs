
# Description: Crawl webpages and rank links based on likelihood of containing job postings.




import datetime, docker, requests, psutil, json, gzip, os, queue, re, socket, time, traceback, urllib.parse, urllib.request, webbrowser, ssl
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
bunkwords = ('academics', 'pnwboces.org', 'recruitfront.com', 'schoolapp.wnyric.org', 'professional development', 'career development', 'javascript:', '.pdf', '.jpg', '.ico', '.rtf', '.doc', 'mailto:', 'tel:', 'icon', 'description', 'specs', 'specification', 'guide', 'faq', 'images', 'exam scores', 'resume-sample', 'resume sample', 'directory', 'pupil personnel')

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
                    print(os.getpid(), 'Empty soup0:', workingurl)
                    continue

                # Remove script, style, and empty elements
                for i in soup(["script", "style"]):
                    i.decompose()

                ## unn
                # Iterate through and remove all of the hidden style attributes
                r = soup.find_all('', {"style" : style_reg})
                for x in r:
                    #print(os.getpid(), 'Decomposed:', workingurl, x)
                    x.decompose()

                # Type="hidden" attribute
                r = soup.find_all('', {"type" : 'hidden'})
                for x in r:
                    #print(os.getpid(), 'Decomposed:', workingurl, x)
                    x.decompose()

                # Hidden section(s) and dropdown classes
                for x in soup(class_=class_reg):
                    #print(os.getpid(), 'Decomposed:', workingurl, x)
                    x.decompose()

                
                ## This preserves whitespace across lines. Prevents: 'fire departmentapparatuscode compliance'
                # Remove unnecessary whitespace. eg: multiple newlines, spaces, and all tabs
                vis_soup = ''
                temp_soup = str(soup.text)
                for i in temp_soup.split('\n'):
                    i = i.replace('\t', ' ').replace('  ', '')
                    if i:
                        vis_soup = vis_soup + i

                '''
                # Remove unnecessary whitespace
                vis_soup = ''
                temp_soup = str(soup.text)
                for i in temp_soup.split('\n'):
                    i = i.strip()
                    if i:
                        vis_soup = vis_soup + i
                '''

                # Use lowercase visible text for comparisons
                vis_soup = vis_soup.lower()

                if vis_soup is None:
                    print(os.getpid(), 'Empty soup1:', workingurl)
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

    all_list2 = [
['ABBOTT UNION FREE SCHOOL DISTRICT', '', 'www.abbottufsd.org', (41.0430933949, -73.8563583389)],
['ADDISON CENTRAL SCHOOL DISTRICT', 'http://www.addisoncsd.org/domain/30', 'www.addisoncsd.org', (42.1001732444, -77.2312078066)],
['ADIRONDACK CENTRAL SCHOOL DISTRICT', 'https://www.adirondackcsd.org/welcome/employment_opportunities', 'www.adirondackcsd.org', (43.4826797831, -75.3367246688)],
['AFTON CENTRAL SCHOOL DISTRICT', 'https://www.aftoncsd.org/Employment1.aspx', 'www.aftoncsd.org', (42.2299678749, -75.527336497)],
['AKRON CENTRAL SCHOOL DISTRICT', 'http://www.akronschools.org/Page/5499', 'www.akronschools.org', (43.0221769248, -78.4938084447)],
['ALBANY CITY SCHOOL DISTRICT', 'https://www.albanyschools.org/employment/index.html', 'www.albanyschools.org', (42.653413081, -73.7543811061)],
['ALBION CENTRAL SCHOOL DISTRICT', 'http://www.albionk12.org/district/district-office/employment/index', 'www.albionk12.org', (43.2393211046, -78.1847900128)],
['ALDEN CENTRAL SCHOOL DISTRICT', 'http://aldenschools.org/Page/25', 'www.aldenschools.org', (42.9030205856, -78.4965127996)],
['ALEXANDER CENTRAL SCHOOL DISTRICT', '', 'www.alexandercsd.org', (42.9020052366, -78.2610842264)],
['ALEXANDRIA CENTRAL SCHOOL DISTRICT', 'http://www.alexandriacentral.org/Page/398', 'www.alexandriacentral.org', (44.3367529522, -75.9099510381)],
['ALFRED-ALMOND CENTRAL SCHOOL DISTRICT', '', 'www.aacs.wnyric.org', (42.294521398, -77.7487625349)],
['ALLEGANY-LIMESTONE CENTRAL SCHOOL DISTRICT', 'http://www.alcsny.org/Page/1695', 'www.alcsny.org', (42.1319816381, -78.5040358743)],
['ALTMAR-PARISH-WILLIAMSTOWN CENTRAL SCHOOL DISTRICT', 'https://www.apwschools.org/Page/1083', 'www.apwschools.org', (43.443596009, -76.053234569)],
['AMAGANSETT UNION FREE SCHOOL DISTRICT', '', 'www.aufsd.org', (40.9768001783, -72.138217828)],
['AMHERST CENTRAL SCHOOL DISTRICT', 'http://www.amherstschools.org/Page/242', 'www.amherstschools.org', (42.9564996874, -78.7919240763)],
['AMITYVILLE UNION FREE SCHOOL DISTRICT', 'http://www.amityvilleschools.org/departments/human_resources', 'www.amityvilleschools.org', (40.6772195098, -73.4179283469)],
['AMSTERDAM CITY SCHOOL DISTRICT', 'https://www.gasd.org/employment', 'www.gasd.org', (42.96451107, -74.1760825)],
['ANDES CENTRAL SCHOOL DISTRICT', '', ' ', (42.1897767021, -74.7873770635)],
['ANDOVER CENTRAL SCHOOL DISTRICT', '', 'www.andovercsd.org', (42.1585810202, -77.7919887782)],
['ARDSLEY UNION FREE SCHOOL DISTRICT', 'http://www.ardsleyschools.org/Page/277', 'www.ardsleyschools.org', (41.0220944933, -73.8336831801)],
['ARGYLE CENTRAL SCHOOL DISTRICT', 'http://www.argylecsd.org/district/job_opportunities', 'www.argylecsd.org', (43.2414022814, -73.484359547)],
['ARKPORT CENTRAL SCHOOL DISTRICT', 'https://www.arkportcsd.org/Page/121', 'www.arkportcsd.org', (42.3947685045, -77.6902614964)],
['ARLINGTON CENTRAL SCHOOL DISTRICT', '', 'www.arlingtonschools.org', (41.6556245142, -73.7774323345)],
['ATTICA CENTRAL SCHOOL DISTRICT', '', 'www.atticacsd.org', (42.8585012074, -78.2641562456)],
['AUBURN CITY SCHOOL DISTRICT', '', 'www.aecsd.education', (42.9136342347, -76.578495806)],
['AUSABLE VALLEY CENTRAL SCHOOL DISTRICT', 'http://www.avcs.org/district-offices/employment-opportunities', 'www.avcs.org', (44.466545327, -73.575154323)]
]


    all_list = [
['ABBOTT UNION FREE SCHOOL DISTRICT', '', 'www.abbottufsd.org', (41.0430933949, -73.8563583389)],
['ADDISON CENTRAL SCHOOL DISTRICT', 'http://www.addisoncsd.org/domain/30', 'www.addisoncsd.org', (42.1001732444, -77.2312078066)],
['ADIRONDACK CENTRAL SCHOOL DISTRICT', 'https://www.adirondackcsd.org/welcome/employment_opportunities', 'www.adirondackcsd.org', (43.4826797831, -75.3367246688)],
['AFTON CENTRAL SCHOOL DISTRICT', 'https://www.aftoncsd.org/Employment1.aspx', 'www.aftoncsd.org', (42.2299678749, -75.527336497)],
['AKRON CENTRAL SCHOOL DISTRICT', 'http://www.akronschools.org/Page/5499', 'www.akronschools.org', (43.0221769248, -78.4938084447)],
['ALBANY CITY SCHOOL DISTRICT', 'https://www.albanyschools.org/employment/index.html', 'www.albanyschools.org', (42.653413081, -73.7543811061)],
['ALBION CENTRAL SCHOOL DISTRICT', 'http://www.albionk12.org/district/district-office/employment/index', 'www.albionk12.org', (43.2393211046, -78.1847900128)],
['ALDEN CENTRAL SCHOOL DISTRICT', 'http://aldenschools.org/Page/25', 'www.aldenschools.org', (42.9030205856, -78.4965127996)],
['ALEXANDER CENTRAL SCHOOL DISTRICT', '', 'www.alexandercsd.org', (42.9020052366, -78.2610842264)],
['ALEXANDRIA CENTRAL SCHOOL DISTRICT', 'http://www.alexandriacentral.org/Page/398', 'www.alexandriacentral.org', (44.3367529522, -75.9099510381)],
['ALFRED-ALMOND CENTRAL SCHOOL DISTRICT', '', 'www.aacs.wnyric.org', (42.294521398, -77.7487625349)],
['ALLEGANY-LIMESTONE CENTRAL SCHOOL DISTRICT', 'http://www.alcsny.org/Page/1695', 'www.alcsny.org', (42.1319816381, -78.5040358743)],
['ALTMAR-PARISH-WILLIAMSTOWN CENTRAL SCHOOL DISTRICT', 'https://www.apwschools.org/Page/1083', 'www.apwschools.org', (43.443596009, -76.053234569)],
['AMAGANSETT UNION FREE SCHOOL DISTRICT', '', 'www.aufsd.org', (40.9768001783, -72.138217828)],
['AMHERST CENTRAL SCHOOL DISTRICT', 'http://www.amherstschools.org/Page/242', 'www.amherstschools.org', (42.9564996874, -78.7919240763)],
['AMITYVILLE UNION FREE SCHOOL DISTRICT', 'http://www.amityvilleschools.org/departments/human_resources', 'www.amityvilleschools.org', (40.6772195098, -73.4179283469)],
['AMSTERDAM CITY SCHOOL DISTRICT', 'https://www.gasd.org/employment', 'www.gasd.org', (42.96451107, -74.1760825)],
['ANDES CENTRAL SCHOOL DISTRICT', '', ' ', (42.1897767021, -74.7873770635)],
['ANDOVER CENTRAL SCHOOL DISTRICT', '', 'www.andovercsd.org', (42.1585810202, -77.7919887782)],
['ARDSLEY UNION FREE SCHOOL DISTRICT', 'http://www.ardsleyschools.org/Page/277', 'www.ardsleyschools.org', (41.0220944933, -73.8336831801)],
['ARGYLE CENTRAL SCHOOL DISTRICT', 'http://www.argylecsd.org/district/job_opportunities', 'www.argylecsd.org', (43.2414022814, -73.484359547)],
['ARKPORT CENTRAL SCHOOL DISTRICT', 'https://www.arkportcsd.org/Page/121', 'www.arkportcsd.org', (42.3947685045, -77.6902614964)],
['ARLINGTON CENTRAL SCHOOL DISTRICT', '', 'www.arlingtonschools.org', (41.6556245142, -73.7774323345)],
['ATTICA CENTRAL SCHOOL DISTRICT', '', 'www.atticacsd.org', (42.8585012074, -78.2641562456)],
['AUBURN CITY SCHOOL DISTRICT', '', 'www.aecsd.education', (42.9136342347, -76.578495806)],
['AUSABLE VALLEY CENTRAL SCHOOL DISTRICT', 'http://www.avcs.org/district-offices/employment-opportunities', 'www.avcs.org', (44.466545327, -73.575154323)],
['AVERILL PARK CENTRAL SCHOOL DISTRICT', 'http://www.averillpark.k12.ny.us/district-information/job-vacancies', 'www.averillpark.k12.ny.us', (42.64464015, -73.572789968)],
['AVOCA CENTRAL SCHOOL DISTRICT', '', 'www.avocacsd.org', (42.4118373642, -77.4163615237)],
['AVON CENTRAL SCHOOL DISTRICT', 'http://www.avoncsd.org/jobs.cfm', 'www.avoncsd.org', (42.906990943, -77.7404484479)],
['BABYLON UNION FREE SCHOOL DISTRICT', 'http://www.babylon.k12.ny.us/our_district/employment', 'http://babylon.k12.ny.us', (40.6994545874, -73.3261094375)],
['BAINBRIDGE-GUILFORD CENTRAL SCHOOL DISTRICT', '', ' ', (42.2933340655, -75.4841952296)],
['BALDWIN UNION FREE SCHOOL DISTRICT', '', 'www.baldwinschools.org', (40.6360899254, -73.6050343627)],
['BALDWINSVILLE CENTRAL SCHOOL DISTRICT', 'http://www.bville.org/teacherpage.cfm?teacher=99', 'www.bville.org', (43.1624672591, -76.3303312898)],
['BALLSTON SPA CENTRAL SCHOOL DISTRICT', '', 'www.bscsd.org', (43.0044979246, -73.846321879)],
['BARKER CENTRAL SCHOOL DISTRICT', 'https://www.barkercsd.net/Page/3945', 'www.barkercsd.net', (43.3346287532, -78.5552117755)],
['BATAVIA CITY SCHOOL DISTRICT', 'http://www.bataviacsd.org/Page/574', 'www.bataviacsd.org', (43.0124045929, -78.1799121147)],
['BATH CENTRAL SCHOOL DISTRICT', 'http://www.bathcsd.org/jobs.cfm', 'www.bathcsd.org', (42.3405838197, -77.3243050226)],
['BAY SHORE UNION FREE SCHOOL DISTRICT', 'https://www.bayshoreschools.org/jobs.cfm', 'www.bayshoreschools.org', (40.731677842, -73.2539371695)],
['BAYPORT-BLUE POINT UNION FREE SCHOOL DISTRICT', 'http://www.bbpschools.org/district_information/human_resources_department', 'www.bbpschools.org', (40.7431017687, -73.0558289208)],
['BEACON CITY SCHOOL DISTRICT', 'http://www.beaconcityk12.org/Page/117', 'www.beaconcityk12.org', (41.4958658551, -73.9719697059)],
['BEAVER RIVER CENTRAL SCHOOL DISTRICT', 'http://www.brcsd.org', 'www.brcsd.org', (43.8859999362, -75.4312250634)],
['BEDFORD CENTRAL SCHOOL DISTRICT', 'http://www.bcsdny.org/Page/134', 'www.bcsdny.org', (41.1892924656, -73.6765472091)],
['BEEKMANTOWN CENTRAL SCHOOL DISTRICT', 'http://www.bcsdk12.org', 'www.bcsdk12.org', (44.772606149, -73.49105192)],
['BELFAST CENTRAL SCHOOL DISTRICT', '', 'www.belfastcsd.org', (42.3414496325, -78.1169753894)],
['BELLEVILLE-HENDERSON CENTRAL SCHOOL DISTRICT', 'http://www.bhpanthers.org/Page/1054', 'www.bhpanthers.org', (43.788766505, -76.117636005)],
['BELLMORE UNION FREE SCHOOL DISTRICT', '', 'www.bellmoreschools.org', (40.6653660979, -73.5249354754)],
['BELLMORE-MERRICK CENTRAL HIGH SCHOOL DISTRICT', '', 'www.bellmore-merrick.k12.ny.us', (40.6881420591, -73.5679297257)],
['BEMUS POINT CENTRAL SCHOOL DISTRICT', 'http://bemusptcsd.org/district/employment_information', 'http://bemusptcsd.org', (42.1609425977, -79.3228883774)],
['BERKSHIRE UNION FREE SCHOOL DISTRICT', '', 'www.berkshirefarm.org', (42.4206567486, -73.4100090449)],
['BERLIN CENTRAL SCHOOL DISTRICT', 'http://berlincentral.org/district/employment', 'www.berlincentral.org', (42.6380991668, -73.3580494183)],
['BERNE-KNOX-WESTERLO CENTRAL SCHOOL DISTRICT', 'https://www.bkwschools.org/employment', 'www.bkwschools.org', (42.625579897, -74.1434515086)],
['BETHLEHEM CENTRAL SCHOOL DISTRICT', 'https://www.bethlehemschools.org/employment', 'www.bethlehemschools.org', (42.6117182515, -73.85710737)],
['BETHPAGE UNION FREE SCHOOL DISTRICT', 'http://www.bethpagecommunity.com/district/employment', 'www.bethpagecommunity.com', (40.7559447013, -73.4842577166)],
['BINGHAMTON CITY SCHOOL DISTRICT', 'http://www.binghamtonschools.org', 'www.binghamtonschools.org', (42.0988642348, -75.9040339629)],
['BLIND BROOK-RYE UNION FREE SCHOOL DISTRICT', 'http://www.blindbrook.org', 'www.blindbrook.org', (41.0303258446, -73.6823918459)],
['BOLIVAR-RICHBURG CENTRAL SCHOOL DISTRICT', 'http://www.brcs.wnyric.org/Page/194', 'www.brcs.wnyric.org', (42.0661548257, -78.1600457447)],
['BOLTON CENTRAL SCHOOL DISTRICT', 'http://www.boltoncsd.org', 'www.boltoncsd.org', (43.5600311604, -73.6555185532)],
['BOQUET VALLEY CENTRAL SCHOOL DISTRICT AT ELIZABETHTOWN-LEWIS-WESTPORT', '', 'www.boquetvalleycsd.org', (0.0, 0.0)],
['BRADFORD CENTRAL SCHOOL DISTRICT', 'https://www.bradfordcsd.org/our-school/employment', 'www.bradfordcsd.org', (42.3668495475, -77.0939356903)],
['BRASHER FALLS CENTRAL SCHOOL DISTRICT', 'http://www.bfcsd.org/apps/spotlightmessages/1776', 'www.bfcsd.org', (44.8032159655, -74.7658727507)],
['BRENTWOOD UNION FREE SCHOOL DISTRICT', '', 'www.brentwood.k12.ny.us', (40.7739017413, -73.2552587908)],
['BREWSTER CENTRAL SCHOOL DISTRICT', '', 'www.brewsterschools.org', (41.437461636, -73.604338716)],
['BRIARCLIFF MANOR UNION FREE SCHOOL DISTRICT', 'http://www.briarcliffschools.org/district-information/human-resources', 'www.briarcliffschools.org', (41.1470545301, -73.8189284586)],
['BRIDGEHAMPTON UNION FREE SCHOOL DISTRICT', 'http://www.bridgehampton.k12.ny.us/district/employment_opportunities', 'www.bridgehampton.k12.ny.us', (40.9375417135, -72.294779156)],
['BRIGHTON CENTRAL SCHOOL DISTRICT', '', ' ', (43.1245136738, -77.5631703215)],
['BROADALBIN-PERTH CENTRAL SCHOOL DISTRICT', 'http://www.bpcsd.org/community/employment', 'www.bpcsd.org', (43.05631402, -74.18796731)],
['BROCKPORT CENTRAL SCHOOL DISTRICT', '', 'www.bcs1.org', (43.2082249594, -77.9455578695)],
['BROCTON CENTRAL SCHOOL DISTRICT', 'http://www.broctoncsd.org/Page/1907', 'www.broctoncsd.org', (42.3834462909, -79.4519534178)],
['BRONXVILLE UNION FREE SCHOOL DISTRICT', 'https://www.bronxvilleschool.org', 'www.bronxvilleschool.org', (40.9368301998, -73.8305548179)],
['BROOKFIELD CENTRAL SCHOOL DISTRICT', 'http://www.brookfieldcsd.org/Page/429', 'www.brookfieldcsd.org', (42.8153391581, -75.314009941)],
['BROOKHAVEN-COMSEWOGUE UNION FREE SCHOOL DISTRICT', '', 'www.comsewogue.k12.ny.us', (40.91640408, -73.069152903)],
['BRUNSWICK CENTRAL SCHOOL DISTRICT (BRITTONKILL)', '', 'www.brunswickcsd.org', (42.7502426395, -73.5707791784)],
['BRUSHTON-MOIRA CENTRAL SCHOOL DISTRICT', 'http://www.bmcsd.org/home/employment-opportunities', 'www.bmcsd.org', (44.8248694023, -74.5210790535)],
['BUFFALO CITY SCHOOL DISTRICT', '', 'www.buffaloschools.org', (42.886675527, -78.8790018392)],
['BURNT HILLS-BALLSTON LAKE CENTRAL SCHOOL DISTRICT', '', 'www.bhbl.org', (42.9119728785, -73.8914373923)],
['BYRAM HILLS CENTRAL SCHOOL DISTRICT', 'https://www.byramhills.org/departments/human-resources/career-opportunities', 'www.byramhills.org', (41.1346030249, -73.6898317415)],
['BYRON-BERGEN CENTRAL SCHOOL DISTRICT', 'http://www.bbschools.org/Employment.aspx', 'www.bbschools.org', (43.0780167161, -78.0033014628)],
['CAIRO-DURHAM CENTRAL SCHOOL DISTRICT', 'http://www.cairodurham.org/jobs', 'www.cairodurham.org', (42.29863825, -73.9966546296)],
['CALEDONIA-MUMFORD CENTRAL SCHOOL DISTRICT', '', 'www.cal-mum.org', (42.9825608976, -77.8565728748)],
['CAMBRIDGE CENTRAL SCHOOL DISTRICT', 'http://www.cambridgecsd.org/domain/23', 'www.cambridgecsd.org', (43.0211319796, -73.3754875366)],
['CAMDEN CENTRAL SCHOOL DISTRICT', 'http://www.camdenschools.org/districtpage.cfm?pageid=1395', 'www.camdenschools.org', (43.3377704832, -75.7455054299)],
['CAMPBELL-SAVONA CENTRAL SCHOOL DISTRICT', '', 'www.cscsd.org', (42.2356225368, -77.2001866894)],
['CANAJOHARIE CENTRAL SCHOOL DISTRICT', 'https://www.canajoharieschools.org/employment', 'www.canajoharieschools.org', (42.89630556, -74.56112147)],
['CANANDAIGUA CITY SCHOOL DISTRICT', '', 'www.canandaiguaschools.org', (42.8899937612, -77.2932177722)],
['CANASERAGA CENTRAL SCHOOL DISTRICT', 'http://www.ccsdny.org/domain/8', 'www.ccsdny.org', (42.4613367919, -77.7773453419)],
['CANASTOTA CENTRAL SCHOOL DISTRICT', 'http://www.canastotacsd.org', 'www.canastotacsd.org', (43.0836492402, -75.746359436)],
['CANDOR CENTRAL SCHOOL DISTRICT', 'http://www.candorcsd.org/index.php/departments/employment', 'www.candorcsd.org', (42.2275298676, -76.3376481227)],
['CANISTEO-GREENWOOD CSD', '', 'www.cgcsd.org', (42.265711886, -77.60947695)],
['CANTON CENTRAL SCHOOL DISTRICT', 'http://www.ccsdk12.org', 'www.ccsdk12.org', (44.6060004199, -75.1691402453)],
['CARLE PLACE UNION FREE SCHOOL DISTRICT', 'http://www.cps.k12.ny.us/departments/oip_employment', 'www.cps.k12.ny.us', (40.7540975705, -73.6053049846)],
['CARMEL CENTRAL SCHOOL DISTRICT', 'http://www.carmelschools.org/groups/6223/personnelpayrollbenefits/employment_opportunities', 'www.carmelschools.org', (41.5080794106, -73.6059784456)],
['CARTHAGE CENTRAL SCHOOL DISTRICT', 'http://www.carthagecsd.org', 'www.carthagecsd.org', (44.0322738598, -75.7195471736)],
['CASSADAGA VALLEY CENTRAL SCHOOL DISTRICT', 'http://cvweb.wnyric.org/Page/998', 'www.cvweb.wnyric.org', (42.2546593968, -79.2834034392)],
['CATO-MERIDIAN CENTRAL SCHOOL DISTRICT', 'http://www.catomeridian.org/districtpage.cfm?pageid=1350', 'www.catomeridian.org', (43.1740673877, -76.5512703213)],
['CATSKILL CENTRAL SCHOOL DISTRICT', 'https://catskillcsd.org/employment', 'www.catskillcsd.org', (42.219189867, -73.870227092)],
['CATTARAUGUS-LITTLE VALLEY CENTRAL SCHOOL DISTRICT', 'https://www.cattlv.wnyric.org/Page/20', 'www.cattlv.wnyric.org', (42.3344917045, -78.8617485598)],
['CAZENOVIA CENTRAL SCHOOL DISTRICT', '', 'www.caz.cnyric.org', (42.93417987, -75.8580478318)],
['CENTER MORICHES UNION FREE SCHOOL DISTRICT', '', 'www.cmschools.org', (40.800503155, -72.7983995774)],
['CENTRAL ISLIP UNION FREE SCHOOL DISTRICT', 'http://www.centralislip.k12.ny.us', 'www.centralislip.k12.ny.us', (40.7929917593, -73.2056288836)],
['CENTRAL SQUARE CENTRAL SCHOOL DISTRICT', '', 'www.cssd.org', (43.281990786, -76.1504426172)],
['CENTRAL VALLEY CSD AT ILION-MOHAWK', 'https://www.cvalleycsd.org/human-resources', 'www.cvalleycsd.org', (43.007256012, -75.0429160618)],
['CHAPPAQUA CENTRAL SCHOOL DISTRICT', '', 'www.ccsd.ws', (41.1760705272, -73.7542933985)],
['CHARLOTTE VALLEY CENTRAL SCHOOL DISTRICT', 'http://www.charlottevalleycs.org/district/employment_opportunities', 'www.charlottevalleycs.org', (42.5144200193, -74.8655150463)],
['CHATEAUGAY CENTRAL SCHOOL DISTRICT', 'http://www.chateaugaycsd.org/employment', 'www.chateaugaycsd.org', (44.9295065656, -74.0787897327)],
['CHATHAM CENTRAL SCHOOL DISTRICT', 'http://www.chathamcentralschools.com/district/employment', 'www.chathamcentralschools.com', (42.3588147955, -73.6033299287)],
['CHAUTAUQUA LAKE CENTRAL SCHOOL DISTRICT', 'https://www.clake.org/District/1748-Untitled.html', 'www.clake.org', (42.2581404911, -79.5144812154)],
['CHAZY UNION FREE SCHOOL DISTRICT', 'https://ccrsk12.org/opportunities', 'www.ccrsk12.org', (44.8868945009, -73.4341276343)],
['CHEEKTOWAGA CENTRAL SCHOOL DISTRICT', 'http://www.cheektowagacentral.org', 'www.cheektowagacentral.org', (42.9109408937, -78.7544257004)],
['CHEEKTOWAGA-MARYVALE UNION FREE SCHOOL DISTRICT', '', 'www.maryvaleufsd.org', (42.9332784338, -78.7499177461)],
['CHEEKTOWAGA-SLOAN UNION FREE SCHOOL DISTRICT', '', 'www.cheektowagasloan.org', (42.894718524, -78.7943358536)],
['CHENANGO FORKS CENTRAL SCHOOL DISTRICT', 'https://www.cforks.org/Employment.aspx', 'www.cforks.org', (42.1924874833, -75.8532211232)],
['CHENANGO VALLEY CENTRAL SCHOOL DISTRICT', 'http://www.cvcsd.stier.org', 'www.cvcsd.stier.org', (42.1625636424, -75.8724986608)],
['CHERRY VALLEY-SPRINGFIELD CENTRAL SCHOOL DISTRICT', 'https://www.cvscs.org/EmploymentOpportunities.aspx', 'www.cvscs.org', (42.814507778, -74.7699553092)],
['CHESTER UNION FREE SCHOOL DISTRICT', '', 'www.chesterufsd.org', (41.3664565584, -74.2779744736)],
['CHITTENANGO CENTRAL SCHOOL DISTRICT', 'http://www.chittenangoschools.org', 'www.chittenangoschools.org', (43.0865752612, -75.8752618008)],
['CHURCHVILLE-CHILI CENTRAL SCHOOL DISTRICT', '', 'www.cccsd.org', (43.1211938544, -77.8312254935)],
['CINCINNATUS CENTRAL SCHOOL DISTRICT', 'http://www.cc.cnyric.org/districtpage.cfm?pageid=65', 'www.cc.cnyric.org', (42.5428400243, -75.8956067611)],
['CLARENCE CENTRAL SCHOOL DISTRICT', 'http://www.clarenceschools.org/Page/3205', 'www.clarenceschools.org', (42.9721056079, -78.631966058)],
['CLARKSTOWN CENTRAL SCHOOL DISTRICT', 'http://www.ccsd.edu/domain/999', 'www.ccsd.edu', (41.1244217222, -74.0034185664)],
['CLEVELAND HILL UNION FREE SCHOOL DISTRICT', '', 'www.clevehill.org', (42.9411549637, -78.781613545)],
['CLIFTON-FINE CENTRAL SCHOOL DISTRICT', 'http://www.cliftonfine.org/cliftonfine.org/district/employment', 'www.cliftonfine.org', (44.1635356668, -75.0453164278)],
['CLINTON CENTRAL SCHOOL DISTRICT', 'http://www.ccs.edu/Page/228', 'www.ccs.edu', (43.049317112, -75.3813995372)],
['CLYDE-SAVANNAH CENTRAL SCHOOL DISTRICT', 'http://www.clydesavannah.org/district/employment_opportunities', 'www.clydesavannah.org', (43.0884213531, -76.8625773716)],
['CLYMER CENTRAL SCHOOL DISTRICT', '', 'www.clymercsd.org', (42.0228717728, -79.6256265858)],
['COBLESKILL-RICHMONDVILLE CENTRAL SCHOOL DISTRICT', '', 'www.crcs.k12.ny.us', (42.6796749127, -74.4968652197)],
['COHOES CITY SCHOOL DISTRICT', '', 'www.cohoes.org', (42.7743002601, -73.691606436)],
['COLD SPRING HARBOR CENTRAL SCHOOL DISTRICT', 'http://www.csh.k12.ny.us/domain/49', 'www.csh.k12.ny.us', (40.8799617274, -73.4526587565)],
['COLTON-PIERREPONT CENTRAL SCHOOL DISTRICT', '', 'www.cpcs.us', (44.5571461333, -74.9454790769)],
['COMMACK UNION FREE SCHOOL DISTRICT', '', 'commack.k12.ny.us', (40.8687814735, -73.2925637604)],
['CONNETQUOT CENTRAL SCHOOL DISTRICT', 'http://www.ccsdli.org/staff_resources/employment', 'www.ccsdli.org', (40.7601991793, -73.1174144059)],
['COOPERSTOWN CENTRAL SCHOOL DISTRICT', 'https://www.cooperstowncs.org/o/cooperstown-csd/page/employment-information--13', 'www.cooperstowncs.org', (42.6904261001, -74.9342696774)],
['COPENHAGEN CENTRAL SCHOOL DISTRICT', 'http://www.ccsknights.org', 'www.ccsknights.org', (43.8919839127, -75.6772144289)],
['COPIAGUE UNION FREE SCHOOL DISTRICT', 'http://www.copiague.k12.ny.us/our_district/employment', 'www.copiague.k12.ny.us', (40.6888574554, -73.4024296121)],
['CORINTH CENTRAL SCHOOL DISTRICT', '', ' ', (43.2428536964, -73.8267913806)],
['CORNING CITY SCHOOL DISTRICT', 'http://www.corningareaschools.com/content/vacai', 'www.corningareaschools.com', (42.1616471341, -77.0941766804)],
['CORNWALL CENTRAL SCHOOL DISTRICT', 'https://www.cornwallschools.com/apps/pages/index.jsp?uREC_ID=310699&type=d&termREC_ID=&pREC_ID=577553', 'www.cornwallschools.com', (41.4460151999, -74.0164347302)],
['CORTLAND CITY SCHOOL DISTRICT', 'http://www.cortlandschools.org/teacherpage.cfm?teacher=814', 'www.cortlandschools.org', (42.5884722868, -76.1796701609)],
['COXSACKIE-ATHENS CENTRAL SCHOOL DISTRICT', '', 'www.cacsd.org', (42.3508024167, -73.8085230973)],
['CROTON-HARMON UNION FREE SCHOOL DISTRICT', '', 'www.chufsd.org', (41.2101692196, -73.8753175019)],
['CROWN POINT CENTRAL SCHOOL DISTRICT', 'http://www.cpcsteam.org/district/employment', 'www.cpcsteam.org', (43.9531311041, -73.4295585752)],
['CUBA-RUSHFORD CENTRAL SCHOOL DISTRICT', '', 'www.crcs.wnyric.org', (42.2366367863, -78.2702252539)],
['DALTON-NUNDA CENTRAL SCHOOL DISTRICT (KESHEQUA)', '', 'www.keshequa.org', (42.5793590567, -77.9415078189)],
['DANSVILLE CENTRAL SCHOOL DISTRICT', 'https://www.dansvillecsd.org/Page/2394', 'www.dansvillecsd.org', (0.0, 0.0)],
['DEER PARK UNION FREE SCHOOL DISTRICT', 'http://www.deerparkschools.org/staff/job_opportunities', 'www.deerparkschools.org', (40.7606699786, -73.3286723026)],
['DELAWARE ACADEMY CENTRAL SCHOOL DISTRICT AT DELHI', 'http://www.delhischools.org', 'www.delhischools.org', (42.2736910982, -74.9159740948)],
['DEPEW UNION FREE SCHOOL DISTRICT', 'http://www.depewschools.org', 'www.depewschools.org', (42.8957736891, -78.6967920469)],
['DEPOSIT CENTRAL SCHOOL DISTRICT', 'http://www.depositcsd.org', 'www.depositcsd.org', (42.066755064, -75.4190100999)],
['DERUYTER CENTRAL SCHOOL DISTRICT', '', 'www.deruytercentral.org', (42.757653622, -75.8909463262)],
['DOBBS FERRY UNION FREE SCHOOL DISTRICT', 'http://www.dfsd.org/domain/239', 'www.dfsd.org', (41.0176581557, -73.8703268162)],
['DOLGEVILLE CENTRAL SCHOOL DISTRICT', 'http://www.dolgeville.org', 'www.dolgeville.org', (43.1021968787, -74.7761070218)],
['DOVER UNION FREE SCHOOL DISTRICT', '', 'www.doverschools.org', (41.6864476309, -73.5738741862)],
['DOWNSVILLE CENTRAL SCHOOL DISTRICT', 'https://www.dcseagles.org/employment.aspx', 'www.dcseagles.org', (42.0776349634, -74.998066602)],
['DRYDEN CENTRAL SCHOOL DISTRICT', '', 'www.dcsd-ny.schoolloop.com', (42.5006568271, -76.3110406746)],
['DUANESBURG CENTRAL SCHOOL DISTRICT', 'https://www.duanesburg.org', 'www.duanesburg.org', (42.748816447, -74.1867721633)],
['DUNDEE CENTRAL SCHOOL DISTRICT', 'http://www.dundeecs.org/staff/job_opportunities', 'www.dundeecs.org', (42.5269515286, -76.9733674552)],
['DUNKIRK CITY SCHOOL DISTRICT', 'http://www.dunkirkcsd.org', 'www.dunkirkcsd.org', (42.477189217, -79.340828791)],
['EAST AURORA UNION FREE SCHOOL DISTRICT', 'http://www.eastauroraschools.org/domain/56', 'www.eastauroraschools.org', (42.7686646183, -78.6187129943)],
['EAST BLOOMFIELD CENTRAL SCHOOL DISTRICT', 'http://www.bloomfieldcsd.org/apps/jobs', 'www.bloomfieldcsd.org', (42.8968808913, -77.4186814538)],
['EAST GREENBUSH CENTRAL SCHOOL DISTRICT', 'http://egcsd.org/departments/personnel-and-professional-development/employment', 'www.egcsd.org', (42.6005213908, -73.706328591)],
['EAST HAMPTON UNION FREE SCHOOL DISTRICT', '', 'www.ehufsd.org', (40.9685058206, -72.2005764444)],
['EAST IRONDEQUOIT CENTRAL SCHOOL DISTRICT', '', 'www.eastiron.org', (43.1872805869, -77.5524077073)],
['EAST ISLIP UNION FREE SCHOOL DISTRICT', 'http://www.eischools.org/district/personnel_services', 'www.eischools.org', (40.7587250438, -73.1751100261)],
['EAST MEADOW UNION FREE SCHOOL DISTRICT', 'http://www.eastmeadow.k12.ny.us/our_district/human_resources', 'www.eastmeadow.k12.ny.us', (40.7428876806, -73.5697741854)],
['EAST MORICHES UNION FREE SCHOOL DISTRICT', 'http://www.emoschools.org/Employment.aspx', 'www.emoschools.org', (40.8025333736, -72.7634168368)],
['EAST QUOGUE UNION FREE SCHOOL DISTRICT', 'http://www.eastquogue.k12.ny.us', 'www.eastquogue.k12.ny.us', (40.8452616973, -72.5861990055)],
['EAST RAMAPO CENTRAL SCHOOL DISTRICT (SPRING VALLEY)', '', 'https://www.ercsd.org/', (41.1028616739, -74.0496985242)],
['EAST ROCHESTER UNION FREE SCHOOL DISTRICT', '', 'www.erschools.org', (43.1078675844, -77.4890859885)],
['EAST ROCKAWAY UNION FREE SCHOOL DISTRICT', 'http://www.eastrockawayschools.org/district/employment', 'www.eastrockawayschools.org', (40.645940635, -73.6585553822)],
['EAST SYRACUSE MINOA CENTRAL SCHOOL DISTRICT', 'http://www.esmschools.org/district.cfm?subpage=24415', 'www.esmschools.org', (43.0663459589, -76.0304875651)],
['EAST WILLISTON UNION FREE SCHOOL DISTRICT', 'http://www.ewsdonline.org', 'www.ewsdonline.org', (40.7618395446, -73.6172457461)],
['EASTCHESTER UNION FREE SCHOOL DISTRICT', '', 'http://district.eastchesterschools.org', (40.9623555587, -73.8102911149)],
['EASTPORT-SOUTH MANOR CSD', 'http://www.esmonline.org', 'www.esmonline.org', (40.8392224726, -72.830413686)],
['EDEN CENTRAL SCHOOL DISTRICT', 'http://www.edencsd.org/Page/10', 'www.edencsd.org', (42.6609022314, -78.8910817788)],
['EDGEMONT UNION FREE SCHOOL DISTRICT', 'http://www.edgemont.org/district/human-resources/employment', 'www.edgemont.org', (41.0008080131, -73.80925805)],
['EDINBURG COMMON SCHOOL DISTRICT', 'http://www.edinburgcs.org/employment-opportunities.html', 'www.edinburgcs.org', (43.2211268988, -74.1255999395)],
['EDMESTON CENTRAL SCHOOL DISTRICT', 'http://www.edmestoncentralschool.net/job-of-the-week', 'www.edmestoncentralschool.net', (42.6984648599, -75.2442322654)],
['EDWARDS-KNOX CENTRAL SCHOOL DISTRICT', 'http://www.ekcsk12.org/domain/134', 'www.ekcsk12.org', (44.3639876235, -75.201189691)],
['ELBA CENTRAL SCHOOL DISTRICT', 'http://www.elbacsd.org/domain/47', 'www.elbacsd.org', (43.0744898999, -78.188994193)],
['ELDRED CENTRAL SCHOOL DISTRICT', '', 'www.eldred.k12.ny.us', (41.5299839648, -74.8806765051)],
['ELLENVILLE CENTRAL SCHOOL DISTRICT', 'http://www.ecs.k12.ny.us', 'www.ecs.k12.ny.us', (41.7179562031, -74.3899471522)],
['ELLICOTTVILLE CENTRAL SCHOOL DISTRICT', 'http://www.ellicottvillecentral.com', 'www.ellicottvillecentral.com', (42.3282920856, -78.6718188714)],
['ELMIRA CITY SCHOOL DISTRICT', 'http://www.elmiracityschools.com', 'www.elmiracityschools.com', (42.0970058476, -76.8291123501)],
['ELMIRA HEIGHTS CENTRAL SCHOOL DISTRICT', 'http://www.heightsschools.com', 'www.heightsschools.com', (42.1230425416, -76.8251242321)],
['ELMONT UNION FREE SCHOOL DISTRICT', '', 'www.elmontschools.org', (40.7063445052, -73.7101583189)],
['ELMSFORD UNION FREE SCHOOL DISTRICT', '', 'www.eufsd.org', (41.0506605844, -73.8174398224)],
['ELWOOD UNION FREE SCHOOL DISTRICT', 'http://www.elwood.k12.ny.us/departments/human_resources', 'www.elwood.k12.ny.us', (40.8572848517, -73.3400051695)],
['EVANS-BRANT CENTRAL SCHOOL DISTRICT (LAKE SHORE)', '', 'www.lakeshorecsd.org', (42.649278203, -79.0377211751)],
['FABIUS-POMPEY CENTRAL SCHOOL DISTRICT', 'http://www.fabiuspompey.org', 'www.fabiuspompey.org', (42.8303475704, -75.9846529977)],
['FAIRPORT CENTRAL SCHOOL DISTRICT', '', 'www.fairport.org', (43.0990643605, -77.4449703566)],
['FALCONER CENTRAL SCHOOL DISTRICT', '', 'www.falconerschools.org', (42.124101389, -79.193366016)],
['FALLSBURG CENTRAL SCHOOL DISTRICT', 'http://www.fallsburgcsd.net', 'www.fallsburgcsd.net', (41.7326290823, -74.6142202825)],
['FARMINGDALE UNION FREE SCHOOL DISTRICT', 'http://www.farmingdaleschools.org/domain/2290', 'www.farmingdaleschools.org', (40.7324265573, -73.4391681213)],
['FAYETTEVILLE-MANLIUS CENTRAL SCHOOL DISTRICT', 'http://www.fmschools.org/departments-services/employment', 'www.fmschools.org', (43.007382212, -75.9597612064)],
['FILLMORE CENTRAL SCHOOL DISTRICT', 'http://www.fillmorecsd.org/domain/209', 'www.fillmorecsd.org', (42.4653716695, -78.1187417376)],
['FIRE ISLAND UNION FREE SCHOOL DISTRICT', 'http://www.fi.k12.ny.us/district/employment', 'www.fi.k12.ny.us', (40.6458198795, -73.159942129)],
['FISHERS ISLAND UNION FREE SCHOOL DISTRICT', 'http://www.fischool.com', 'www.fischool.com', (41.25555328, -72.031189)],
['FLORAL PARK-BELLEROSE UNION FREE SCHOOL DISTRICT', 'http://www.floralpark.k12.ny.us/Page/1164', 'www.floralpark.k12.ny.us', (40.7202817851, -73.7203487219)],
['FLORIDA UNION FREE SCHOOL DISTRICT', '', 'www.floridaufsd.org', (41.3335746631, -74.3567174697)],
['FONDA-FULTONVILLE CENTRAL SCHOOL DISTRICT', 'https://www.fondafultonvilleschools.org/about/employment', 'www.fondafultonvilleschools.org', (42.9596013242, -74.3663539338)],
['FORESTVILLE CENTRAL SCHOOL DISTRICT', 'https://www.forestville.com/domain/10', 'www.forestville.com', (42.4651716427, -79.1798567394)],
['FORT ANN CENTRAL SCHOOL DISTRICT', 'http://www.fortannschool.org/district/job_opportunities', 'www.fortannschool.org', (43.4104930047, -73.4915426213)],
['FORT EDWARD UNION FREE SCHOOL DISTRICT', 'http://www.fortedward.org', 'www.fortedward.org', (43.2729840104, -73.5851866024)],
['FORT PLAIN CENTRAL SCHOOL DISTRICT', 'http://www.fortplain.org/contact-us/employment', 'www.fortplain.org', (42.9335967197, -74.6337685834)],
['FRANKFORT-SCHUYLER CENTRAL SCHOOL DISTRICT', 'http://www.frankfort-schuyler.org/Page/47', 'www.frankfort-schuyler.org', (43.0312463074, -75.0722573387)],
['FRANKLIN CENTRAL SCHOOL DISTRICT', 'https://www.franklincsd.org/Employment.aspx', 'www.franklincsd.org', (42.3385656932, -75.1679603928)],
['FRANKLIN SQUARE UNION FREE SCHOOL DISTRICT', 'http://www.franklinsquare.k12.ny.us', 'www.franklinsquare.k12.ny.us', (40.7116648192, -73.667992823)],
['FRANKLINVILLE CENTRAL SCHOOL DISTRICT', 'http://www.tbafcs.org/Page/1444', 'www.tbafcs.org', (42.3400784795, -78.4559970852)],
['FREDONIA CENTRAL SCHOOL DISTRICT', 'http://www.fredonia.wnyric.org/Page/80', 'www.fredonia.wnyric.org', (42.4294663876, -79.3465448365)],
['FREEPORT UNION FREE SCHOOL DISTRICT', 'http://www.freeportschools.org/district/employment_opportunities', 'www.freeportschools.org', (40.6645417756, -73.5895287591)],
['FREWSBURG CENTRAL SCHOOL DISTRICT', 'http://www.frewsburgcsd.org/domain/146', 'www.frewsburgcsd.org', (42.0564717361, -79.1604267235)],
['FRIENDSHIP CENTRAL SCHOOL DISTRICT', 'http://www.friendship.wnyric.org/Page/39', 'www.friendship.wnyric.org', (42.2063523878, -78.135566507)],
['FRONTIER CENTRAL SCHOOL DISTRICT', 'http://www.frontier.wnyric.org/Page/118', 'www.frontier.wnyric.org', (42.7473136032, -78.9003148338)],
['FULTON CITY SCHOOL DISTRICT', '', 'www.fulton.cnyric.org', (43.3022722325, -76.4196355363)],
['GALWAY CENTRAL SCHOOL DISTRICT', 'http://www.galwaycsd.org', 'www.galwaycsd.org', (43.0238169932, -74.0344813822)],
['GANANDA CENTRAL SCHOOL DISTRICT', 'http://www.gananda.org/apps/jobs', 'www.gananda.org', (43.1246862412, -77.3076079335)],
['GARDEN CITY UNION FREE SCHOOL DISTRICT', '', 'www.gardencity.k12.ny.us', (40.723351801, -73.6425487438)],
['GARRISON UNION FREE SCHOOL DISTRICT', 'http://www.gufs.org', 'www.gufs.org', (41.3808316533, -73.9376285511)],
['GATES-CHILI CENTRAL SCHOOL DISTRICT', '', 'www.gateschili.org', (43.153395217, -77.7099259908)],
['GENERAL BROWN CENTRAL SCHOOL DISTRICT', 'http://www.gblions.org/Page/67', 'www.gblions.org', (44.0146626141, -76.0194106941)],
['GENESEE VALLEY CENTRAL SCHOOL DISTRICT', 'https://www.genvalley.org/Page/49', 'www.genvalley.org', (42.2333892092, -78.0322240018)],
['GENESEO CENTRAL SCHOOL DISTRICT', '', 'www.geneseocsd.org', (42.8115043714, -77.8051517994)],
['GENEVA CITY SCHOOL DISTRICT', 'http://www.genevacsd.org/Page/285', 'www.genevacsd.org', (42.8771422309, -76.9964996948)],
['GEORGE JUNIOR REPUBLIC UNION FREE SCHOOL DISTRICT', '', 'www.georgejuniorrepublic.com', (42.5066746011, -76.3330484618)],
['GEORGETOWN-SOUTH OTSELIC CENTRAL SCHOOL DISTRICT', 'http://www.ovcs.org', 'www.ovcs.org', (42.6500914553, -75.7859679311)],
['GERMANTOWN CENTRAL SCHOOL DISTRICT', 'http://www.germantowncsd.org/Page/71', 'www.germantowncsd.org', (42.1335336197, -73.8897012)],
['GILBERTSVILLE-MOUNT UPTON CENTRAL SCHOOL DISTRICT', 'https://www.gmucsd.org/Employment.aspx', 'www.gmucsd.org', (42.4418909694, -75.3453100898)],
['GILBOA-CONESVILLE CENTRAL SCHOOL DISTRICT', 'http://gilboa-conesville.k12.ny.us/our_school/Job_Vacancies', 'www.gilboa-conesville.k12.ny.us', (42.3924436264, -74.4383949553)],
['GLEN COVE CITY SCHOOL DISTRICT', 'http://www.glencove.k12.ny.us/staff_resources/employment', 'www.glencove.k12.ny.us', (40.8790020533, -73.62969285)],
['GLENS FALLS CITY SCHOOL DISTRICT', '', 'www.gfsd.org', (43.3106212155, -73.6591985106)],
['GLENS FALLS COMMON SCHOOL DISTRICT', 'https://www.abewing.org/aws', 'www.abewing.org', (43.3149112123, -73.632258559)],
['GLOVERSVILLE CITY SCHOOL DISTRICT', 'https://www.gesdk12.org/employment', 'www.gesdk12.org', (43.05377222, -74.36098794)],
['GORHAM-MIDDLESEX CENTRAL SCHOOL DISTRICT (MARCUS WHITMAN)', '', 'www.mwcsd.org', (42.7792315197, -77.2241211149)],
['GOSHEN CENTRAL SCHOOL DISTRICT', '', 'www.goshenschoolsny.org', (41.404424524, -74.319902227)],
['GOUVERNEUR CENTRAL SCHOOL DISTRICT', 'http://www.gcsk12.org/about-us/employment', 'www.gcsk12.org', (44.341032398, -75.465382444)],
['GOWANDA CENTRAL SCHOOL DISTRICT', '', 'www.gowcsd.org', (42.465360727, -78.947584837)],
['GRAND ISLAND CENTRAL SCHOOL DISTRICT', '', 'www.grandislandschools.org', (43.0370529698, -78.9333933658)],
['GRANVILLE CENTRAL SCHOOL DISTRICT', 'http://www.granvillecsd.org/Page/27', 'www.granvillecsd.org', (43.4011170107, -73.2633232563)],
['GREAT NECK UNION FREE SCHOOL DISTRICT', 'http://www.greatneck.k12.ny.us/Page/3453', 'www.greatneck.k12.ny.us', (40.7653117641, -73.7013687322)],
['GREECE CENTRAL SCHOOL DISTRICT', '', 'www.greececsd.org', (43.2254461095, -77.6634726789)],
['GREEN ISLAND UNION FREE SCHOOL DISTRICT', '', 'www.greenisland.org', (42.7457681106, -73.6897409101)],
['GREENBURGH CENTRAL SCHOOL DISTRICT', 'https://www.greenburghcsd.org/domain/45', 'www.greenburghcsd.org', (41.0325705297, -73.8089413941)],
['GREENBURGH ELEVEN UNION FREE SCHOOL DISTRICT', 'http://www.greenburgheleven.org/employment.html', 'www.greenburgheleven.org', (41.0124950071, -73.869975069)],
['GREENBURGH-GRAHAM UNION FREE SCHOOL DISTRICT', '', 'www.greenburghgraham.org', (40.9785155985, -73.8807835145)],
['GREENBURGH-NORTH CASTLE UNION FREE SCHOOL DISTRICT', 'http://www.greenburghnorthcastleschools.com', 'www.greenburghnorthcastleschools.com', (41.0062103634, -73.8795411146)],
['GREENE CENTRAL SCHOOL DISTRICT', 'http://www.greenecsd.org', 'www.greenecsd.org', (42.3264530183, -75.7746993325)],
['GREENPORT UNION FREE SCHOOL DISTRICT', '', 'www.gufsd.org', (41.1003951096, -72.3692457164)],
['GREENVILLE CENTRAL SCHOOL DISTRICT', '', 'www.greenvillecsd.org', (42.4182929099, -74.0268478725)],
['GREENWICH CENTRAL SCHOOL DISTRICT', 'http://wps.greenwichcsd.org/employment', 'www.greenwichcsd.org', (43.0968677971, -73.4975084562)],
['GREENWOOD LAKE UNION FREE SCHOOL DISTRICT', 'http://www.gwlufsd.org/domain/41', 'www.gwlufsd.org', (41.2676008654, -74.2574867565)],
['GROTON CENTRAL SCHOOL DISTRICT', 'http://www.grotoncs.org/districtpage.cfm?pageid=1407', 'www.grotoncs.org', (42.5806350385, -76.370396014)],
['GUILDERLAND CENTRAL SCHOOL DISTRICT', 'http://www.guilderlandschools.org', 'www.guilderlandschools.org', (42.697423431, -73.966180622)],
['HADLEY-LUZERNE CENTRAL SCHOOL DISTRICT', 'http://www.hlcs.org/?DivisionID=22236&ToggleSideNav=ShowAll', 'www.hlcs.org', (43.3439611725, -73.8410885309)],
['HALDANE CENTRAL SCHOOL DISTRICT', 'https://www.haldaneschool.org/departments/employment-resources/employment-opportunities', 'www.haldaneschool.org', (41.4227616509, -73.9558085807)],
['HALF HOLLOW HILLS CENTRAL SCHOOL DISTRICT', 'http://www.halfhollowhills.k12.ny.us/district/career-opportunities', 'www.halfhollowhills.k12.ny.us', (40.799145379, -73.35778078)],
['HAMBURG CENTRAL SCHOOL DISTRICT', 'http://www.hamburgschools.org/Page/251', 'www.hamburgschools.org', (42.7424983579, -78.7978258213)],
['HAMILTON CENTRAL SCHOOL DISTRICT', 'http://www.hamiltoncentral.org/domain/66', 'www.hamiltoncentral.org', (42.8210792342, -75.5473872567)],
['HAMMOND CENTRAL SCHOOL DISTRICT', '', 'www.hammond.sllboces.org', (44.4451493691, -75.6974820437)],
['HAMMONDSPORT CENTRAL SCHOOL DISTRICT', 'http://www.hammondsportcsd.org/domain/65', 'www.hammondsportcsd.org', (42.4031153297, -77.2207644961)],
['HAMPTON BAYS UNION FREE SCHOOL DISTRICT', 'http://www.hbschools.us/district/employment', 'www.hbschools.us', (40.8714868424, -72.5288291247)],
['HANCOCK CENTRAL SCHOOL DISTRICT', 'https://www.hancock.stier.org/Employment.aspx', 'www.hancock.stier.org', (41.95790996, -75.2809410322)],
['HANNIBAL CENTRAL SCHOOL DISTRICT', 'http://www.hannibalcsd.org', 'www.hannibalcsd.org', (43.3178133446, -76.578235732)],
['HARBORFIELDS CENTRAL SCHOOL DISTRICT', 'http://www.harborfieldscsd.net/employment/employment_opportunities', 'www.harborfieldscsd.net', (40.8723635953, -73.3794163179)],
['HARPURSVILLE CENTRAL SCHOOL DISTRICT', 'https://www.hcs.stier.org/employment.aspx', 'www.hcs.stier.org', (42.1813215707, -75.6200179606)],
['HARRISON CENTRAL SCHOOL DISTRICT', 'http://www.harrisoncsd.org/index.php/current-job-vacancies/certificated-openings', 'www.harrisoncsd.org', (40.9788158974, -73.7180562468)],
['HARRISVILLE CENTRAL SCHOOL DISTRICT', 'https://www.hcsk12.org/Page/194', 'www.hcsk12.org', (44.1603446789, -75.3217850862)],
['HARTFORD CENTRAL SCHOOL DISTRICT', 'http://www.hartfordcsd.org/Page/797', 'www.hartfordcsd.org', (43.3606260804, -73.3962710559)],
['HASTINGS-ON-HUDSON UNION FREE SCHOOL DISTRICT', '', 'www.hohschools.org', (40.9944424412, -73.8777324131)],
['HAUPPAUGE UNION FREE SCHOOL DISTRICT', 'http://www.hauppauge.k12.ny.us/Page/2668', 'www.hauppauge.k12.ny.us', (40.8226417194, -73.1847588545)],
['HAVERSTRAW-STONY POINT CSD (NORTH ROCKLAND)', 'http://www.nrcsd.org/hr', 'www.nrcsd.org', (41.21157211, -73.99605094)],
['HAWTHORNE-CEDAR KNOLLS UNION FREE SCHOOL DISTRICT', 'http://www.hcks.org/district/human-resources', 'www.hcks.org', (41.1032399705, -73.7870712901)],
['HEMPSTEAD UNION FREE SCHOOL DISTRICT', 'http://www.hempsteadschools.org/Page/120', 'www.hempsteadschools.org', (40.7045017836, -73.6192086846)],
['HENDRICK HUDSON CENTRAL SCHOOL DISTRICT', 'http://www.henhudschools.org/domain/1148', 'www.henhudschools.org', (41.2529671222, -73.9363846073)],
['HERKIMER CENTRAL SCHOOL DISTRICT', '', 'www.herkimercsd.org', (43.0238375049, -75.0011328462)],
['HERMON-DEKALB CENTRAL SCHOOL DISTRICT', 'https://www.hdcsk12.org/Page/29', 'www.hdcsk12.org', (44.4826431042, -75.3033710335)],
['HERRICKS UNION FREE SCHOOL DISTRICT', 'http://www.herricks.org/Page/167', 'www.herricks.org', (40.7590155775, -73.6604128045)],
['HEUVELTON CENTRAL SCHOOL DISTRICT', '', 'www.heuvelton.schoolfusion.us', (44.6211278491, -75.4090711137)],
['HEWLETT-WOODMERE UNION FREE SCHOOL DISTRICT', 'http://www.hewlett-woodmere.net', 'www.hewlett-woodmere.net', (40.6328817481, -73.7052887411)],
['HICKSVILLE UNION FREE SCHOOL DISTRICT', 'http://www.hicksvillepublicschools.org', 'www.hicksvillepublicschools.org', (40.7578383381, -73.524824847)],
['HIGHLAND CENTRAL SCHOOL DISTRICT', 'http://www.highland-k12.org/Page/23', 'www.highland-k12.org', (41.7244775322, -74.0121694747)],
['HIGHLAND FALLS CENTRAL SCHOOL DISTRICT', 'http://www.hffmcsd.org/Page/66', 'www.hffmcsd.org', (41.3513905178, -73.9754334503)],
['HILTON CENTRAL SCHOOL DISTRICT', '', 'www.hilton.k12.ny.us', (43.2870369484, -77.8004711272)],
['HINSDALE CENTRAL SCHOOL DISTRICT', 'http://www.hinsdalebobcats.org/Page/107', 'www.hinsdalebobcats.org', (42.1566252893, -78.396220889)],
['HOLLAND CENTRAL SCHOOL DISTRICT', '', 'www.hollandcsd.org', (42.6445971332, -78.540810521)],
['HOLLAND PATENT CENTRAL SCHOOL DISTRICT', 'http://www.hpschools.org/Page/1693', 'www.hpschools.org', (43.2432380291, -75.2542293956)],
['HOLLEY CENTRAL SCHOOL DISTRICT', 'http://www.holleycsd.org/JobOpportunities1.aspx', 'www.holleycsd.org', (43.2338788091, -78.0266007592)],
['HOMER CENTRAL SCHOOL DISTRICT', 'http://www1.homercentral.org/district/employment', 'www.homercentral.org', (42.63045014, -76.190780107)],
['HONEOYE CENTRAL SCHOOL DISTRICT', 'http://www.honeoye.org/apps/jobs', 'www.honeoye.org', (42.7904189182, -77.5029227887)],
['HONEOYE FALLS-LIMA CENTRAL SCHOOL DISTRICT', '', 'www.hflcsd.org', (42.9511888061, -77.5870435175)],
['HOOSIC VALLEY CENTRAL SCHOOL DISTRICT', 'http://www.hoosicvalley.k12.ny.us/district/jobs', 'www.hoosicvalley.k12.ny.us', (42.907211288, -73.5803286217)],
['HOOSICK FALLS CENTRAL SCHOOL DISTRICT', '', 'www.hoosickfallscsd.org', (42.8750116703, -73.355647815)],
['HOPEVALE UNION FREE SCHOOL DISTRICT AT HAMBURG', '', ' ', (42.7579023765, -78.8450615911)],
['HORNELL CITY SCHOOL DISTRICT', '', 'www.hornellcityschools.com', (0.0, 0.0)],
['HORSEHEADS CENTRAL SCHOOL DISTRICT', 'http://www.horseheadsdistrict.com', 'www.horseheadsdistrict.com', (42.1617277704, -76.8232675119)],
['HUDSON CITY SCHOOL DISTRICT', 'http://www.hudsoncityschooldistrict.com/employment', 'www.hudsoncityschooldistrict.com', (42.2598622012, -73.7724653655)],
['HUDSON FALLS CENTRAL SCHOOL DISTRICT', 'http://www.hfcsd.org', 'www.hfcsd.org', (0.0, 0.0)],
['HUNTER-TANNERSVILLE CENTRAL SCHOOL DISTRICT', '', 'www.htcsd.org', (42.1966426192, -74.1377036485)],
['HUNTINGTON UNION FREE SCHOOL DISTRICT', 'http://www.hufsd.edu/leadership/hr.html', 'www.hufsd.edu', (40.8549016969, -73.4156388044)],
['HYDE PARK CENTRAL SCHOOL DISTRICT', 'https://www.hpcsd.org/Page/412', 'www.hpcsd.org', (41.7891663169, -73.9334959306)],
['INDIAN LAKE CENTRAL SCHOOL DISTRICT', 'http://www.ilcsd.org', 'www.ilcsd.org', (43.7820474542, -74.2706827072)],
['INDIAN RIVER CENTRAL SCHOOL DISTRICT', 'http://www.ircsd.org/about_i_r_c_s_d/employment_opportunities', 'www.ircsd.org', (44.1402893219, -75.7097196555)],
['INLET COMMON SCHOOL DISTRICT', '', 'http://inletcommonschool.org/', (43.7476372102, -74.7899835184)],
['IROQUOIS CENTRAL SCHOOL DISTRICT', '', 'www.iroquoiscsd.org', (42.8366230269, -78.6059097853)],
['IRVINGTON UNION FREE SCHOOL DISTRICT', 'https://www.irvingtonschools.org/Page/2145', 'www.irvingtonschools.org', (41.0332794701, -73.8708134941)],
['ISLAND PARK UNION FREE SCHOOL DISTRICT', 'http://www.ips.k12.ny.us/employment_opportunities', 'www.ips.k12.ny.us', (40.6076922755, -73.6466126333)],
['ISLAND TREES UNION FREE SCHOOL DISTRICT', 'http://www.islandtrees.org/districtinformation/employment.htm', 'www.islandtrees.org', (40.7355504829, -73.5005937215)],
['ISLIP UNION FREE SCHOOL DISTRICT', 'http://www.islipufsd.org/staff/professional_employment_opportunities', 'www.islipufsd.org', (40.7279737627, -73.2209868296)],
['ITHACA CITY SCHOOL DISTRICT', '', 'www.ithacacityschools.org', (42.45481474, -76.49639845)],
['JAMESTOWN CITY SCHOOL DISTRICT', '', 'www.jpsny.org', (42.078145295, -79.22024478)],
['JAMESVILLE-DEWITT CENTRAL SCHOOL DISTRICT', 'http://www.jamesvilledewitt.org/employment', 'www.jamesvilledewitt.org', (43.0194618913, -76.0453356969)],
['JASPER-TROUPSBURG CENTRAL SCHOOL DISTRICT', 'http://www.jtcsd.org/Page/51', 'www.jtcsd.org', (42.1433750976, -77.473434984)],
['JEFFERSON CENTRAL SCHOOL DISTRICT', 'http://www.jeffersoncs.org/about_j_c_s/district_job_opportunities', 'www.jeffersoncs.org', (42.4819377961, -74.6077335477)],
['JERICHO UNION FREE SCHOOL DISTRICT', 'http://jerichoschools.org', 'http://www.jerichoschools.org', (40.7981154373, -73.5447767993)],
['JOHNSBURG CENTRAL SCHOOL DISTRICT', 'http://www.johnsburgcsd.org', 'www.johnsburgcsd.org', (43.6935711621, -73.9846583888)],
['JOHNSON CITY CENTRAL SCHOOL DISTRICT', 'http://www.jcschools.com/Departments/Personnel/personnel.html', 'www.jcschools.com', (42.1342215486, -75.9685877716)],
['JOHNSTOWN CITY SCHOOL DISTRICT', 'https://www.johnstownschools.org/job-openings', 'www.johnstownschools.org', (43.00994131, -74.38380864)],
['JORDAN-ELBRIDGE CENTRAL SCHOOL DISTRICT', 'http://www.jecsd.org/districtpage.cfm?pageid=1586', 'www.jecsd.org', (43.0688113448, -76.4708775661)],
['KATONAH-LEWISBORO UNION FREE SCHOOL DISTRICT', 'http://www.klschools.org/groups/4498/human_resources/career_opportunities', 'www.klschools.org', (41.2386168495, -73.5229110372)],
['KEENE CENTRAL SCHOOL DISTRICT', 'http://www.keenecentralschool.org/about-us/employment', 'www.keenecentralschool.org', (44.1866110346, -73.7903984666)],
['KENDALL CENTRAL SCHOOL DISTRICT', 'http://www.kendallschools.org/district2.cfm?subpage=1169', 'www.kendallschools.org', (43.3220907724, -78.0369900949)],
['KENMORE-TONAWANDA UNION FREE SCHOOL DISTRICT', '', 'www.ktufsd.org', (42.9821709109, -78.859094309)],
['KINDERHOOK CENTRAL SCHOOL DISTRICT', 'http://www.ichabodcrane.org/district/employment', 'www.ichabodcrane.org', (42.425936036, -73.684079178)],
['KINGS PARK CENTRAL SCHOOL DISTRICT', 'https://www.kpcsd.org/apps/pages/index.jsp?dir=Job%20Postings&type=d&uREC_ID=346753', 'www.kpcsd.org', (40.8888378468, -73.240404973)],
['KINGSTON CITY SCHOOL DISTRICT', 'http://www.kingstoncityschools.org', 'www.kingstoncityschools.org', (0.0, 0.0)],
['KIRYAS JOEL VILLAGE UNION FREE SCHOOL DISTRICT', '', ' ', (41.33448274, -74.161741725)],
['LA FARGEVILLE CENTRAL SCHOOL DISTRICT', 'http://www.lafargevillecsd.org/Page/187', 'www.lafargevillecsd.org', (44.1936773531, -75.9652381516)],
['LACKAWANNA CITY SCHOOL DISTRICT', 'http://www.lackawannaschools.org', 'www.lackawannaschools.org', (42.825676259, -78.8109802765)],
['LAFAYETTE CENTRAL SCHOOL DISTRICT', 'http://www.lafayetteschools.org/teacherpage.cfm?teacher=247', 'www.lafayetteschools.org', (42.8937576625, -76.1086041434)],
['LAKE GEORGE CENTRAL SCHOOL DISTRICT', 'http://www.lkgeorge.org/Page/40', 'www.lkgeorge.org', (43.4283611714, -73.7125885259)],
['LAKE PLACID CENTRAL SCHOOL DISTRICT', 'http://www.lpcsd.org/employment', 'www.lpcsd.org', (44.2811412476, -73.9879994055)],
['LAKE PLEASANT CENTRAL SCHOOL DISTRICT', 'http://www.lpschool.com', 'www.lpschool.com', (43.5024624682, -74.3615536161)],
['LAKELAND CENTRAL SCHOOL DISTRICT', 'http://www.lakelandschools.org/departments/human_resources/employment.php', 'www.lakelandschools.org', (41.3296259756, -73.827698489)],
['LANCASTER CENTRAL SCHOOL DISTRICT', '', 'www.lancasterschools.org', (42.9073897393, -78.6712674258)],
['LANSING CENTRAL SCHOOL DISTRICT', '', 'www.lcsd.k12.ny.us', (42.5444498667, -76.5311745611)],
['LANSINGBURGH CENTRAL SCHOOL DISTRICT', 'http://www.lansingburgh.org/Page/38', 'www.lansingburgh.org', (42.7740512934, -73.6732485532)],
['LAURENS CENTRAL SCHOOL DISTRICT', 'http://www.laurenscs.org/Employment.aspx', 'www.laurenscs.org', (42.5318114531, -75.0885281366)],
['LAWRENCE UNION FREE SCHOOL DISTRICT', 'http://www.lawrence.org', 'www.lawrence.org', (40.630853675, -73.734548884)],
['LE ROY CENTRAL SCHOOL DISTRICT', '', 'www.leroycsd.org', (42.9763082464, -77.9859488865)],
['LETCHWORTH CENTRAL SCHOOL DISTRICT', 'http://www.letchworth.k12.ny.us/domain/1056', 'www.letchworth.k12.ny.us', (42.6294447563, -78.1151912166)],
['LEVITTOWN UNION FREE SCHOOL DISTRICT', 'http://www.levittownschools.com/departments/administrative/hr/employment', 'www.levittownschools.com', (40.7184900547, -73.510723849)],
['LEWISTON-PORTER CENTRAL SCHOOL DISTRICT', 'https://www.lew-port.com/Page/77', 'www.lew-port.com', (43.2167496311, -79.01751673)],
['LIBERTY CENTRAL SCHOOL DISTRICT', 'http://www.libertyk12.org/about-us/employment', 'www.libertyk12.org', (41.806302225, -74.754620367)],
['LINDENHURST UNION FREE SCHOOL DISTRICT', 'http://www.lindenhurstschools.org/our_district/employment', 'www.lindenhurstschools.org', (40.7009630687, -73.3661440132)],
['LISBON CENTRAL SCHOOL DISTRICT', 'http://lisboncs.schoolwires.com/Page/1346', 'http://lisboncs.schoolwires.com', (44.7232323951, -75.3214850471)],
['LITTLE FALLS CITY SCHOOL DISTRICT', 'http://www.lfcsd.org', 'www.lfcsd.org', (43.0443547055, -74.8515733649)],
['LITTLE FLOWER UNION FREE SCHOOL DISTRICT', 'http://www.littleflowerufsd.org', 'www.littleflowerufsd.org', (40.9603124454, -72.8322837006)],
['LIVERPOOL CENTRAL SCHOOL DISTRICT', 'http://www.liverpool.k12.ny.us/departments/human-resources/job-opportunities', 'www.liverpool.k12.ny.us', (43.1405588101, -76.2245514731)],
['LIVINGSTON MANOR CENTRAL SCHOOL DISTRICT', '', 'www.lmcs.k12.ny.us', (41.90305436, -74.8265030124)],
['LIVONIA CENTRAL SCHOOL DISTRICT', 'http://www.livoniacsd.org/Page/537', 'www.livoniacsd.org', (42.8173069604, -77.6674226034)],
['LOCKPORT CITY SCHOOL DISTRICT', '', 'www.lockportschools.org', (43.1605948157, -78.6795916895)],
['LOCUST VALLEY CENTRAL SCHOOL DISTRICT', '', 'www.lvcsd.k12.ny.us', (40.8868211957, -73.5915403881)],
['LONG BEACH CITY SCHOOL DISTRICT', 'http://www.lbeach.org/departments/opportunities', 'www.lbeach.org', (40.5881168021, -73.6279255539)],
['LONG LAKE CENTRAL SCHOOL DISTRICT', 'http://www.longlakecsd.org/employment', 'www.longlakecsd.org', (43.97271688, -74.422333678)],
['LONGWOOD CENTRAL SCHOOL DISTRICT', 'http://www.longwood.k12.ny.us', 'www.longwood.k12.ny.us', (40.8783548291, -72.9411701896)],
['LOWVILLE ACADEMY & CENTRAL SCHOOL DISTRICT', '', 'www.lowvilleacademy.org', (43.7901953039, -75.4923241982)],
['LYME CENTRAL SCHOOL DISTRICT', 'http://www.lymecsd.org/domain/31', 'www.lymecsd.org', (44.0663558253, -76.1341905838)],
['LYNBROOK UNION FREE SCHOOL DISTRICT', 'http://www.lynbrookschools.org/departments/personnel_office', 'www.lynbrookschools.org', (40.6534547974, -73.6714704264)],
['LYNCOURT UNION FREE SCHOOL DISTRICT', 'http://www.lyncourtschool.org/districtpage.cfm?pageid=259', 'www.lyncourtschool.org', (43.083982048, -76.1320860611)],
['LYNDONVILLE CENTRAL SCHOOL DISTRICT', 'http://www.lyndonvillecsd.org', 'www.lyndonvillecsd.org', (43.3231679687, -78.3909822591)],
['LYONS CENTRAL SCHOOL DISTRICT', '', 'www.lyonscsd.org', (43.0639901116, -76.9884830731)],
['MADISON CENTRAL SCHOOL DISTRICT', 'http://www.madisoncentralny.org/domain/176', 'www.madisoncentralny.org', (42.8994988503, -75.5162346234)],
['MADRID-WADDINGTON CENTRAL SCHOOL DISTRICT', 'http://www.mwcsk12.org', 'www.mwcsk12.org', (44.7893147265, -75.1546956335)],
['MAHOPAC CENTRAL SCHOOL DISTRICT', 'http://www.mahopac.k12.ny.us/groups/11079/human_resources/home', 'www.mahopac.k12.ny.us', (41.3771974826, -73.7286290042)],
['MAINE-ENDWELL CENTRAL SCHOOL DISTRICT', 'https://www.me.stier.org/Personnel-Employment.aspx', 'www.me.stier.org', (42.1280691005, -76.0234118385)],
['MALONE CENTRAL SCHOOL DISTRICT', 'http://www.malonecsd.org/employment.html', 'www.malonecsd.org', (44.8413421578, -74.2789330558)],
['MALVERNE UNION FREE SCHOOL DISTRICT', 'http://www.malverne.k12.ny.us/district/employment', 'www.malverne.k12.ny.us', (40.6703245066, -73.6626850723)],
['MAMARONECK UNION FREE SCHOOL DISTRICT', 'http://www.mamkschools.org/district/personnel/employment-opportunities', 'www.mamkschools.org', (40.941590907, -73.744610891)],
['MANCHESTER-SHORTSVILLE CENTRAL SCHOOL DISTRICT (RED JACKET)', '', 'www.redjacket.org', (42.9603017394, -77.2303374849)],
['MANHASSET UNION FREE SCHOOL DISTRICT', 'https://www.manhassetschools.org/domain/64', 'www.manhassetschools.org', (40.7942459564, -73.7034285876)],
['MARATHON CENTRAL SCHOOL DISTRICT', 'http://www.marathonschools.org/job-postings.html', 'www.marathonschools.org', (42.4409158976, -76.0340426264)],
['MARCELLUS CENTRAL SCHOOL DISTRICT', 'http://www.marcellusschools.org/teacherpage.cfm?teacher=816', 'www.marcellusschools.org', (42.9867842406, -76.3408474877)],
['MARGARETVILLE CENTRAL SCHOOL DISTRICT', 'https://www.margaretvillecs.org/Employment.aspx', 'www.margaretvillecs.org', (42.1455662305, -74.6533548154)],
['MARION CENTRAL SCHOOL DISTRICT', '', 'www.marioncs.org', (43.1718313516, -77.1899173296)],
['MARLBORO CENTRAL SCHOOL DISTRICT', '', 'www.marlboroschools.org', (41.6232679456, -73.9630983032)],
['MASSAPEQUA UNION FREE SCHOOL DISTRICT', 'http://www.msd.k12.ny.us/domain/33', 'www.msd.k12.ny.us', (40.6679878719, -73.4535237489)],
['MASSENA CENTRAL SCHOOL DISTRICT', '', 'www.mcs.k12.ny.us', (44.9232582662, -74.9008307028)],
['MATTITUCK-CUTCHOGUE UNION FREE SCHOOL DISTRICT', 'http://www.mufsd.com/departments/human_resources/job_postings', 'www.mufsd.com', (41.0130616479, -72.4857890921)],
['MAYFIELD CENTRAL SCHOOL DISTRICT', 'http://www.mayfieldk12.com', 'www.mayfieldk12.com', (43.10363, -74.26244)],
['MCGRAW CENTRAL SCHOOL DISTRICT', 'http://www.mcgrawschools.org/teacherpage.cfm?teacher=842', 'www.mcgrawschools.org', (42.5918003491, -76.0951344479)],
['MECHANICVILLE CITY SCHOOL DISTRICT', 'http://www.mechanicville.org/Page/189', 'www.mechanicville.org', (42.9006269986, -73.6987661349)],
['MEDINA CENTRAL SCHOOL DISTRICT', 'http://www.medinacsd.org/Page/761', 'www.medinacsd.org', (43.210697748, -78.3945140892)],
['MENANDS UNION FREE SCHOOL DISTRICT', 'https://www.menands.org/menands_union_free_school_employ.html', 'www.menands.org', (42.6844713871, -73.7336896535)],
['MERRICK UNION FREE SCHOOL DISTRICT', '', 'www.merrick.k12.ny.us', (40.6527447222, -73.5521293316)],
['MEXICO CENTRAL SCHOOL DISTRICT', '', 'www.mexico.cnyric.org', (43.4634779341, -76.2452265966)],
['MIDDLE COUNTRY CENTRAL SCHOOL DISTRICT', 'https://www.mccsd.net/Page/317', 'www.mccsd.net', (40.873209487, -73.0902465704)],
['MIDDLEBURGH CENTRAL SCHOOL DISTRICT', '', 'www.middleburghcsd.org', (42.5922473537, -74.3234672595)],
['MIDDLETOWN CITY SCHOOL DISTRICT', 'http://www.middletowncityschools.org', 'www.middletowncityschools.org', (41.44935446, -74.39723511)],
['MILFORD CENTRAL SCHOOL DISTRICT', 'http://www.web.milfordcentral.org/district/job_opportunities', 'www.milfordcentral.org', (42.5899314878, -74.9516382049)],
['MILLBROOK CENTRAL SCHOOL DISTRICT', '', 'www.millbrookcsd.org', (41.7822325666, -73.6867033219)],
['MILLER PLACE UNION FREE SCHOOL DISTRICT', 'https://www.millerplace.k12.ny.us/Domain/39', 'www.millerplace.k12.ny.us', (40.9345238816, -72.9885857307)],
['MINEOLA UNION FREE SCHOOL DISTRICT', 'http://www.mineola.k12.ny.us/district/human_resources', 'www.mineola.k12.ny.us', (40.7469983795, -73.6405549173)],
['MINERVA CENTRAL SCHOOL DISTRICT', 'http://www.minervasd.org', 'www.minervasd.org', (43.7689778464, -73.9363507315)],
['MINISINK VALLEY CENTRAL SCHOOL DISTRICT', 'http://www.minisink.com/index.php?id=11', 'www.minisink.com', (41.3827069192, -74.5166667886)],
['MONROE-WOODBURY CENTRAL SCHOOL DISTRICT', 'https://www.mw.k12.ny.us/about/employment', 'www.mw.k12.ny.us', (41.333386053, -74.120947803)],
['MONTAUK UNION FREE SCHOOL DISTRICT', 'http://www.montaukschool.org/domain/16', 'www.montaukschool.org', (41.0356132497, -71.9581296601)],
['MONTICELLO CENTRAL SCHOOL DISTRICT', 'https://www.monticelloschools.net/business-hr/employment', 'http://monticelloschools.net/', (41.6426160203, -74.7050765775)],
['MORAVIA CENTRAL SCHOOL DISTRICT', 'http://www.moraviaschool.org/teacherpage.cfm?teacher=1831', 'www.moraviaschool.org', (42.707536845, -76.42018335)],
['MORIAH CENTRAL SCHOOL DISTRICT', 'http://www.moriahk12.org/employment.html', 'www.moriahk12.org', (44.045236418, -73.478256575)],
['MORRIS CENTRAL SCHOOL DISTRICT', '', 'www.morriscsd.org', (42.5506833133, -75.2368814283)],
['MORRISTOWN CENTRAL SCHOOL DISTRICT', '', 'www.greenrockets.org', (44.5866253683, -75.6461458251)],
['MORRISVILLE-EATON CENTRAL SCHOOL DISTRICT', 'http://www.m-ecs.org/departments/business_office/human_resources/vacancy_postings', 'www.m-ecs.org', (42.9437369152, -75.6595737317)],
['MOUNT MARKHAM CENTRAL SCHOOL DISTRICT', 'http://www.mmcsd.org/Page/19', 'www.mmcsd.org', (42.8860449828, -75.1855411062)],
['MOUNT MORRIS CENTRAL SCHOOL DISTRICT', '', 'www.mtmorriscsd.org', (42.7140780913, -77.8722093681)],
['MOUNT PLEASANT CENTRAL SCHOOL DISTRICT', 'http://www.mtplcsd.org', 'www.mtplcsd.org', (41.1109845392, -73.7672576675)],
['MOUNT PLEASANT-BLYTHEDALE UNION FREE SCHOOL DISTRICT', 'http://www.mpbschools.org', 'www.mpbschools.org', (41.0746021567, -73.7998141605)],
['MOUNT PLEASANT-COTTAGE UNION FREE SCHOOL DISTRICT', 'http://www.mpcsny.org', 'www.mpcsny.org', (41.1292410063, -73.7713345336)],
['MOUNT SINAI UNION FREE SCHOOL DISTRICT', 'http://www.mtsinai.k12.ny.us/our_district/employment/employment.html', 'www.mtsinai.k12.ny.us', (40.9425345277, -73.0240191847)],
['MOUNT VERNON SCHOOL DISTRICT', 'http://www.mtvernoncsd.org', 'www.mtvernoncsd.org', (40.916523363, -73.824335494)],
['NANUET UNION FREE SCHOOL DISTRICT', '', 'www.nanuetsd.org', (41.0895855058, -74.0043643775)],
['NAPLES CENTRAL SCHOOL DISTRICT', '', 'www.naples.k12.ny.us', (42.617875587, -77.400776522)],
['NEW HARTFORD CENTRAL SCHOOL DISTRICT', '', 'www.nhart.org', (43.0697013367, -75.28333804)],
['NEW HYDE PARK-GARDEN CITY PARK UNION FREE SCHOOL DISTRICT', 'http://www.nhp-gcp.org/domain/63', 'www.nhp-gcp.org', (40.7496117674, -73.680768749)],
['NEW LEBANON CENTRAL SCHOOL DISTRICT', 'http://www.newlebanoncsd.org/district/employment', 'www.newlebanoncsd.org', (42.4756392791, -73.3793754445)],
['NEW PALTZ CENTRAL SCHOOL DISTRICT', 'http://www.newpaltz.k12.ny.us/domain/10', 'www.newpaltz.k12.ny.us', (41.7456027572, -74.0778129412)],
['NEW ROCHELLE CITY SCHOOL DISTRICT', 'http://www.nred.org/groups/17143/human_resources/human_resources', 'www.nred.org', (40.9200100003, -73.7861600252)],
['NEW SUFFOLK COMMON SCHOOL DISTRICT', 'http://www.newsuffolkschool.com', 'www.newsuffolkschool.com', (40.9927016647, -72.4751690776)],
['NEW YORK CITY GEOGRAPHIC DISTRICT # 1', '', ' ', (40.7213101278, -73.9865668266)],
['NEW YORK CITY GEOGRAPHIC DISTRICT # 2', '', ' ', (40.7473902485, -73.9929687658)],
['NEW YORK CITY GEOGRAPHIC DISTRICT # 3', '', ' ', (40.7915850234, -73.9708516916)],
['NEW YORK CITY GEOGRAPHIC DISTRICT # 4', '', ' ', (40.7973684775, -73.9362905507)],
['NEW YORK CITY GEOGRAPHIC DISTRICT # 5', '', ' ', (40.8107051251, -73.9562316796)],
['NEW YORK CITY GEOGRAPHIC DISTRICT # 6', '', ' ', (40.8534183318, -73.9334510031)],
['NEW YORK CITY GEOGRAPHIC DISTRICT # 7', '', ' ', (40.8156697264, -73.9200252477)],
['NEW YORK CITY GEOGRAPHIC DISTRICT # 8', '', ' ', (40.8179648165, -73.8562978153)],
['NEW YORK CITY GEOGRAPHIC DISTRICT # 9', '', ' ', (40.8362417209, -73.9050655733)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #10', '', ' ', (40.8606118942, -73.8901499893)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #11', '', ' ', (40.8669872462, -73.8508001542)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #12', '', ' ', (40.8391827393, -73.8802805548)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #13', '', ' ', (40.6960560496, -73.9633542954)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #14', '', ' ', (40.7037177273, -73.9532136384)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #15', '', ' ', (40.6910798334, -73.9883832649)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #16', '', ' ', (40.6919313597, -73.9317700161)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #17', '', ' ', (40.6725712436, -73.9372573018)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #18', '', ' ', (40.6432483057, -73.9033151895)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #19', '', ' ', (40.6636337198, -73.8935458938)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #20', '', ' ', (40.6202317101, -74.0285202515)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #21', '', ' ', (40.582210563, -73.9724764323)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #22', '', ' ', (40.6303158399, -73.921748802)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #23', '', ' ', (40.6742301597, -73.9132521785)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #24', '', ' ', (40.7423254866, -73.8627339293)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #25', '', ' ', (40.7701702048, -73.8329936125)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #26', '', ' ', (40.7590909658, -73.7742440844)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #27', '', ' ', (40.6844212276, -73.8579938554)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #28', '', ' ', (40.702328581, -73.8080432351)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #29', '', ' ', (40.7207363057, -73.7315323739)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #30', '', ' ', (40.7502628302, -73.9385070149)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #31', '', ' ', (40.6093017468, -74.1039729266)],
['NEW YORK CITY GEOGRAPHIC DISTRICT #32', '', ' ', (40.6950398562, -73.9277170771)],
['NEW YORK MILLS UNION FREE SCHOOL DISTRICT', 'http://www.newyorkmills.org/Page/30', 'www.newyorkmills.org', (43.0926899584, -75.2909991429)],
['NEWARK CENTRAL SCHOOL DISTRICT', '', 'www.newarkcsd.org', (43.0462114015, -77.0931673067)],
['NEWARK VALLEY CENTRAL SCHOOL DISTRICT', 'http://www.nvcs.stier.org', 'www.nvcs.stier.org', (42.2300545647, -76.1850644381)],
['NEWBURGH CITY SCHOOL DISTRICT', 'http://www.newburghschools.org/page.php?page=7', 'www.newburghschools.org', (41.5036251169, -74.0084225809)],
['NEWCOMB CENTRAL SCHOOL DISTRICT', '', 'www.newcombcsd.org', (43.9714571333, -74.1509682808)],
['NEWFANE CENTRAL SCHOOL DISTRICT', 'http://www.newfane.wnyric.org/page/24', 'www.newfane.wnyric.org', (43.284401322, -78.6923141935)],
['NEWFIELD CENTRAL SCHOOL DISTRICT', 'http://www.newfieldschools.org', 'www.newfieldschools.org', (42.3578413655, -76.5968103757)],
['NIAGARA FALLS CITY SCHOOL DISTRICT', 'https://www.nfschools.net/Page/3559', 'www.nfschools.net', (43.0868283343, -78.9888345744)],
['NIAGARA-WHEATFIELD CENTRAL SCHOOL DISTRICT', '', 'www.nwcsd.org', (43.1425827798, -78.8928068761)],
['NISKAYUNA CENTRAL SCHOOL DISTRICT', '', 'www.niskyschools.org', (42.8087213199, -73.8950585081)],
['NORTH BABYLON UNION FREE SCHOOL DISTRICT', 'http://www.northbabylonschools.net/our_district/employment_opportunities', 'www.northbabylonschools.net', (40.7232598462, -73.3246341532)],
['NORTH BELLMORE UNION FREE SCHOOL DISTRICT', '', 'www.northbellmoreschools.org', (40.67438794, -73.5318568178)],
['NORTH COLLINS CENTRAL SCHOOL DISTRICT', 'https://www.northcollins.com/cms/One.aspx?portalId=272706&pageId=626890', 'www.northcollins.com', (42.5978390439, -78.9390406279)],
['NORTH COLONIE CSD', 'https://www.northcolonie.org/about-us/employment-opportunities', 'www.northcolonie.org', (42.729102507, -73.746943824)],
['NORTH GREENBUSH COMMON SCHOOL DISTRICT (WILLIAMS)', '', ' ', (42.6933280159, -73.6870499455)],
['NORTH MERRICK UNION FREE SCHOOL DISTRICT', '', 'www.nmerrickschools.org', (40.6949154361, -73.5649082973)],
['NORTH ROSE-WOLCOTT CENTRAL SCHOOL DISTRICT', 'http://www.nrwcs.org/domain/38', 'www.nrwcs.org', (43.192302562, -76.8299545236)],
['NORTH SALEM CENTRAL SCHOOL DISTRICT', 'http://www.northsalemschools.org/Page/2807', 'www.northsalemschools.org', (41.3555605645, -73.5948432293)],
['NORTH SHORE CENTRAL SCHOOL DISTRICT', '', 'www.northshoreschools.org', (40.8467252314, -73.6417391885)],
['NORTH SYRACUSE CENTRAL SCHOOL DISTRICT', '', 'www.nscsd.org', (43.1226570837, -76.1440092685)],
['NORTH TONAWANDA CITY SCHOOL DISTRICT', '', 'www.ntschools.org', (43.044098926, -78.879104788)],
['NORTH WARREN CENTRAL SCHOOL DISTRICT', 'http://www.northwarren.k12.ny.us/Employment.html', 'www.northwarren.k12.ny.us', (43.663823041, -73.7851490896)],
['NORTHEAST CENTRAL SCHOOL DISTRICT', 'https://www.webutuckschools.org/Page/29', 'www.webutuckschools.org', (41.8863728458, -73.5358515773)],
['NORTHEASTERN CLINTON CENTRAL SCHOOL DISTRICT', 'http://www.nccscougar.org/Page/29', 'www.nccscougar.org', (44.9894034809, -73.4150782558)],
['NORTHERN ADIRONDACK CENTRAL SCHOOL DISTRICT', 'http://www.nacs1.org/cms/One.aspx?portalId=465963&pageId=1327562', 'www.nacs1.org', (44.8937336483, -73.8420099437)],
['NORTHPORT-EAST NORTHPORT UNION FREE SCHOOL DISTRICT', 'http://northport.k12.ny.us/district/human_resources', 'www.northport.k12.ny.us', (40.89839077, -73.33715786)],
['NORTHVILLE CENTRAL SCHOOL DISTRICT', 'https://sites.google.com/a/northvillecsd.org/ncsd/home/district/community/local-job-postings', 'www.northvillecsd.org', (43.2241480085, -74.1758443224)],
['NORWICH CITY SCHOOL DISTRICT', 'https://www.norwichcsd.org/Vacancies.aspx', 'www.norwichcsd.org', (42.526083318, -75.515615064)],
['NORWOOD-NORFOLK CENTRAL SCHOOL DISTRICT', 'http://www.nncsk12.org/Page/36', 'www.nncsk12.org', (44.7753482503, -74.9883630731)],
['NYACK UNION FREE SCHOOL DISTRICT', 'http://www.nyackschools.org/groups/6169/human_resources/home', 'www.nyackschools.org', (41.0900312971, -73.9333999942)],
["NYC CHANCELLOR'S OFFICE", '', ' ', (40.7134375787, -74.0052697594)],
['NYC SPECIAL SCHOOLS - DISTRICT 75', '', ' ', (40.7369585029, -73.978250606)],
['OAKFIELD-ALABAMA CENTRAL SCHOOL DISTRICT', 'https://www.oahornets.org/apps/jobs', 'www.oahornets.org', (43.0743262644, -78.2797602389)],
['OCEANSIDE UNION FREE SCHOOL DISTRICT', '', 'www.oceansideschools.org', (40.6430232304, -73.6338762685)],
['ODESSA-MONTOUR CENTRAL SCHOOL DISTRICT', 'http://www.omschools.org/employment.cfm', 'www.omschools.org', (42.3343556425, -76.7912624769)],
['OGDENSBURG CITY SCHOOL DISTRICT', 'http://www.ogdensburgk12.org/domain/1035', 'www.ogdensburgk12.org', (44.689372822, -75.4847516825)],
['OLEAN CITY SCHOOL DISTRICT', 'https://www.oleanschools.org/Page/5715', 'www.oleanschools.org', (42.0830226675, -78.4351288168)],
['ONEIDA CITY SCHOOL DISTRICT', 'http://www.oneidacsd.org', 'www.oneidacsd.org', (43.0804709998, -75.662595076)],
['ONEONTA CITY SCHOOL DISTRICT', 'https://www.oneontacsd.org/EmploymentOpportunities.aspx', 'www.oneontacsd.org', (42.4595914829, -75.0646581482)],
['ONONDAGA CENTRAL SCHOOL DISTRICT', 'http://www.ocs.cnyric.org/district.cfm?subpage=3520', 'www.ocs.cnyric.org', (42.9296113458, -76.2057176306)],
['ONTEORA CENTRAL SCHOOL DISTRICT', '', 'www.onteora.k12.ny.us', (42.0099339384, -74.2660330488)],
['OPPENHEIM-EPHRATAH-ST. JOHNSVILLE CSD', 'https://www.oesj.org', 'www.oesj.org', (43.00115841, -74.67620823)],
['ORCHARD PARK CENTRAL SCHOOL DISTRICT', 'http://www.opschools.org/Page/125', 'www.opschools.org', (42.8048300206, -78.7364529347)],
['ORISKANY CENTRAL SCHOOL DISTRICT', 'http://www.oriskanycsd.org/Page/663', 'www.oriskanycsd.org', (43.1619146713, -75.3414982116)],
['OSSINING UNION FREE SCHOOL DISTRICT', '', 'www.ossiningufsd.org', (41.1830867507, -73.8566299665)],
['OSWEGO CITY SCHOOL DISTRICT', 'http://www.oswego.org/personnel', 'www.oswego.org', (0.0, 0.0)],
['OTEGO-UNADILLA CENTRAL SCHOOL DISTRICT', 'https://www.unatego.org/Employment.aspx', 'www.unatego.org', (42.37063932, -75.225602248)],
['OWEGO-APALACHIN CENTRAL SCHOOL DISTRICT', '', 'www.oacsd.org', (42.114974408, -76.271820817)],
['OXFORD ACADEMY AND CENTRAL SCHOOL DISTRICT', 'https://www.oxac.org/Employment.aspx', 'www.oxac.org', (42.440927114, -75.5956690593)],
['OYSTER BAY-EAST NORWICH CENTRAL SCHOOL DISTRICT', 'http://obenschools.org/domain/33', 'www.obenschools.org', (40.8712742575, -73.5250299556)],
['OYSTERPONDS UNION FREE SCHOOL DISTRICT', 'http://www.oysterponds.org', 'www.oysterponds.org', (41.1435233542, -72.2992778828)],
['PALMYRA-MACEDON CENTRAL SCHOOL DISTRICT', 'http://www.palmaccsd.org/Content2/286', 'www.palmaccsd.org', (43.0578884792, -77.2443529233)],
['PANAMA CENTRAL SCHOOL DISTRICT', 'http://www.pancent.org/Page/27', 'www.pancent.org', (42.0781838494, -79.483322125)],
['PARISHVILLE-HOPKINTON CENTRAL SCHOOL DISTRICT', '', 'www.phcs.neric.org', (44.6305861744, -74.8116335857)],
['PATCHOGUE-MEDFORD UNION FREE SCHOOL DISTRICT', 'https://www.pmschools.org/Page/160', 'www.pmschools.org', (40.760211702, -73.0120489509)],
['PAVILION CENTRAL SCHOOL DISTRICT', 'http://www.pavilioncsd.org', 'www.pavilioncsd.org', (42.8719072435, -78.0182651043)],
['PAWLING CENTRAL SCHOOL DISTRICT', 'http://www.pawlingschools.org', 'www.pawlingschools.org', (41.5605427006, -73.5943830112)],
['PEARL RIVER UNION FREE SCHOOL DISTRICT', 'http://www.pearlriver.org/groups/55638/human_resources/employment_opportunities', 'www.pearlriver.org', (41.068075773, -74.0273740676)],
['PEEKSKILL CITY SCHOOL DISTRICT', 'https://www.peekskillcsd.org/Page/383', 'www.peekskillcsd.org', (41.2861163764, -73.9168378045)],
['PELHAM UNION FREE SCHOOL DISTRICT', 'http://www.pelhamschools.org', 'www.pelhamschools.org', (40.9039012262, -73.8117963931)],
['PEMBROKE CENTRAL SCHOOL DISTRICT', 'http://www.pembrokecsd.org', 'www.pembrokecsd.org', (42.9912801588, -78.4044101044)],
['PENFIELD CENTRAL SCHOOL DISTRICT', '', 'www.penfield.edu', (43.1542431743, -77.4940498375)],
['PENN YAN CENTRAL SCHOOL DISTRICT', 'https://www.pycsd.org/apps/pages/index.jsp?uREC_ID=948562&type=d&pREC_ID=1275659', 'www.pycsd.org', (42.6670823446, -77.0626180858)],
['PERRY CENTRAL SCHOOL DISTRICT', '', 'www.perry.k12..ny.us', (42.7251355866, -78.0025689304)],
['PERU CENTRAL SCHOOL DISTRICT', 'http://www.perucsd.org/Page/1822', 'www.perucsd.org', (44.5819817664, -73.5328084924)],
['PHELPS-CLIFTON SPRINGS CENTRAL SCHOOL DISTRICT', 'http://www.midlakes.org/Page/43', 'www.midlakes.org', (42.9599843588, -77.095860297)],
['PHOENIX CENTRAL SCHOOL DISTRICT', 'http://www.phoenixcsd.org/Page/1053', 'www.phoenixcsd.org', (43.238456247, -76.296384977)],
['PINE BUSH CENTRAL SCHOOL DISTRICT', 'https://www.pinebushschools.org/departments/hr-employment', 'www.pinebushschools.org', (41.6028663096, -74.3073523446)],
['PINE PLAINS CENTRAL SCHOOL DISTRICT', 'http://www.ppcsd.org/Employment', 'www.ppcsd.org', (41.9840151498, -73.6627306377)],
['PINE VALLEY CENTRAL SCHOOL DISTRICT (SOUTH DAYTON)', 'http://www.pval.org/Page/20', 'www.pval.org', (42.3367411786, -79.0923314095)],
['PISECO COMMON SCHOOL DISTRICT', 'http://www.pisecoschool.com', 'www.pisecoschool.com', (43.4274224078, -74.497203572)],
['PITTSFORD CENTRAL SCHOOL DISTRICT', 'http://www.pittsfordschools.org/Page/928', 'www.pittsfordschools.org', (43.058071154, -77.5251827998)],
['PLAINEDGE UNION FREE SCHOOL DISTRICT', 'http://www.plainedgeschools.org/administration/office_of_human_resources/employment_opportunities', 'www.plainedgeschools.org', (40.7000136035, -73.4747161577)],
['PLAINVIEW-OLD BETHPAGE CENTRAL SCHOOL DISTRICT', '', 'www.pobschools.org', (40.780273529, -73.4651925356)],
['PLATTSBURGH CITY SCHOOL DISTRICT', '', 'www.plattscsd.org', (44.6944371087, -73.4587224233)],
['PLEASANTVILLE UNION FREE SCHOOL DISTRICT', 'http://www.pleasantvilleschools.com', 'www.pleasantvilleschools.com', (41.1344324801, -73.785434559)],
['POCANTICO HILLS CENTRAL SCHOOL DISTRICT', '', 'http://pocantico.pocanticohills.org', (41.0973498176, -73.8313890724)],
['POLAND CENTRAL SCHOOL DISTRICT', 'http://www.polandcs.org/domain/270', 'www.polandcs.org', (43.2279159246, -75.0589169003)],
['PORT BYRON CENTRAL SCHOOL DISTRICT', 'http://www.pbcschools.org/districtpage.cfm?pageid=1512', 'www.pbcschools.org', (43.0423531562, -76.6175847994)],
['PORT CHESTER-RYE UNION FREE SCHOOL DISTRICT', '', 'www.portchesterschools.org', (41.0054856486, -73.6844993466)],
['PORT JEFFERSON UNION FREE SCHOOL DISTRICT', '', 'www.portjeffschools.org', (40.9440733132, -73.0529576601)],
['PORT JERVIS CITY SCHOOL DISTRICT', '', 'www.pjschools.org', (41.37373622, -74.697158299)],
['PORT WASHINGTON UNION FREE SCHOOL DISTRICT', '', 'www.portnet.org', (40.8294617469, -73.6801886948)],
['PORTVILLE CENTRAL SCHOOL DISTRICT', 'http://www.portville.wnyric.org', 'www.portville.wnyric.org', (42.0341468626, -78.3311005025)],
['POTSDAM CENTRAL SCHOOL DISTRICT', 'http://www.potsdam.k12.ny.us/apps/pages/index.jsp?uREC_ID=747176&type=d&pREC_ID=1248094', 'www.potsdam.k12.ny.us', (44.6749621946, -74.9749737249)],
['POUGHKEEPSIE CITY SCHOOL DISTRICT', 'https://www.poughkeepsieschools.org/Page/320', 'www.poughkeepsieschools.org', (41.70441005, -73.93439081)],
['PRATTSBURGH CENTRAL SCHOOL DISTRICT', 'https://www.prattsburghcsd.org/Page/26', 'www.prattsburghcsd.org', (42.5249922123, -77.2894291123)],
['PULASKI CENTRAL SCHOOL DISTRICT', '', 'www.pacs.cnyric.org', (43.5713629575, -76.1356300299)],
['PUTNAM CENTRAL SCHOOL DISTRICT', 'http://www.putnamcsd.org/employment.html', 'www.putnamcsd.org', (43.7478008519, -73.3942938886)],
['PUTNAM VALLEY CENTRAL SCHOOL DISTRICT', 'http://pvcsd.org/index.php/district/district-info/human-resources', 'www.pvcsd.org', (41.3546967247, -73.8720355501)],
['QUEENSBURY UNION FREE SCHOOL DISTRICT', '', 'www.queensburyschool.org', (43.3293967579, -73.6908577796)],
['QUOGUE UNION FREE SCHOOL DISTRICT', 'https://www.quogueschool.com', 'www.quogueschool.com', (40.8196817152, -72.6043390442)],
['RANDOLPH ACADEMY UNION FREE SCHOOL DISTRICT', 'http://www.randolphacademy.org', 'www.randolphacademy.org', (42.168181999, -78.9615730573)],
['RANDOLPH CENTRAL SCHOOL DISTRICT', 'http://www.randolphcsd.org/domain/24', 'www.randolphcsd.org', (42.1642698573, -78.9672704385)],
['RAQUETTE LAKE UNION FREE SCHOOL DISTRICT', '', ' ', (43.8092788645, -74.6542438978)],
['RAVENA-COEYMANS-SELKIRK CENTRAL SCHOOL DISTRICT', '', 'www.rcscsd.org', (42.4730475749, -73.8148364099)],
['RED CREEK CENTRAL SCHOOL DISTRICT', 'http://www.rccsd.org/apps/jobs', 'www.rccsd.org', (43.240328113, -76.716476609)],
['RED HOOK CENTRAL SCHOOL DISTRICT', 'http://www.redhookcentralschools.org', 'www.redhookcentralschools.org', (42.0187657429, -73.8703814561)],
['REMSEN CENTRAL SCHOOL DISTRICT', 'http://www.remsencsd.org/Page/1050', 'www.remsencsd.org', (43.3325020252, -75.1931509542)],
['REMSENBURG-SPEONK UNION FREE SCHOOL DISTRICT', '', 'http://rsufsd.drupalgardens.com', (40.8072900554, -72.707500085)],
['RENSSELAER CITY SCHOOL DISTRICT', 'http://www.rcsd.k12.ny.us/district/employment', 'www.rcsd.k12.ny.us', (42.653909498, -73.72075147)],
['RHINEBECK CENTRAL SCHOOL DISTRICT', 'http://www.rhinebeckcsd.org/pagecontent.php?id=69', 'www.rhinebeckcsd.org', (41.9255155038, -73.9003931828)],
['RICHFIELD SPRINGS CENTRAL SCHOOL DISTRICT', 'http://www.richfieldcsd.org/Page/442', 'www.richfieldcsd.org', (42.8547817744, -74.9885993348)],
['RIPLEY CENTRAL SCHOOL DISTRICT', '', 'www.ripleycsd.wnyric.org', (42.267997525, -79.7111344965)],
['RIVERHEAD CENTRAL SCHOOL DISTRICT', 'http://www.riverhead.net/district/employment', 'www.riverhead.net', (40.9252560553, -72.6750893086)],
['ROCHESTER CITY SCHOOL DISTRICT', 'https://www.rcsdk12.org/employment', 'www.rcsdk12.org', (43.1536357038, -77.616077131)],
['ROCKVILLE CENTRE UNION FREE SCHOOL DISTRICT', 'http://www.rvcschools.org/departments_and_programs/personnel/employment_opportunities', 'www.rvcschools.org', (40.6669679824, -73.623432835)],
['ROCKY POINT UNION FREE SCHOOL DISTRICT', '', 'www.rockypointschools.org', (40.929907985, -72.9408549418)],
['ROME CITY SCHOOL DISTRICT', 'http://www.romecsd.org', 'www.romecsd.org', (43.2217865404, -75.4267708805)],
['ROMULUS CENTRAL SCHOOL DISTRICT', '', 'www.rcs.k12.ny.us', (42.7489388887, -76.8326204712)],
['RONDOUT VALLEY CENTRAL SCHOOL DISTRICT', 'http://www.rondout.k12.ny.us', 'www.rondout.k12.ny.us', (41.814549721, -74.18820517)],
['ROOSEVELT UNION FREE SCHOOL DISTRICT', '', 'www.rooseveltufsd.org', (40.6870449048, -73.5815659964)],
['ROSCOE CENTRAL SCHOOL DISTRICT', 'http://www.roscoe.k12.ny.us/Page/88', 'www.roscoe.k12.ny.us', (41.9345686032, -74.9164739045)],
['ROSLYN UNION FREE SCHOOL DISTRICT', '', 'www.roslynschools.org', (40.7943676437, -73.639570517)],
['ROTTERDAM-MOHONASEN CENTRAL SCHOOL DISTRICT', 'https://www.mohonasen.org/employment', 'www.mohonasen.org', (42.7751403097, -73.9526436084)],
['ROXBURY CENTRAL SCHOOL DISTRICT', 'http://www.roxburycs.org', 'www.roxburycs.org', (42.2865337296, -74.5641077509)],
['ROYALTON-HARTLAND CENTRAL SCHOOL DISTRICT', 'http://www.royhart.org/Page/269', 'www.royhart.org', (43.212289443, -78.46729083)],
['RUSH-HENRIETTA CENTRAL SCHOOL DISTRICT', '', 'www.rhnet.org', (43.0600843306, -77.5942736802)],
['RYE CITY SCHOOL DISTRICT', 'http://www.ryeschools.org', 'www.ryeschools.org', (40.9735055948, -73.70067955)],
['RYE NECK UNION FREE SCHOOL DISTRICT', 'http://www.ryeneck.k12.ny.us', 'www.ryeneck.k12.ny.us', (40.9579472789, -73.7157214451)],
['SACHEM CENTRAL SCHOOL DISTRICT', '', 'www.sachem.edu', (40.8319509843, -73.1033539124)],
['SACKETS HARBOR CENTRAL SCHOOL DISTRICT', 'http://www.sacketspatriots.org/our_district/employment_opportunities', 'www.sacketspatriots.org', (43.9435617618, -76.1206278811)],
['SAG HARBOR UNION FREE SCHOOL DISTRICT', 'http://www.sagharborschools.org', 'www.sagharborschools.org', (40.9943016954, -72.2886391092)],
['SAGAPONACK COMMON SCHOOL DISTRICT', 'http://www.sagaponackschool.com', 'www.sagaponackschool.com', (40.9261050617, -72.2784100659)],
['SAINT REGIS FALLS CENTRAL SCHOOL DISTRICT', '', 'www.stregisfallscsd.org', (44.6790742805, -74.544488141)],
['SALAMANCA CITY SCHOOL DISTRICT', 'http://www.salamancany.org', 'www.salamancany.org', (42.1607146139, -78.7386862724)],
['SALEM CENTRAL SCHOOL DISTRICT', 'http://www.salemcsd.org', 'www.salemcsd.org', (43.1735492966, -73.3240865614)],
['SALMON RIVER CENTRAL SCHOOL DISTRICT', '', 'www.srk12.org', (44.96172299, -74.51968084)],
['SANDY CREEK CENTRAL SCHOOL DISTRICT', '', 'www.sccs.cnyric.org', (43.646098229, -76.0766000351)],
['SARANAC CENTRAL SCHOOL DISTRICT', '', 'www.saranac.org', (44.7132131132, -73.7214413813)],
['SARANAC LAKE CENTRAL SCHOOL DISTRICT', 'http://www.slcs.org/district-office/employment-applications', 'www.slcs.org', (44.3277420356, -74.1440369612)],
['SAUGERTIES CENTRAL SCHOOL DISTRICT', '', 'www.saugerties.k12.ny.us', (42.0869188606, -73.9510454182)],
['SAUQUOIT VALLEY CENTRAL SCHOOL DISTRICT', 'http://www.svcsd.org', 'www.svcsd.org', (42.9888427531, -75.2534384153)],
['SAYVILLE UNION FREE SCHOOL DISTRICT', 'https://www.sayvilleschools.org/Page/3271', 'www.sayvilleschools.org', (40.7378345242, -73.0872950691)],
['SCARSDALE UNION FREE SCHOOL DISTRICT', '', 'www.scarsdaleschools.org', (40.9952461295, -73.7944945386)],
['SCHALMONT CENTRAL SCHOOL DISTRICT', '', 'www.schalmont.org', (42.7835243642, -74.0195052677)],
['SCHENECTADY CITY SCHOOL DISTRICT', 'http://www.schenectady.k12.ny.us', 'www.schenectady.k12.ny.us', (42.797537346, -73.9394134346)],
['SCHENEVUS CENTRAL SCHOOL DISTRICT', '', 'www.schenevuscs.org', (42.5495823068, -74.8180159541)],
['SCHODACK CENTRAL SCHOOL DISTRICT', 'http://www.schodack.k12.ny.us/district/employment', 'www.schodack.k12.ny.us', (42.5214223184, -73.7096255134)],
['SCHOHARIE CENTRAL SCHOOL DISTRICT', '', 'www.schoharieschools.org', (42.6670198369, -74.3077856909)],
['SCHROON LAKE CENTRAL SCHOOL DISTRICT', 'http://www.schroonschool.org/?page_id=30', 'www.schroonschool.org', (43.8367049578, -73.7611950669)],
['SCHUYLERVILLE CENTRAL SCHOOL DISTRICT', 'https://www.schuylervilleschools.org/employment', 'www.schuylervilleschools.org', (43.1041218103, -73.5799421911)],
['SCIO CENTRAL SCHOOL DISTRICT', 'http://www.scio.wnyric.org/districtpage.cfm?pageid=334', 'www.scio.wnyric.org', (42.1722067306, -77.9767185616)],
['SCOTIA-GLENVILLE CENTRAL SCHOOL DISTRICT', 'http://scotiaglenvilleschools.org', 'www.scotiaglenvilleschools.org', (42.83462386, -73.98023473)],
['SEAFORD UNION FREE SCHOOL DISTRICT', 'http://www.seaford.k12.ny.us', 'www.seaford.k12.ny.us', (40.6854572024, -73.4851049332)],
['SENECA FALLS CENTRAL SCHOOL DISTRICT', '', 'www.senecafallscsd.org', (42.9188120338, -76.8031321755)],
['SEWANHAKA CENTRAL HIGH SCHOOL DISTRICT', '', 'www.sewanhakaschools.org', (40.7169017115, -73.6918430814)],
['SHARON SPRINGS CENTRAL SCHOOL DISTRICT', 'https://www.sharonsprings.org/employment', 'www.sharonsprings.org', (42.7898866235, -74.6240396757)],
['SHELTER ISLAND UNION FREE SCHOOL DISTRICT', 'http://www.shelterisland.k12.ny.us/domain/104', 'www.shelterisland.k12.ny.us', (41.063210968, -72.3276143734)],
['SHENENDEHOWA CENTRAL SCHOOL DISTRICT', 'https://www.shenet.org/employment', 'www.shenet.org', (42.8686912376, -73.7703187727)],
['SHERBURNE-EARLVILLE CENTRAL SCHOOL DISTRICT', 'https://www.secsd.org/Employment.aspx', 'www.secsd.org', (42.6886065354, -75.5004309081)],
['SHERMAN CENTRAL SCHOOL DISTRICT', '', 'www.sherman.wnyric.org', (42.1608555987, -79.5939419494)],
['SHERRILL CITY SCHOOL DISTRICT', 'http://www.vvsschools.org/domain/16', 'www.vvsschools.org', (43.117085753, -75.5678027079)],
['SHOREHAM-WADING RIVER CENTRAL SCHOOL DISTRICT', 'http://www.swrschools.org/our_district/employment', 'www.swrschools.org', (40.9419489029, -72.86857969)],
['SIDNEY CENTRAL SCHOOL DISTRICT', '', 'www.sidneycsd.org', (42.3037667297, -75.3887181991)],
['SILVER CREEK CENTRAL SCHOOL DISTRICT', 'http://www.silvercreekschools.org', 'www.silvercreekschools.org', (42.5341441525, -79.1665196287)],
['SKANEATELES CENTRAL SCHOOL DISTRICT', 'http://www.skanschools.org/districtpage.cfm?pageid=363', 'www.skanschools.org', (42.9500387106, -76.4248511054)],
['SMITHTOWN CENTRAL SCHOOL DISTRICT', 'http://www.smithtown.k12.ny.us/district/district_documents', 'www.smithtown.k12.ny.us', (40.8543085705, -73.199152311)],
['SODUS CENTRAL SCHOOL DISTRICT', '', 'www.soduscsd.org', (43.2306239722, -77.0598970076)],
['SOLVAY UNION FREE SCHOOL DISTRICT', 'http://www.solvayschools.org/districtpage.cfm?pageid=346', 'www.solvayschools.org', (43.0929093684, -76.2493640562)],
['SOMERS CENTRAL SCHOOL DISTRICT', 'http://www.somersschools.org/Page/3984', 'www.somersschools.org', (41.3264121165, -73.6962827148)],
['SOUTH COLONIE CENTRAL SCHOOL DISTRICT', 'https://www.southcolonieschools.org/departments/human-resources-department/employment-opportunities', 'www.southcolonieschools.org', (42.7315725202, -73.8390242959)],
['SOUTH COUNTRY CENTRAL SCHOOL DISTRICT', 'http://www.southcountry.org/departments/employment_opportunities', 'www.southcountry.org', (40.7504511019, -72.9675040136)],
['SOUTH GLENS FALLS CENTRAL SCHOOL DISTRICT', 'https://www.sgfcsd.org/human-resources', 'www.sgfcsd.org', (43.2729737057, -73.6477454182)],
['SOUTH HUNTINGTON UNION FREE SCHOOL DISTRICT', 'http://www.shufsd.org/district/employment', 'www.shufsd.org', (40.8211817435, -73.4185988209)],
['SOUTH JEFFERSON CENTRAL SCHOOL DISTRICT', 'http://www.spartanpride.org/districtpage.cfm?pageid=1729', 'www.spartanpride.org', (43.8695949191, -76.0145049667)],
['SOUTH KORTRIGHT CENTRAL SCHOOL DISTRICT', 'http://www.skcs.org/Employment.aspx', 'www.skcs.org', (42.3523962849, -74.6981639819)],
['SOUTH LEWIS CENTRAL SCHOOL DISTRICT', 'https://www.southlewis.org/employment-opportunities--163', 'www.southlewis.org', (43.6361018632, -75.394833243)],
['SOUTH MOUNTAIN-HICKORY COMMON SCHOOL DISTRICT AT BINGHAMTON', '', ' ', (42.0763946683, -75.9302145853)],
['SOUTH ORANGETOWN CENTRAL SCHOOL DISTRICT', 'https://www.socsd.org', 'www.socsd.org', (41.0616017342, -73.9680185669)],
['SOUTH SENECA CENTRAL SCHOOL DISTRICT', '', 'www.southseneca.org', (42.6725431647, -76.8236623172)],
['SOUTHAMPTON UNION FREE SCHOOL DISTRICT', 'http://www.southamptonschools.org/Page/56', 'www.southamptonschools.org', (40.8904512685, -72.3789734785)],
['SOUTHERN CAYUGA CENTRAL SCHOOL DISTRICT', 'http://www.southerncayuga.org', 'www.southerncayuga.org', (42.73405925, -76.61577581)],
['SOUTHOLD UNION FREE SCHOOL DISTRICT', 'http://southoldufsd.com', 'www.southoldufsd.com', (41.0588416382, -72.431759121)],
['SOUTHWESTERN CENTRAL SCHOOL DISTRICT AT JAMESTOWN', '', 'www.swcs.wnyric.org', (42.0897332353, -79.2937007668)],
['SPACKENKILL UNION FREE SCHOOL DISTRICT', '', 'www.sufsdny.org', (41.6617807453, -73.9249308578)],
['SPENCERPORT CENTRAL SCHOOL DISTRICT', 'http://www.spencerportschools.org/departments_and_programs/human_resources/JobOpportunities', 'www.spencerportschools.org', (43.1870962411, -77.7914514141)],
['SPENCER-VAN ETTEN CENTRAL SCHOOL DISTRICT', 'http://www.svecsd.org', 'www.svecsd.org', (42.2040293406, -76.5224411572)],
['SPRINGS UNION FREE SCHOOL DISTRICT', 'http://www.springsschool.org/district/employment', 'www.springsschool.org', (41.0173463451, -72.1564729555)],
['SPRINGVILLE-GRIFFITH INSTITUTE CENTRAL SCHOOL DISTRICT', 'http://www.springvillegi.org/available-positions', 'www.springvillegi.org', (42.5157227135, -78.6545643771)],
['STAMFORD CENTRAL SCHOOL DISTRICT', 'http://www.stamfordcs.org/Employment.aspx', 'www.stamfordcs.org', (42.4117356603, -74.620740431)],
['STARPOINT CENTRAL SCHOOL DISTRICT', 'http://www.starpointcsd.org/Page/42', 'www.starpointcsd.org', (43.1243015805, -78.8073792806)],
['STILLWATER CENTRAL SCHOOL DISTRICT', '', 'www.scsd.org', (42.9480805907, -73.6392841568)],
['STOCKBRIDGE VALLEY CENTRAL SCHOOL DISTRICT', 'http://www.stockbridgevalley.org', 'www.stockbridgevalley.org', (42.9801264637, -75.5978395215)],
['SUFFERN CENTRAL SCHOOL DISTRICT ', 'http://www.sufferncentral.org/human-resources', 'www.sufferncentral.org', (41.12502741, -74.17001854)],
['SULLIVAN WEST CENTRAL SCHOOL DISTRICT', '', 'www.swcsd.org', (41.7797669076, -74.9400402698)],
['SUSQUEHANNA VALLEY CENTRAL SCHOOL DISTRICT', 'http://www.svsabers.org/EmploymentOpportunities.aspx', 'www.svsabers.org', (42.0772530835, -75.8220424439)],
['SWEET HOME CENTRAL SCHOOL DISTRICT', 'http://sweethomeschools.org/District/2200-Employment-Opportunities.html', 'www.sweethomeschools.org', (43.0106402616, -78.798724467)],
['SYOSSET CENTRAL SCHOOL DISTRICT', '', 'http://syossetschools.org', (40.8322324446, -73.4870987892)],
['SYRACUSE CITY SCHOOL DISTRICT', '', 'www.syracusecityschools.com', (43.044811314, -76.13959765)],
['TACONIC HILLS CENTRAL SCHOOL DISTRICT', 'http://www.taconichills.k12.ny.us/site/Default.aspx?PageID=193', 'www.taconichills.k12.ny.us', (0.0, 0.0)],
['THE ENLARGED CITY SCHOOL DISTRICT OF THE CITY OF SARATOGA SPRINGS', 'https://www.saratogaschools.org/district.cfm?subpage=1383228', 'www.saratogaschools.org', (43.0726755096, -73.8025849123)],
['THOUSAND ISLANDS CENTRAL SCHOOL DISTRICT', 'http://www.1000islandsschools.org', 'www.1000islandsschools.org', (44.1928247329, -76.2003901511)],
['THREE VILLAGE CENTRAL SCHOOL DISTRICT', '', 'www.3villagecsd.org', (40.91982626, -73.13292454)],
['TICONDEROGA CENTRAL SCHOOL DISTRICT', 'http://www.ticonderogak12.org/Employment', 'www.ticonderogak12.org', (43.8428210701, -73.4274585858)],
['TIOGA CENTRAL SCHOOL DISTRICT', 'http://www.tiogacentral.org', 'www.tiogacentral.org', (42.0556350422, -76.3482999485)],
['TONAWANDA CITY SCHOOL DISTRICT', 'http://www.tonawandacsd.org/Page/39', 'www.tonawandacsd.org', (43.0114168127, -78.8968629428)],
['TOWN OF WEBB UNION FREE SCHOOL DISTRICT', 'http://www.towschool.org/our_district/employment_opportunities', 'www.towschool.org', (43.7075434459, -74.9763662401)],
['TRI-VALLEY CENTRAL SCHOOL DISTRICT', 'https://www.trivalleycsd.org/domain/124', 'www.trivalleycsd.org', (41.84925922, -74.5364442587)],
['TROY CITY SCHOOL DISTRICT', 'http://www.troycsd.org/district-services/human-resources', 'www.troycsd.org', (42.7123114019, -73.6974486246)],
['TRUMANSBURG CENTRAL SCHOOL DISTRICT', 'http://www.tburgschools.org/districtpage.cfm?pageid=433', 'www.tburgschools.org', (42.5378758139, -76.6557270718)],
['TUCKAHOE COMMON SCHOOL DISTRICT', '', 'www.tuckahoecommonsd.com', (40.8975005552, -72.4161113409)],
['TUCKAHOE UNION FREE SCHOOL DISTRICT', 'http://www.tuckahoeschools.org/employment_opportunities', 'www.tuckahoeschools.org', (40.9428609853, -73.8124149872)],
['TULLY CENTRAL SCHOOL DISTRICT', 'http://tullyschools.org/teacherpage.cfm?teacher=694', 'www.tullyschools.org', (42.7958113695, -76.1123876344)],
['TUPPER LAKE CENTRAL SCHOOL DISTRICT', 'http://www.tupperlakecsd.net', 'www.tupperlakecsd.net', (44.2240590816, -74.4436882831)],
['TUXEDO UNION FREE SCHOOL DISTRICT', 'http://www.tuxedoufsd.org', 'www.tuxedoufsd.org', (41.1885438069, -74.1852662273)],
['UNADILLA VALLEY CENTRAL SCHOOL DISTRICT', 'http://www.uvstorm.org/EmploymentOpportunities.aspx', 'www.uvstorm.org', (42.585192115, -75.3350464784)],
['UNION FREE SCHOOL DISTRICT OF THE TARRYTOWNS', '', 'www.tufsd.org', (41.0828828019, -73.8585664166)],
['UNION SPRINGS CENTRAL SCHOOL DISTRICT', '', 'www.unionspringscsd.org', (42.8505805511, -76.6909061775)],
['UNIONDALE UNION FREE SCHOOL DISTRICT', 'http://district.uniondaleschools.org/job_postings', 'www.district.uniondaleschools.org', (40.7048486464, -73.5837606438)],
['UNION-ENDICOTT CENTRAL SCHOOL DISTRICT', 'http://www.uek12.org/Employment.aspx', 'www.uek12.org', (42.09688388, -76.05076497)],
['UTICA CITY SCHOOL DISTRICT', '', 'www.uticacsd.org', (43.0875407671, -75.2534501841)],
['VALHALLA UNION FREE SCHOOL DISTRICT', 'http://www.valhallaschools.org', 'www.valhallaschools.org', (41.0932251215, -73.7775552201)],
['VALLEY CENTRAL SCHOOL DISTRICT (MONTGOMERY)', '', 'www.vcsd.k12.ny.us', (41.5278361004, -74.1877746304)],
['VALLEY STREAM 13 UNION FREE SCHOOL DISTRICT', 'http://valleystream13.com/departments/human-resources', 'www.valleystream13.com', (40.6818054321, -73.6889230044)],
['VALLEY STREAM 24 UNION FREE SCHOOL DISTRICT', 'http://www.valleystreamdistrict24.org/employment-opportunities-1.html', 'www.valleystreamdistrict24.org', (40.6526617934, -73.6909787026)],
['VALLEY STREAM 30 UNION FREE SCHOOL DISTRICT', 'http://www.valleystream30.com/our_district/employmentcareers', 'www.valleystream30.com', (40.672711812, -73.7087886832)],
['VALLEY STREAM CENTRAL HIGH SCHOOL DISTRICT', 'http://www.vschsd.org/district/employment', 'www.vschsd.org', (40.6734124753, -73.6999126975)],
['VAN HORNESVILLE-OWEN D YOUNG CENTRAL SCHOOL DISTRICT', '', 'odyoung-csd.k-12.ny.us', (42.8964030448, -74.8261870869)],
['VESTAL CENTRAL SCHOOL DISTRICT', '', 'www.vestal.k12.ny.us', (42.0847915733, -76.0510978041)],
['VICTOR CENTRAL SCHOOL DISTRICT', '', 'www.victorschools.org', (42.9923166459, -77.4190636296)],
['VOORHEESVILLE CENTRAL SCHOOL DISTRICT', 'http://www.voorheesville.org/domain/40', 'www.voorheesville.org', (42.6414058637, -73.9642097113)],
['WAINSCOTT COMMON SCHOOL DISTRICT', 'http://www.wainscottschool.org', 'www.wainscottschool.org', (40.9345016908, -72.24994916)],
['WALLKILL CENTRAL SCHOOL DISTRICT', '', 'www.wallkillcsd.k12.ny.us', (41.6057914313, -74.1819402059)],
['WALTON CENTRAL SCHOOL DISTRICT', 'http://www.waltoncsd.org', 'www.waltoncsd.org', (42.160065297, -75.125323579)],
['WANTAGH UNION FREE SCHOOL DISTRICT', 'http://www.wantaghschools.org/domain/956', 'www.wantaghschools.org', (40.6891950939, -73.5163237242)],
['WAPPINGERS CENTRAL SCHOOL DISTRICT', 'http://www.wappingersschools.org', 'www.wappingersschools.org', (41.5368704423, -73.8408321707)],
['WARRENSBURG CENTRAL SCHOOL DISTRICT', '', 'www.wcsd.org', (43.4978112051, -73.7624584631)],
['WARSAW CENTRAL SCHOOL DISTRICT', '', 'www.warsawcsd.org', (42.7405924515, -78.1376343473)],
['WARWICK VALLEY CENTRAL SCHOOL DISTRICT', 'https://www.warwickvalleyschools.com/employment', 'www.warwickvalleyschools.com', (41.2541044733, -74.3876530177)],
['WASHINGTONVILLE CENTRAL SCHOOL DISTRICT', 'https://www.ws.k12.ny.us/JobPostings.aspx', 'www.ws.k12.ny.us', (41.4244883233, -74.1716369806)],
['WATERFORD-HALFMOON UNION FREE SCHOOL DISTRICT', 'http://www.whufsd.org', 'www.whufsd.org', (42.8113265603, -73.6851133298)],
['WATERLOO CENTRAL SCHOOL DISTRICT', 'https://www.waterloocsd.org/Page/66', 'www.waterloocsd.org', (42.8963558681, -76.8622912961)],
['WATERTOWN CITY SCHOOL DISTRICT', '', 'www.watertowncsd.org', (43.957264467, -75.910552653)],
['WATERVILLE CENTRAL SCHOOL DISTRICT', 'http://www.watervillecsd.org/site/default.aspx?pageid=1', 'www.watervillecsd.org', (42.9244713721, -75.3914479684)],
['WATERVLIET CITY SCHOOL DISTRICT', 'https://www.watervlietcityschools.org/employment', 'www.watervlietcityschools.org', (42.7310960811, -73.715953162)],
['WATKINS GLEN CENTRAL SCHOOL DISTRICT', 'http://www.wgcsd.org/employment.cfm', 'www.wgcsd.org', (42.3750842938, -76.8663573316)],
['WAVERLY CENTRAL SCHOOL DISTRICT', 'http://community.waverlyschools.com/employment', 'www.waverlyschools.com', (42.0138198756, -76.5311777946)],
['WAYLAND-COHOCTON CENTRAL SCHOOL DISTRICT', 'http://www.wccsk12.org', 'www.wccsk12.org', (42.5618741547, -77.600121354)],
['WAYNE CENTRAL SCHOOL DISTRICT', '', 'www.waynecsd.org', (43.22366242, -77.30430116)],
['WEBSTER CENTRAL SCHOOL DISTRICT', '', 'www.websterschools.org', (43.207913473, -77.432871397)],
['WEEDSPORT CENTRAL SCHOOL DISTRICT', 'http://www.weedsport.org', 'www.weedsport.org', (43.0473121471, -76.5539499669)],
['WELLS CENTRAL SCHOOL DISTRICT', '', 'www.wellscsd.com', (43.4216414674, -74.2753559928)],
['WELLSVILLE CENTRAL SCHOOL DISTRICT', '', 'www.wellsvilleschools.org', (42.1191860053, -77.9486720118)],
['WEST BABYLON UNION FREE SCHOOL DISTRICT', 'http://www.wbschools.org/District/employment_opportunities', 'www.wbschools.org', (40.7044201389, -73.3451805153)],
['WEST CANADA VALLEY CENTRAL SCHOOL DISTRICT', 'http://www.westcanada.org/domain/93', 'www.westcanada.org', (43.1635594574, -75.0011945695)],
['WEST GENESEE CENTRAL SCHOOL DISTRICT', 'https://www.westgenesee.org/staff-resources/job-opportunities', 'www.westgenesee.org', (43.0459845163, -76.2676415089)],
['WEST HEMPSTEAD UNION FREE SCHOOL DISTRICT', 'http://www.whufsd.com/district/human_resources', 'www.whufsd.com', (40.697326288, -73.6517477231)],
['WEST IRONDEQUOIT CENTRAL SCHOOL DISTRICT', '', 'www.westirondequoit.org', (43.2166516008, -77.5925908427)],
['WEST ISLIP UNION FREE SCHOOL DISTRICT', 'http://www.wi.k12.ny.us/district/office_of_human_resources', 'www.wi.k12.ny.us', (40.704655677, -73.303633885)],
['WEST PARK UNION FREE SCHOOL DISTRICT', '', ' ', (41.7949150775, -73.9599950357)],
['WEST SENECA CENTRAL SCHOOL DISTRICT', 'https://www.wscschools.org/Page/291', 'www.wscschools.org', (42.8355863401, -78.791447212)],
['WEST VALLEY CENTRAL SCHOOL DISTRICT', 'http://www.wvalley.wnyric.org/Page/159', 'www.wvalley.wnyric.org', (42.4059879288, -78.6093925472)],
['WESTBURY UNION FREE SCHOOL DISTRICT', 'http://www.westburyschools.org', 'www.westburyschools.org', (40.76860121, -73.58428282)],
['WESTFIELD CENTRAL SCHOOL DISTRICT', 'http://www.wacs.wnyric.org/Page/1330', 'www.wacs.wnyric.org', (42.3288105051, -79.5680182556)],
['WESTHAMPTON BEACH UNION FREE SCHOOL DISTRICT', '', 'www.whbschools.org', (40.8173913128, -72.6509029373)],
['WESTHILL CENTRAL SCHOOL DISTRICT', 'http://www.westhillschools.org/teacherpage.cfm?teacher=448', 'www.westhillschools.org', (43.0411013422, -76.223867654)],
['WESTMORELAND CENTRAL SCHOOL DISTRICT', 'http://www.westmorelandschool.org/Page/1867', 'www.westmorelandschool.org', (43.113301428, -75.4007419963)],
['WHEATLAND-CHILI CENTRAL SCHOOL DISTRICT', '', 'www.wheatland.k12.ny.us', (43.0253795861, -77.7481066726)],
['WHEELERVILLE UNION FREE SCHOOL DISTRICT', 'http://www.wufsk8.com', 'www.wufsk8.com', (43.1235767553, -74.4992223809)],
['WHITE PLAINS CITY SCHOOL DISTRICT', 'https://www.whiteplainspublicschools.org/Page/546', 'www.whiteplainspublicschools.org', (41.0067137735, -73.7329566979)],
['WHITEHALL CENTRAL SCHOOL DISTRICT', 'https://www.railroaders.net/EmploymentHAL.php', 'www.railroaders.net', (43.5513726513, -73.3745742971)],
['WHITESBORO CENTRAL SCHOOL DISTRICT', 'http://www.wboro.org/Page/32', 'www.wboro.org', (43.1152313006, -75.2914280069)],
['WHITESVILLE CENTRAL SCHOOL DISTRICT', '', 'www.whitesvillesd.org', (42.0385725414, -77.7800671232)],
['WHITNEY POINT CENTRAL SCHOOL DISTRICT', 'https://www.wpcsd.org/EmploymentOpportunities.aspx', 'www.wpcsd.org', (42.3377015058, -75.9726777703)],
['WILLIAM FLOYD UNION FREE SCHOOL DISTRICT', 'http://www.wfsd.k12.ny.us/index.php/employment-opportunities', 'www.wfsd.k12.ny.us', (40.7803191142, -72.8485664177)],
['WILLIAMSON CENTRAL SCHOOL DISTRICT', '', 'www.williamsoncentral.org', (43.2209974496, -77.1821860949)],
['WILLIAMSVILLE CENTRAL SCHOOL DISTRICT', 'http://www.williamsvillek12.org/departments/human_resources/career_opportunities.php', 'www.williamsvillek12.org', (43.024134053, -78.7328717039)],
['WILLSBORO CENTRAL SCHOOL DISTRICT', 'http://www.willsborocsd.org/district/employment', 'www.willsborocsd.org', (44.3756609718, -73.3901185644)],
['WILSON CENTRAL SCHOOL DISTRICT', '', 'www.wilson.wnyric.org', (0.0, 0.0)],
['WINDHAM-ASHLAND-JEWETT CENTRAL SCHOOL DISTRICT', 'http://www.wajcs.org/?PageName=bc&n=246209', 'www.wajcs.org', (42.3074038733, -74.2549749881)],
['WINDSOR CENTRAL SCHOOL DISTRICT', 'https://www.windsor-csd.org/Employment.aspx', 'www.windsor-csd.org', (42.069112815, -75.6411453176)],
['WORCESTER CENTRAL SCHOOL DISTRICT', 'http://www.worcestercs.org/employment-opportunities.html', 'www.worcestercs.org', (42.5917714196, -74.7439881914)],
['WYANDANCH UNION FREE SCHOOL DISTRICT', 'http://www.wyandanch.k12.ny.us', 'www.wyandanch.k12.ny.us', (40.74623637, -73.36430561)],
['WYNANTSKILL UNION FREE SCHOOL DISTRICT', 'http://www.wynantskillufsd.org/district/employment', 'www.wynantskillufsd.org', (42.6925014009, -73.6609385935)],
['WYOMING CENTRAL SCHOOL DISTRICT', 'https://www.wyomingcsd.org/Page/20', 'www.wyomingcsd.org', (42.8211541747, -78.0934019776)],
['YONKERS CITY SCHOOL DISTRICT', 'http://www.yonkerspublicschools.org/Page/1191', 'www.yonkerspublicschools.org', (40.9360058121, -73.9015333257)],
['YORK CENTRAL SCHOOL DISTRICT', 'http://www.yorkcsd.org/Page/65', 'www.yorkcsd.org', (42.8306309782, -77.8856279494)],
['YORKSHIRE-PIONEER CENTRAL SCHOOL DISTRICT', '', 'www.pioneerschools.org', (42.5244517062, -78.4643211861)],
['YORKTOWN CENTRAL SCHOOL DISTRICT', '', 'www.yorktown.org', (41.2948292175, -73.8018078166)]
]






    # Advanced options
    max_crawl_depth = 2
    num_procs = 8


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

        # Add scheme if necessary
        if not homepage.startswith('http'):
            homepage = 'http://' + homepage

        # Put civil service URLs, initial crawl level, portal url, and jbws type into queue
        all_urls_q.put([homepage, 0, homepage, 'sch'])

        # Put portal URL into checked pages
        dup_checker = dup_checker_f(homepage)
        checkedurls_man_list.append([dup_checker, None])

    # Clear list to free up memory
    all_list2 = None




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


    # Display sorted results in handy format
    with lock:
        for i in sort_dict:
            print("\n\n['" + i + "', ''],")
            temp = sorted(sort_dict[i], key = lambda x: int(x[1]), reverse=True)
            for ii in temp: 
                print(ii[0])




'''
# Find matching URLs from old db
for i in sort_dict.items():
    print('\n\n=', i[0])
    for ii in i[1]:
        for iii in uni_list:
            if iii == ii[0]:
                print('Match:', iii)
'''



















