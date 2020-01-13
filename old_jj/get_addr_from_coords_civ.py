
# Desc: Get street addresses from coordinates



import geopy
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="jj")



the_list = [
['Albany City', 'https://www.albanyny.gov/government/departments/humanresources/employment/', 'https://www.albanyny.gov/government/departments/humanresources/employment', (42.6511674, -73.754968)],
['Albany County', 'http://www.albanycounty.com/civilservice/', 'http://www.albanycounty.com/Government/Departments/DepartmentofCivilService.aspx', (42.6511674, -73.754968)],
['Allegany County', 'http://www.alleganyco.com/departments/human-resources-civil-service/', 'http://www.alleganyco.com/departments/human-resources-civil-service/', (42.2231241, -78.0344506)],
['Amherst Town', 'http://www.amherst.ny.us/govt/govt_dept.asp?dept_id=dept_12&div_id=div_18&menu_id=menu_04&_sm_au_=iVV8Z8Lp1WfFsNV6', 'http://www.amherst.ny.us', (42.9637836, -78.7377258)],
['Auburn City', 'http://www.auburnny.gov/Public_Documents/AuburnNY_CivilService/index', 'http://www.auburnny.gov/public_documents/auburnny_civilservice/index', (42.9320202, -76.5672029)],
['Batavia City', 'http://www.batavianewyork.com/fire-department/pages/employment', 'https://www.batavianewyork.com/fire-department/pages/employment', (42.9980144, -78.1875515)],
['Bethlehem Town', 'http://www.townofbethlehem.org/137/Human-Resources?_sm_au_=iVV8Z8Lp1WfFsNV6', 'http://www.townofbethlehem.org/137/Human-Resources?_sm_au_=ivv8z8lp1wffsnv6', (42.6220235, -73.8326232)],
['Binghamton City', 'http://www.binghamton-ny.gov/departments/personnel/employment/employment', 'http://www.binghamton-ny.gov/departments/personnel/employment/employment', (42.096968, -75.914341)],
['Brighton Town', 'http://www.townofbrighton.org/index.aspx?nid=219&_sm_au_=iVV8Z8Lp1WfFsNV6', 'https://www.townofbrighton.org/219/Human-Resources', (43.1635257, -77.6083784825996)],
['Bronx County', 'https://www1.nyc.gov/jobs/index.page', 'https://www1.nyc.gov/jobs', (40.7308619, -73.9871558)],
['Brookhaven Town', 'https://www.brookhavenny.gov/', 'https://www.brookhavenny.gov/', (40.8312096, -73.029552)],
['Broome County', 'http://www.gobroomecounty.com/personnel/cs', 'http://www.gobroomecounty.com/personnel/cs', (42.1156308, -75.9588092)],
['Buffalo City', 'https://www.buffalony.gov/1001/Employment-Resources', 'https://www.buffalony.gov/1001/Employment-Resources', (42.8867166, -78.8783922)],
['Carmel Town', 'https://www.putnamcountyny.com/personneldept/exam-postings/', 'https://www.putnamcountyny.com/personneldept/', (41.4266361, -73.6788272)],
['Cattaraugus County', 'http://www.cattco.org/jobs', 'https://www.cattco.org/human-resources/jobs', (42.252563, -78.80559)],
['Cayuga County', 'http://www.cayugacounty.us/Community/CivilServiceCommission/ExamAnnouncementsVacancies.aspx', 'http://www.cayugacounty.us/QuickLinks.aspx?CID=103', (42.932628, -76.5643831)],
['Chautauqua County', 'http://www.co.chautauqua.ny.us/314/Human-Resources', 'http://www.co.chautauqua.ny.us/314/Human-Resources', (42.253947, -79.504491)],
['Chemung County', 'http://www.chemungcountyny.gov/departments/a_-_f_departments/civil_service_personnel/index.php', 'https://www.chemungcountyny.gov/departments/a_-_f_departments/civil_service_personnel/index.php', (42.0897965, -76.8077338)],
['Chenango County', 'http://www.co.chenango.ny.us/personnel/examinations/', 'http://www.co.chenango.ny.us/personnel/examinations/', (42.531184, -75.5235149)],
['Chili Town', 'http://www.townofchili.org/notice-category/job-postings/', 'http://www.townofchili.org/notice-category/job-postings/', (43.157285, -77.615214)],
['Cicero Town', 'http://www.ongov.net/employment/jurisdiction.html?_sm_au_=iVVrLpv4fvqPNjQj', 'http://www.ongov.net/employment/civilService.html', (43.0481221, -76.1474244)],
['City University of New York (CUNY)', 'http://www.cuny.edu/employment/civil-service.html', 'https://www2.cuny.edu/employment/civil-service/', (40.7308619, -73.9871558)],
['Clarkstown Town', 'http://rocklandgov.com/departments/personnel', 'http://rocklandgov.com/departments/personnel/civil-service-examinations', (41.1469917, -73.9902998)],
['Clifton Park Town', 'http://www.cliftonpark.org/services/employment-applications.html', 'https://www.cliftonpark.org/services/employment-applications.html', (42.8656325, -73.7709535)],
['Clinton County', 'http://www.clintoncountygov.com/Departments/Personnel/PersonnelHomePage.htm', 'https://www.clintoncountygov.com/employment', (44.69282, -73.45562)],
['Cohoes City', 'https://www.ci.cohoes.ny.us/', 'https://www.ci.cohoes.ny.us/', (42.7742446, -73.7001187)],
['Colonie Town', 'https://www.colonie.org/departments/civilservice/', 'https://www.colonie.org/departments/civilservice/', (42.7442986, -73.7614799)],
['Columbia County', 'https://sites.google.com/a/columbiacountyny.com/civilservice/', 'https://sites.google.com/a/columbiacountyny.com/civilservice/', (42.2528649, -73.790959)],
['Cortland County', 'http://www.cortland-co.org/263/Personnel-Civil%20Service', 'http://www.cortland-co.org/263/Personnel-Civil-Service', (42.6000833, -76.1804347)],
['Cortlandt Town', 'http://www.townofcortlandt.com/Cit-e-Access/webpage.cfm?TID=20&TPID=2522&_sm_au_=iVVt78QZ5W7P2qHF', 'http://www.townofcortlandt.com', (41.248774, -73.9086846461571)],
['De Witt Town', 'http://www.ongov.net/employment/jurisdiction.html', 'http://www.ongov.net/employment/civilService.html', (43.0481221, -76.1474244)],
['Delaware County', 'http://www.co.delaware.ny.us/departments/pers/pers.htm', 'http://www.co.delaware.ny.us/departments/pers/jobs.htm', (42.2781401, -74.9159946)],
['Dutchess County', 'https://www.dutchessny.gov/Departments/Human-Resources/Human-Resources.htm', 'https://www.dutchessny.gov/Departments/Human-Resources/Human-Resources.htm', (41.7065779, -73.9284101)],
['East Fishkill Town', 'http://eastfishkillny.gov/government/employment.htm', 'http://eastfishkillny.gov/government/employment.htm', (41.5839824, -73.8087442)],
['Eastchester Town', 'http://www.eastchester.org/departments/comptoller.php', 'http://www.eastchester.org/departments/comptoller.php', (40.9562415, -73.8129474)],
['Elmira City', 'http://www.cityofelmira.net/personnel', 'http://www.cityofelmira.net/personnel', (42.0897965, -76.8077338)],
['Erie County', 'http://www.erie.gov/employment/', 'http://www2.erie.gov/employment/', (42.8867166, -78.8783922)],
['Essex County', 'http://www.co.essex.ny.us/jobs.asp', 'http://www.co.essex.ny.us/jobs.asp', (44.216171, -73.591232)],
['Franklin County', 'https://countyfranklin.digitaltowpath.org:10078/content/Departments/View/6:field=services;/content/DepartmentServices/View/48', 'https://countyfranklin.digitaltowpath.org:10078/content/Departments/View/6:field=services;/content/DepartmentServices/View/48', (44.831732274226, -74.5184874695369)],
['Fulton County', 'http://www.fultoncountyny.gov/node/5', 'https://www.fultoncountyny.gov/node/5', (43.0068689, -74.3676437)],
['Genesee County', 'http://www.co.genesee.ny.us/departments/humanresources/index.html', 'http://www.co.genesee.ny.us/departments/humanresources/index.php', (42.9980144, -78.1875515)],
['Geneva City', 'http://www.co.ontario.ny.us/index.aspx?nid=94', 'http://www.co.ontario.ny.us/jobs.aspx', (42.8844625, -77.278399)],
['Glen Cove City', 'http://www.cityofglencoveny.org/index.htm', 'http://www.cityofglencoveny.org/index.htm', (40.862755, -73.6336094)],
['Glens Falls City', 'http://www.cityofglensfalls.com/index.aspx?NID=55', 'http://www.cityofglensfalls.com/55/Human-Resources-Department', (43.3772932, -73.6131714)],
['Glenville Town', 'http://www.schenectadycounty.com/FullStory.aspx?m=36&amid=373&_sm_au_=iVVt78QZ5W7P2qHF', 'https://www.schenectadycounty.com/', (42.8143922952735, -73.9420906329747)],
['Greece Town', '_DUP._http://www2.monroecounty.gov/employment-index.php', 'https://www2.monroecounty.gov/careers', (43.157285, -77.615214)],
['Greenburgh Town', 'http://www.greenburghny.com/Cit-e-Access/webpage.cfm?TID=10&TPID=2491&_sm_au_=iVVt78QZ5W7P2qHF', 'http://www.greenburghny.com', (41.0447887, -73.803487)],
['Greene County', 'http://greenegovernment.com/departments/human-resources-and-civil-service#civil-service', 'http://www.greenegovernment.com/departments/human-resources-and-civil-service', (42.1956438, -74.1337508)],
['Guilderland Town', 'http://www.townofguilderland.org/pages/guilderlandny_hr/index?_sm_au_=iVV8Z8Lp1WfFsNV6', 'https://www.townofguilderland.org/human-resource-department?_sm_au_=ivv8z8lp1wffsnv6', (42.704522, -73.911513)],
['Hamilton County', 'http://www.hamiltoncounty.com/government/departments-services#PersonnelDepartment', 'https://www.hamiltoncounty.com/government/departments-services', (43.47111, -74.412804)],
['Haverstraw Town', '_DUP._http://rocklandgov.com/departments/personnel/', 'http://rocklandgov.com/departments/personnel/civil-service-examinations', (41.1469917, -73.9902998)],
['Hempstead Town', 'https://hempsteadny.gov/employment-services', 'https://hempsteadny.gov/employment-services', (40.7063185, -73.618684)],
['Hempstead Village', 'http://villageofhempstead.org/197/Employment-Opportunities', 'https://www.villageofhempstead.org/197/Employment-Opportunities', (40.7063185, -73.618684)],
['Herkimer County', 'https://countyherkimer.digitaltowpath.org:10069/content/Departments/View/9', 'https://countyherkimer.digitaltowpath.org:10069/content/Departments/View/9', (43.0256259, -74.9859889)],
['Huntington Town', 'http://www.huntingtonny.gov/content/13753/13757/17478/17508/default.aspx?_sm_au_=iVVt78QZ5W7P2qHF', 'http://www.huntingtonny.gov/content/13753/13757/17478/17508/default.aspx?_sm_au_=ivvt78qz5w7p2qhf', (40.868154, -73.425676)],
['Irondequoit Town', 'http://www.irondequoit.org/town-departments/human-resources/town-employment-opportunities?_sm_au_=iVV8Z8Lp1WfFsNV6', 'http://www.irondequoit.org/town-departments/human-resources/town-employment-opportunities?_sm_au_=ivv8z8lp1wffsnv6', (43.1854754, -77.6106861508176)],
['Islip Town', 'https://www.townofislip-ny.gov/?Itemid=220', 'https://www.townofislip-ny.gov/?Itemid=220', (40.7360109, -73.2089705862445)],
['Ithaca City', 'https://ithaca-portal.mycivilservice.com/', 'https://ithaca-portal.mycivilservice.com/', (42.4396039, -76.4968019)],
['Jamestown City', '_DUP._http://www.co.chautauqua.ny.us/314/Human-Resources', 'http://www.co.chautauqua.ny.us/314/Human-Resources', (42.253947, -79.504491)],
['Jefferson County', 'http://www.co.jefferson.ny.us/index.aspx?page=83', 'https://co.jefferson.ny.us/', (43.9747838, -75.9107565)],
['Kings County', '_DUP._http://www1.nyc.gov/jobs/index.page', 'https://www1.nyc.gov/jobs', (40.7308619, -73.9871558)],
['Kingston City', 'http://kingston-ny.gov/Employment', 'https://kingston-ny.gov/employment', (41.9287812, -74.0023702)],
['Lackawanna City', 'http://www.lackawannany.gov/departments/civil-service/', 'http://lackawannany.gov/government/civil-service/', (42.8262, -78.820732)],
['Lewis County', 'https://www.lewiscounty.org/departments/human-resources/human-resources', 'https://www.lewiscounty.org/departments/human-resources/human-resources', (43.7884182, -75.4935757)],
['Lindenhurst Village', 'http://www.suffolkcountyny.gov/Departments/CivilService.aspx', 'https://www.suffolkcountyny.gov/Departments/Civil-Service', (40.8256537, -73.2026138)],
['Livingston County', 'https://www.livingstoncounty.us/207/Personnel-Department', 'https://www.livingstoncounty.us/207/Personnel-Department', (42.795896, -77.816947)],
['Lockport City', 'http://www.lockportny.gov/residents/city-departments/employment//', 'https://www.lockportny.gov/current-exams-and-openings/', (43.168863, -78.6929557832681)],
['Long Beach City', 'https://www.longbeachny.gov/index.asp?Type=B_BASIC&SEC={9C88689C-135F-4293-A9CE-7A50346BEA23}', 'https://www.longbeachny.gov/index.asp?type=b_basic&amp;sec={9c88689c-135f-4293-a9ce-7a50346bea23}', (40.58888905, -73.6648751135986)],
['Madison County', 'https://www.madisoncounty.ny.gov/287/Personnel', 'https://www.madisoncounty.ny.gov/287/Personnel', (43.075408, -75.70713)],
['Manlius Town', '_DUP._http://www.ongov.net/employment/jurisdiction.html', 'http://www.ongov.net/employment/civilService.html', (43.0481221, -76.1474244)],
['Mechanicville', 'http://www.mechanicville.com/index.aspx?nid=563', 'http://www.mechanicville.com/index.aspx?nid=563', (42.903367, -73.686416)],
['Middletown City', 'http://www.middletown-ny.com/departments/civil-service.html?_sm_au_=iVVrLpv4fvqPNjQj', 'https://www.middletown-ny.com/en/departments/civil-service.html?_sm_au_=ivvrlpv4fvqpnjqj', (41.44591415, -74.4224417389405)],
['Monroe County', 'http://www2.monroecounty.gov/employment-index.php', 'https://www2.monroecounty.gov/careers', (43.157285, -77.615214)],
['Monroe Town', 'http://www.monroeny.org/departments2/human-resources.html', 'https://www.monroeny.org/doc-center/town-of-monroe-job-opportunities.html', (41.3304767, -74.1866348)],
['Montgomery County', 'https://www.co.montgomery.ny.us/sites/public/government/personnel/Personnel_Development/default.aspx', 'https://www.co.montgomery.ny.us/web/sites/departments/personnel/employment.asp', (42.9545179, -74.3765241)],
['Mount Vernon City', 'http://cmvny.com/departments/civil-service/', 'http://cmvny.com/departments/civil-service/job-postings', (40.9125992, -73.8370786)],
['Nassau County', 'http://www.nassaucivilservice.com/NCCSWeb/homepage.nsf/HomePage?ReadForm', 'http://www.nassaucivilservice.com/nccsweb/homepage.nsf/homepage?readform', (40.7063185, -73.618684)],
['New Rochelle', 'http://www.newrochelleny.com/index.aspx?nid=362', 'https://www.newrochelleny.com/362/Civil-Service', (40.9114459, -73.7841684271834)],
['New York City', 'http://www1.nyc.gov/jobs', 'https://www1.nyc.gov/jobs', (40.7308619, -73.9871558)],
['Newburgh City', 'http://www.cityofnewburgh-ny.gov/civil-service', 'https://www.cityofnewburgh-ny.gov/civil-service', (41.5034271, -74.0104179)],
['Niagara County', 'http://www.niagaracounty.com/Departments/CivilService.aspx', 'http://www.niagaracounty.com/Departments/Civil-Service', (43.168863, -78.6929557832681)],
['Niagara Falls City', 'http://niagarafallsusa.org/government/city-departments/human-resources-department/', 'http://niagarafallsusa.org/government/city-departments/human-resources-department/', (43.1030928, -79.0302618)],
['North Hempstead Town', 'https://www.northhempsteadny.gov/employment-opportunities', 'https://www.northhempsteadny.gov/employment-opportunities', (40.7978787, -73.6995749)],
['Norwich City', 'http://www.norwichnewyork.net/human_resources.html', 'https://www.norwichnewyork.net/government/human-resources.php', (42.531184, -75.5235149)],
['Ogdensburg', 'http://www.ogdensburg.org/index.aspx?nid=97', 'http://www.ogdensburg.org/index.aspx?nid=97', (44.694285, -75.486374)],
['Oneida City', 'http://oneidacity.com/civil-service/', 'http://oneidacity.com/473-2/', (43.2144051, -75.4039155)],
['Oneida County', 'http://ocgov.net/personnel', 'http://ocgov.net/personnel', (43.104752, -75.2229497)],
['Oneonta City', 'http://www.oneonta.ny.us/departments/personnel/', 'http://www.oneonta.ny.us/departments/personnel', (42.453492, -75.0629531)],
['Onondaga County', 'http://www.ongov.net/employment/civilService.html', 'http://www.ongov.net/employment/jobs/', (43.0481221, -76.1474244)],
['Ontario County', 'http://www.co.ontario.ny.us/jobs.aspx', 'http://www.co.ontario.ny.us/jobs.aspx', (42.8844625, -77.278399)],
['Orange County', 'https://www.orangecountygov.com/1137/Human-Resources', 'https://www.orangecountygov.com/1137/Human-Resources', (41.4020382, -74.3243191)],
['Orangetown Town', 'https://www.orangetown.com/groups/department/personnel/', 'https://www.orangetown.com/groups/department/personnel/', (41.0465776, -73.9496707)],
['Orleans County', 'http://www.orleansny.com/Departments/Operations/Personnel.aspx', 'http://www.orleansny.com/personnel', (43.246488, -78.193516)],
['Ossining Town', 'http://www.townofossining.com/cms/resources/human-resources', 'https://www.townofossining.com/cms/resources/human-resources', (41.1613168, -73.8620367)],
['Ossining Village', 'http://www.villageofossining.org/personnel-department', 'https://www.villageofossining.org/personnel-department', (41.1613168, -73.8620367)],
['Oswego City', 'http://www.oswegony.org/government/personnel', 'http://www.oswegony.org/government/personnel', (43.4547284, -76.5095967)],
['Oswego County', 'http://oswegocounty.com/humanresources.shtml', 'http://oswegocounty.com/humanresources/openings.php', (43.4547284, -76.5095967)],
['Otsego County', 'http://www.otsegocounty.com/depts/per/', 'http://www.otsegocounty.com/depts/per/', (42.7006303, -74.924321)],
['Oyster Bay Town', 'http://oysterbaytown.com/departments/human-resources/', 'http://oysterbaytown.com/departments/human-resources/', (40.6806564, -73.4742914)],
['Peekskill City', 'http://www.cityofpeekskill.com/human-resources/pages/about-human-resources', 'https://www.cityofpeekskill.com/human-resources/pages/about-human-resources', (41.289811, -73.9204922)],
['Penfield Town', 'http://www.penfield.org/Human_Resources.php', 'http://www.penfield.org', (43.1301133, -77.4759588)],
['Perinton Town', 'http://www.perinton.org/Departments/finpers/', 'http://www.perinton.org/departments/finpers', (43.0993, -77.443014)],
['Pittsford Town', 'http://www.townofpittsford.org/home-hr?_sm_au_=iVV8Z8Lp1WfFsNV6', 'http://www.townofpittsford.org/home-hr?_sm_au_=ivv8z8lp1wffsnv6', (43.090959, -77.515298)],
['Port Chester Village', '_DUP._http://humanresources.westchestergov.com/job-seekers/civil-service-exams', 'http://humanresources.westchestergov.com/job-seekers/civil-service-exams', (41.0339862, -73.7629097)],
['Poughkeepsie City', 'http://cityofpoughkeepsie.com/personnel/', 'http://cityofpoughkeepsie.com/personnel/', (41.7065779, -73.9284101)],
['Poughkeepsie Town', 'http://www.townofpoughkeepsie.com/human_resources/index.html?_sm_au_=iVV8Z8Lp1WfFsNV6', 'http://www.townofpoughkeepsie.com/human_resources/index.html?_sm_au_=ivv8z8lp1wffsnv6', (41.7065779, -73.9284101)],
['Putnam County', 'http://www.putnamcountyny.com/personneldept/', 'https://www.putnamcountyny.com/personneldept/exam-postings/', (41.4266361, -73.6788272)],
['Queens County', '_DUP._http://www1.nyc.gov/jobs/index.page', 'https://www1.nyc.gov/jobs', (40.7308619, -73.9871558)],
['Ramapo Town', 'http://www.ramapo.org/page/personnel-30.html?_sm_au_=iVVt78QZ5W7P2qHF', 'http://www.ramapo.org/page/personnel-30.html?_sm_au_=ivvt78qz5w7p2qhf', (41.1151372, -74.1493948)],
['Rensselaer County', 'http://www.rensco.com/county-job-assistance', 'http://www.rensco.com/county-job-assistance/', (42.7284117, -73.6917878)],
['Richmond County', '_DUP._http://www1.nyc.gov/jobs/index.page', 'https://www1.nyc.gov/jobs', (40.7308619, -73.9871558)],
['Riverhead Town', 'http://www.townofriverheadny.gov/pview.aspx?id=2481&catID=118&_sm_au_=iVVt78QZ5W7P2qHF', 'https://www.townofriverheadny.gov/pview.aspx?id=2481&amp;catid=118&amp;_sm_au_=ivvt78qz5w7p2qhf', (40.9170435, -72.6620402)],
['Rochester City', 'http://www.cityofrochester.gov/article.aspx?id=8589936759', 'https://www.cityofrochester.gov/article.aspx?id=8589936759', (43.157285, -77.615214)],
['Rockland County', 'https://mycivilservice.rocklandgov.com', 'http://rocklandgov.com/departments/personnel/civil-service-examinations', (41.1469917, -73.9902998)],
['Rockville Centre Village', 'http://www.rvcny.us/jobs.html?_sm_au_=iVV8Z8Lp1WfFsNV6', 'http://www.rvcny.us/jobs.html?_sm_au_=ivv8z8lp1wffsnv6', (40.6574186, -73.6450664)],
['Rome City', 'https://romenewyork.com/civil-service/', 'https://romenewyork.com/civil-service/', (43.2128473, -75.4557304)],
['Rotterdam Town', 'http://www.schenectadycounty.com/FullStory.aspx?m=36&amid=373', 'https://www.schenectadycounty.com/', (42.8143922952735, -73.9420906329747)],
['Rye City', 'http://www.ryeny.gov/human-resources.cfm', 'https://www.ryeny.gov/', (40.9808209, -73.684294)],
['Saratoga County', 'http://www.saratogacountyny.gov/departments/personnel/', 'https://www.saratogacountyny.gov/departments/personnel/', (43.0009087, -73.8490111)],
['Saratoga Springs City', 'http://www.saratoga-springs.org/Jobs.aspx', 'http://www.saratoga-springs.org/jobs.aspx', (43.0821793, -73.7853915)],
['Schenectady City', 'http://www.cityofschenectady.com/208/Human-Resources', 'http://www.cityofschenectady.com/208/Human-Resources', (42.8143922952735, -73.9420906329747)],
['Schenectady County', 'https://mycivilservice.schenectadycounty.com', 'https://www.schenectadycounty.com/', (42.8143922952735, -73.9420906329747)],
['Schoharie County', 'https://www4.schohariecounty-ny.gov/', 'https://www4.schohariecounty-ny.gov/', (42.5757217, -74.4390277)],
['Schuyler County', 'http://www.schuylercounty.us/Index.aspx?NID=119', 'http://www.schuylercounty.us/119/Civil-Service', (42.3810555, -76.8705777)],
['Seneca County', 'https://seneca-portal.mycivilservice.com/', 'https://seneca-portal.mycivilservice.com', (42.9047884, -76.8627368)],
['Smithtown Town', 'http://www.smithtownny.gov/jobs.aspx?_sm_au_=iVVt78QZ5W7P2qHF', 'http://www.smithtownny.gov/jobs.aspx?_sm_au_=ivvt78qz5w7p2qhf', (40.8559314, -73.2006687)],
['Southampton Town', 'http://www.southamptontownny.gov/jobs.aspx', 'http://www.southamptontownny.gov/jobs.aspx', (40.884267, -72.3895296)],
['Spring Valley Village', 'http://rocklandgov.com/departments/personnel/civil-service-examinations/', 'http://rocklandgov.com/departments/personnel/civil-service-examinations', (41.1469917, -73.9902998)],
['St Lawrence County', 'https://www.stlawco.org/departments/humanresources/examinationschedule', 'https://www.stlawco.org/departments/humanresources/examinationschedule', (44.5956163, -75.1690942)],
['Steuben County', 'http://www.steubencony.org/Pages.asp?PGID=32', 'https://www.steubencony.org/pages.asp?pgid=32', (42.3370164, -77.3177577)],
['Suffolk County', 'http://www.suffolkcountyny.gov/departments/civilservice.aspx', 'https://www.suffolkcountyny.gov/Departments/Civil-Service', (40.8256537, -73.2026138)],
['Sullivan County', 'http://sullivanny.us/index.php/Departments/Personnel', 'http://sullivanny.us/index.php/Departments/Personnel', (41.6556465, -74.6893282)],
['Syracuse City', '_DUP._http://www.ongov.net/employment/jurisdiction.html', 'http://www.ongov.net/employment/jobs/', (43.0481221, -76.1474244)],
['Tioga County', 'http://www.tiogacountyny.com/departments/personnel-civil-service/', 'http://www.tiogacountyny.com/departments/personnel-civil-service', (42.1034075, -76.2621549)],
['Tompkins County', 'http://tompkinscountyny.gov/personnel', 'http://tompkinscountyny.gov/personnel', (42.4396039, -76.4968019)],
['Tonawanda City', 'http://www.tonawandacity.com/residents/civil_service.php#.WanWSrKGMnR', 'https://www.tonawandacity.com/residents/civil_service.php', (42.991733, -78.8824886119079)],
['Troy City', 'http://www.troyny.gov/departments/personnel-department/', 'http://www.troyny.gov/departments/personnel-department/', (42.7284117, -73.6917878)],
['Ulster County', 'https://ulstercountyny.gov/personnel/index.html', 'https://ulstercountyny.gov/personnel/index.html', (41.9287812, -74.0023702)],
['Union Town', 'http://www.townofunion.com/depts_services_human_full.html', 'https://www.townofunion.com/', (42.1128526, -76.021034)],
['Utica City', 'http://www.cityofutica.com/departments/civil-service/index', 'http://www.cityofutica.com/departments/civil-service/index', (43.1009031, -75.2326641)],
['Valley Stream Village', 'http://www.vsvny.org/index.asp?Type=B_JOB&SEC=%7b05C716C7-40EE-49EE-B5EE-14EFA9074AB9%7d&_sm_au_=iVV8Z8Lp1WfFsNV6', 'https://www.vsvny.org/index.asp?type=b_job&amp;sec=%7b05c716c7-40ee-49ee-b5ee-14efa9074ab9%7d&amp;_sm_au_=ivv8z8lp1wffsnv6', (40.6715969, -73.6982991)],
['Vestal Town', 'http://www.vestalny.com/departments/human_resources/job_opportunities.php', 'https://www.vestalny.com/departments/human_resources/job_opportunities.php', (42.0850747, -76.053813)],
['Wallkill Town', 'http://www.townofwallkill.com/index.php/departments/human-resources', 'https://www.townofwallkill.com/index.php/departments/human-resources', (41.44591415, -74.4224417389405)],
['Wappinger Town', 'http://www.co.dutchess.ny.us/CivilServiceInformationSystem/ApplicantWeb/frmAnnouncementList.aspx?aspxerrorpath=/CivilServiceInformationSystem/ApplicantWeb/frmUserLogin.aspx', 'http://www.co.dutchess.ny.us/civilserviceinformationsystem/applicantweb/frmannouncementlist.aspx?aspxerrorpath=/civilserviceinformationsystem/applicantweb/frmuserlogin', (41.7065779, -73.9284101)],
['Warren County', 'http://www.warrencountyny.gov/civilservice/exams.php', 'http://www.warrencountyny.gov/civilservice/exams.php', (43.425996, -73.712425)],
['Washington County', 'http://www.washingtoncountyny.gov/jobs.aspx', 'http://www.washingtoncountyny.gov/jobs.aspx', (43.267206, -73.584709)],
['Watertown City', 'https://www.watertown-ny.gov/index.asp?nid=791', 'https://www.watertown-ny.gov/index.asp?nid=791', (43.9747838, -75.9107565)],
['Watervliet City', 'http://watervliet.com/city/civil-service.htm', 'http://watervliet.com/city/civil-service.htm', (42.7282483, -73.7014649039252)],
['Wayne County', 'http://web.co.wayne.ny.us/human-resources/', 'https://web.co.wayne.ny.us/', (43.0642305, -76.9902456)],
['Webster Town', 'http://www.ci.webster.ny.us/index.aspx?NID=85&_sm_au_=iVV8Z8Lp1WfFsNV6', 'http://www.ci.webster.ny.us/85/Human-Resources', (43.263428, -77.4334757)],
['Westchester County', 'http://humanresources.westchestergov.com/job-seekers/civil-service-exams', 'http://humanresources.westchestergov.com/job-seekers/civil-service-exams', (41.0339862, -73.7629097)],
['White Plains City', 'https://www.cityofwhiteplains.com/98/Personnel', 'https://www.cityofwhiteplains.com/98/Personnel', (41.0335885, -73.7639768)],
['Wyoming County', 'http://www.wyomingco.net/164/Civil-Service', 'http://www.wyomingco.net/164/Civil-Service', (42.74271215, -78.1326011420972)],
['Yates County', 'http://www.yatescounty.org/203/Personnel', 'https://www.yatescounty.org/203/Personnel', (42.6609248, -77.0563316)],
['Yonkers City', 'http://www.yonkersny.gov/work/jobs-civil-service-exams', 'https://www.yonkersny.gov/work/jobs-civil-service-exams', (40.9312099, -73.8987469)],
['Yorktown Town', 'http://www.yorktownny.org/jobs', 'https://www.yorktownny.org/jobs', (41.2709274, -73.7776336)]
]


fin = []


# Get coordinates from the list
for i in the_list:

    workin = []

    coords = i[3]


    # Get street address from geopy
    location = geolocator.reverse(coords)

    print(i[0], '\nloc:', location)


    workin.append(i[0])
    workin.append(i[1])
    workin.append(i[2])
    workin.append(location.address)
    workin.append(i[3])

    fin.append(workin)



    for i in fin:
        print(i, '\n')





















