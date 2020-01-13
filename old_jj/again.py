# Desc: Add employ urls to grudb


# To do:
# resolve multi matches
# mark unused
# multi periods in em


grudb_list = (
['Adelphi University', 'http://www.adelphi.edu', 'South Avenue Garden City, 11530', 'South Avenue, Garden City, Nassau County, New York, 11530-2714, USA', (40.7227802, -73.6527077)],
['Albany College of Pharmacy and Health Sciences', 'http://www.acphs.edu', '106 New Scotland Avenue Albany, 12208', 'Albany College of Pharmacy and Health Sciences, 106, New Scotland Avenue, New Scotland, Albany, Albany County, New York, 12208, USA', (42.65202585, -73.7786121914516)],
['Albany Law School', 'http://www.albanylaw.edu', '80 New Scotland Avenue Albany, 12208', 'Albany Law School, 80, New Scotland Avenue, New Scotland, Albany, Albany County, New York, 12208, USA', (42.6515463, -73.7774615919355)],
['Albany Medical College', 'http://www.amc.edu', '47 New Scotland Avenue Albany, 12208', '47, New Scotland Avenue, New Scotland, Albany, Albany County, New York, 12208, USA', (42.6526091030803, -73.7753504097573)],
['Alfred State College', 'http://www.alfredstate.edu', '10 Upper College Drive Alfred, 14802', '10, Upper College Drive, Alfred, Allegany County, New York, 14802, USA', (42.2559440282857, -77.7969351714444)],
['Alfred University', 'http://www.alfred.edu', 'One Saxon Drive Alfred, 14802', 'Saxon Drive, Alfred, Allegany County, New York, 14802, USA', (42.253918, -77.789498)],
['Bank Street College of Education', 'http://www.bankstreet.edu', '610 W 112 Street New York City, 10025', 'Manhattan Valley, NYC, New York, 10025, USA', (40.7977716640378, -73.9675799276821)],
['Bard College', 'http://www.bard.edu', 'Annandale Road Annandale-on-Hudson, 12504', 'Annandale Road, Annandale-on-Hudson, Town of Red Hook, Dutchess County, New York, 12504, USA', (42.0202254, -73.9089157)],
['Barnard College', 'http://barnard.edu', '3009 Broadway New York City, 10027', 'Harlem, NYC, New York, 10027, USA', (40.8103796036449, -73.9502987225818)],
['Baruch College, CUNY', 'http://www.baruch.cuny.edu', 'One Bernard Baruch Way New York City, 10010', 'Flatiron District, NYC, New York, 10010, USA', (40.739849042848, -73.9852690710667)],
['Berkeley College', 'http://berkeleycollege.edu', '3 East 43 Street New York City, 10017', 'Chelsea, NYC, New York, 10017, USA', (40.7509542406791, -73.993986225138)],
['Binghamton University, State University of New York', 'http://www.binghamton.edu', '4400 Vestal Parkway East Vestal, 13850', '4400, Vestal Parkway East, Old Dickinson, Willow Point, Vestal Town, Broome County, New York, 13850, USA', (42.0954891601704, -75.9638121950971)],
['Boricua College', 'http://www.boricuacollege.edu', '3755 Broadway New York City, 10032', 'Boricua College, 3755, Broadway, Washington Heights, Manhattan, Manhattan Community Board 12, New York County, NYC, New York, 10032, USA', (40.8333333, -73.9461111)],
['Briarcliffe College', 'http://www.briarcliffe.edu', '1055 Stewart Avenue Bethpage, 11714', '1055, Stewart Avenue, Bethpage, Nassau County, New York, 11714, USA', (40.75955975, -73.4901828990603)],
['Brooklyn College', 'http://www.brooklyn.cuny.edu', '2900 Bedford Avenue Brooklyn, 11210', 'James Hall, 2900, Bedford Avenue, Midwood, BK, Kings County, NYC, New York, 11210, USA', (40.63175995, -73.9534812161228)],
['Brooklyn Law School', 'http://www.brooklaw.edu', '250 Joralemon Street Brooklyn, 11201', 'Brooklyn Law School Annex, 250, Joralemon Street, Downtown Brooklyn, Kings County, NYC, New York, 11201, USA', (40.6919444, -73.9897222)],
['Bryant and Stratton College', 'http://www.bryantstratton.edu', '465 Main Street Buffalo, 14203', 'Buffalo, New York, 14203, USA', (42.8851541102104, -78.8698782031996)],
['Buffalo State College', 'http://www.buffalostate.edu', '1300 Elmwood Avenue Buffalo, 14222', 'Burchfield Penney Art Center, 1300, Elmwood Avenue, Elmwood Village, Buffalo, Erie County, New York, 14222, USA', (42.93141, -78.8779732376238)],
['CUNY School of Law', 'http://www.law.cuny.edu', '2 Court Square Long Island City, 11101', '2, Court Square, LIC, Queens County, NYC, New York, 11101, USA', (40.746246, -73.942895)],
['Canisius College', 'http://www.canisius.edu', '2001 Main Street Buffalo, 14208', 'Buffalo, New York, 14208, USA', (42.9142636868314, -78.8494141593693)],
['Cazenovia College', 'http://www.cazenovia.edu', '22 Sullivan Street Cazenovia, 13035', 'Joy Hall, 22, Sullivan Street, Cazenovia, Town of Cazenovia, Madison County, New York, 13035, USA', (42.9324896, -75.8548604603835)],
['Clarkson University', 'http://www.clarkson.edu', '8 Clarkson Avenue Potsdam, 13699', 'Potsdam, New York, 13699, USA', (44.6610538, -74.997073025)],
['Colgate University', 'http://www.colgate.edu', '13 Oak Drive Hamilton, 13346', '13, Oak Drive, Hamilton, Town of Hamilton, Madison County, New York, 13346, USA', (42.8193216656923, -75.5329017844357)],
['College of Mount Saint Vincent', 'http://mountsaintvincent.edu', '6301 Riverdale Avenue The Bronx, 10471', 'College of Mount Saint Vincent, 6301, Riverdale Avenue, Riverdale, Bronx County, NYC, New York, 10471, USA', (40.9128739, -73.9068178375009)],
['College of Staten Island', 'http://www.csi.cuny.edu', '2800 Victory Boulevard Staten Island, 10314', 'Victory Boulevard, Bulls Head, Staten Island, Todt Hill, Richmond County, NYC, New York, 10314, USA', (40.6088504, -74.1533966)],
['Columbia University in the City of New York', 'http://www.columbia.edu', 'West 116 Street and Broadway New York City, 10027', 'Harlem, NYC, New York, 10027, USA', (40.8103796036449, -73.9502987225818)],
['Concordia College-New York', 'http://www.concordia-ny.edu', '171 White Plains Road Bronxville, 10708', 'Brunn-Maier Hall, 171, White Plains Road, Bronxville, Town of Eastchester, Westchester County, New York, 10708, USA', (40.9424123, -73.8221066892536)],
['Cornell University', 'http://www.cornell.edu', '300 Day Hall Ithaca, 14853', 'Day Hall, 144, East Avenue, Ithaca, Ithaca Town, Tompkins County, New York, 14853, USA', (42.4471768, -76.4835569975977)],
["D'Youville College", 'http://www.dyc.edu', '320 Porter Avenue Buffalo, 14201', '320, Porter Avenue, Buffalo, Erie County, New York, 14201, USA', (42.9022105454416, -78.8905680902405)],
['Daemen College', 'http://www.daemen.edu', '4380 Main Street Amherst, 14226', '4380, Main Street, University Heights, Buffalo, Amherst Town, Erie County, New York, 14226, USA', (42.96377775, -78.788181)],
['Davis College', 'http://www.davisny.edu', '400 Riverside Drive Johnson City, 13790', 'Alice E. Chatlos Library, 400, Riverside Drive, Johnson City, Union Town, Broome County, New York, 13790, USA', (42.10155625, -75.9617987989404)],
['Dominican College', 'http://www.dc.edu', '470 Western Highway Orangeburg, 10962', 'Western Highway, Tappan, Town of Orangetown, Rockland County, New York, 10962, USA', (41.0437293, -73.9496621)],
['Elmira College', 'http://www.elmira.edu', 'One Park Place Elmira, 14901', 'Park Place, Elmira, Chemung County, New York, 14901, USA', (42.095617, -76.812484)],
['Farmingdale State College', 'http://www.farmingdale.edu', '2350 Broadhollow Road Farmingdale, 11735', 'Farmingdale, Nassau County, New York, 11735, USA', (40.7328811, -73.4458564)],
['Fashion Institute of Technology', 'http://www.fitnyc.edu', '227 W 27Th Street New York City, 10001', '227, West 27th Street, Chelsea, Manhattan, Manhattan Community Board 4, New York County, NYC, New York, 10001, USA', (40.7469086530612, -73.994274755102)],
['Five Towns College', 'http://www.ftc.edu', '305 N Service Road Dix Hills, 11746', 'South Huntington, New York, 11746, USA', (40.823178981743, -73.3744034833667)],
['Fordham University', 'http://www.fordham.edu', '441 E Fordham Road The Bronx, 10458', 'Duane Hall, 441, East Fordham Road, Belmont, The Bronx, Bronx County, NYC, New York, 10458, USA', (40.86126405, -73.8874163768828)],
['Hamilton College', 'http://www.hamilton.edu', '198 College Hill Road Clinton, 13323', 'Town of Kirkland, New York, 13323, USA', (43.0576507359389, -75.3748663697885)],
['Hartwick College', 'http://www.hartwick.edu', 'One Hartwick Drive Oneonta, 13820', 'Hartwick Drive, City of Oneonta, Otsego County, New York, 13820, USA', (42.460163, -75.071748)],
['Helene Fuld College of Nursing', 'http://www.helenefuld.edu', '24 East 120th Street New York City, 10035', '24, East 120th Street, East Harlem, Manhattan, Manhattan Community Board 11, New York County, NYC, New York, 10035, USA', (40.8028225, -73.943848)],
['Hilbert College', 'http://www.hilbert.edu', '5200 S Park Avenue Hamburg, 14075', 'South Park Avenue, Hamburg, Erie County, New York, 14075, USA', (42.7385951, -78.8252006)],
['Hobart and William Smith Colleges', 'http://www.hws.edu', '337 Pulteney Street Geneva, 14456', '337, Pulteney Street, Geneva, Geneva Town, Ontario County, New York, 14456, USA', (42.857276393126, -76.9842832910369)],
['Hofstra University', 'http://www.hofstra.edu', '100 Hofstra University Hempstead, 11549', 'Hofstra University, Hempstead Turnpike Bike Path, East Garden City, Nassau County, New York, 11549, USA', (40.71703345, -73.599835005538)],
['Houghton College', 'http://www.houghton.edu', '1 Willard Avenue Houghton, 14744', '1, Willard Avenue, Houghton, Allegany County, New York, 14744, USA', (42.425714, -78.157313)],
['Hunter College, CUNY', 'http://www.hunter.cuny.edu', '695 Park Avenue New York City, 10065', 'Lenox Hill, NYC, New York, 10065, USA', (40.7660774848763, -73.9646222775575)],
['Icahn School of Medicine at Mount Sinai', 'http://www.mssm.edu', '1 Gustave L Levy Place New York City, 10029', 'East Harlem, NYC, New York, 10029, USA', (40.7920399140364, -73.9444226023398)],
['Iona College', 'http://www.iona.edu', '715 North Avenue New Rochelle, 10801', '715, North Avenue, New Rochelle, Westchester County, New York, 10801, USA', (40.9273324545454, -73.7894121666667)],
['Ithaca College', 'http://www.ithaca.edu', '953 Danby Road Ithaca, 14850', 'Ithaca, New York, 14850, USA', (42.4477576428231, -76.4907059862174)],
['Jamestown Business College', 'http://www.jbc.edu', '7 Fairmount Avenue Jamestown, 14701', '7, Fairmount Avenue, Jamestown, Chautauqua County, New York, 14701, USA', (42.0959778, -79.25010365)],
['John Jay College of Criminal Justice', 'http://www.jjay.cuny.edu', '524 W 59th Street New York City, 10019', "New Building, 524, West 59th Street, 1 West End Ave trade area, Hell's Kitchen, Manhattan, Manhattan Community Board 4, New York County, NYC, New York, 10019, USA", (40.7708819, -73.9897054845526)],
['Keuka College', 'http://www.keuka.edu', '141 Central Avenue Keuka Park, 14478', '141, Central Avenue, Keuka Park, Jerusalem Town, Yates County, New York, 14478, USA', (42.6158879739391, -77.0920147877885)],
['LIM College', 'http://www.limcollege.edu', '12 E 53Rd Street New York City, 10022', 'Midtown East, NYC, New York, 10022, USA', (40.7582601391897, -73.9678682034241)],
['Le Moyne College', 'http://www.lemoyne.edu', '1419 Salt Springs Road Syracuse, 13214', 'Le Moyne College, 1419, Salt Springs Road, Meadowbrook, Syracuse, Onondaga County, New York, 13214, USA', (43.0481774, -76.0857404821197)],
['Lehman College, CUNY', 'http://www.lehman.edu', '250 Bedford Park Boulevard W The Bronx, 10468', 'Lehman College of the City University of New York, 250, Bedford Park Boulevard West, Bedford Park, The Bronx, Bronx County, NYC, New York, 10468, USA', (40.8722825, -73.8948917141949)],
['Long Island University', 'http://www.liu.edu', '1 University Plaza Brooklyn, 11201', 'Kings County, NYC, New York, 11201, USA', (40.6913570473619, -73.995074571537)],
['Manhattan College', 'http://manhattan.edu', '4513 Manhattan College Parkway Riverdale, 10471', 'Bronx County, NYC, New York, 10471, USA', (40.9024688832858, -73.90297950271)],
['Manhattan School of Music', 'http://www.msmnyc.edu', '120 Claremont Avenue New York City, 10027', '120, Claremont Avenue, Morningside Heights, Manhattan, Manhattan Community Board 9, New York County, NYC, New York, 10027, USA', (40.8124973, -73.9617409)],
['Manhattanville College', 'http://www.mville.edu', '2900 Purchase Street Purchase, 10577', 'Manhattanville College, 2900, Purchase Street, Harrison, Town of Harrison, Westchester County, New York, 10577, USA', (41.0313935, -73.7155858)],
['Maria College', 'http://mariacollege.edu', '700 New Scotland Avenue Albany, 12208', '700, New Scotland Avenue, New Scotland, Albany, Albany County, New York, 12208, USA', (42.6570284, -73.8071058)],
['Marist College', 'http://www.marist.edu', '3399 North Road Poughkeepsie, 12601', '3399, North Road, Fairview, Town of Poughkeepsie, Dutchess County, New York, 12601, USA', (41.726896, -73.932586)],
['Marymount Manhattan College', 'http://www.mmm.edu', '221 E 71st Street New York City, 10021', 'Marymount Manhattan College, 221, East 71st Street, Lenox Hill, Manhattan, Manhattan Community Board 8, New York County, NYC, New York, 10021, USA', (40.7687028, -73.9597556)],
['Medaille College', 'http://www.medaille.edu', '18 Agassiz Circle Buffalo, 14214', 'Medaille College, 18, Agassiz Circle, Parkside, Buffalo, Erie County, New York, 14214, USA', (42.92864775, -78.8548887220501)],
['Medgar Evers College', 'http://www.mec.cuny.edu', '1650 Bedford Avenue Brooklyn, 11225', 'City University of New York Medgar Evers College, 1650, Bedford Avenue, Flatbush, BK, Kings County, NYC, New York, 11225, USA', (40.6662941, -73.9583633138472)],
['Mercy College', 'http://www.mercy.edu', '555 Broadway Dobbs Ferry, 10522', '555, Broadway, Dobbs Ferry, Town of Greenburgh, Westchester County, New York, 10522, USA', (41.0193732682769, -73.8697504826762)],
['Metropolitan College of New York', 'http://www.mcny.edu', '431 Canal Street New York City, 10013', '431, Canal Street, Hudson Square, Manhattan, Manhattan Community Board 2, New York County, NYC, New York, 10013, USA', (40.7232317, -74.0069711)],
['Molloy College', 'http://www.molloy.edu', '1000 Hempstead Avenue Rockville Centre, 11571', 'Rockville Centre, New York, 11571, USA', (40.6856209060791, -73.6253020149747)],
['Monroe College', 'http://www.monroecollege.edu', '2501 Jerome Avenue Bronx, 10468', '2501, Jerome Avenue, Fordham, The Bronx, Bronx County, NYC, New York, 10468, USA', (40.864011, -73.9003313)],
['Morrisville State College', 'http://www.morrisville.edu', '80 Eaton Street Morrisville, 13408', '80, Eaton Street, Morrisville, Town of Eaton, Madison County, New York, 13408, USA', (42.8955695, -75.645431)],
['Mount Saint Mary College', 'http://www.msmc.edu', '330 Powell Avenue Newburgh, 12550', '330, Powell Avenue, Newburgh, Orange County, New York, 12550, USA', (41.514232, -74.014609)],
['Nazareth College', 'http://www.naz.edu', '4245 East Avenue Rochester, 14618', '4245, East Avenue, Pittsford Town, Monroe County, New York, 14618, USA', (43.1026223061224, -77.5146466938776)],
['New York Academy of Art', 'http://nyaa.edu', '111 Franklin Street New York City, 10013', 'TriBeCa, NYC, New York, 10013, USA', (40.7192292699307, -74.0028507187478)],
['New York City College of Technology, CUNY', 'http://www.citytech.cuny.edu', '300 Jay Street Brooklyn, 11201', '300, Jay Street, Downtown Brooklyn, Kings County, NYC, New York, 11201, USA', (40.6952788, -73.9873073)],
['New York College of Podiatric Medicine', 'http://www.nycpm.edu', '53 E 124 Street New York City, 10035', 'East Harlem, NYC, New York, 10035, USA', (40.7970825176789, -73.9396480796993)],
['New York Institute of Technology', 'http://www.nyit.edu', 'Northern Boulevard Old Westbury, 11568', 'Old Westbury, Nassau County, New York, 11568, USA', (40.7887113, -73.5995717)],
['New York Law School', 'http://www.nyls.edu', '185 West Broadway New York City, 10013', '185, West Broadway, TriBeCa, Manhattan, Manhattan Community Board 1, New York County, NYC, New York, 10013, USA', (40.7180696, -74.0070841)],
['New York Medical College', 'http://www.nymc.edu', 'Administration Building Valhalla, 10595', 'Town of Mount Pleasant, New York, 10595, USA', (41.0858360269658, -73.776427931425)],
['New York School of Interior Design', 'http://www.nysid.edu', '170 East 70Th Street New York City, 10021', 'New York School of Interior Design, 170, East 70th Street, Lenox Hill, Manhattan, Manhattan Community Board 8, New York County, NYC, New York, 10021, USA', (40.7685442, -73.9624782559877)],
['New York University', 'http://www.nyu.edu', '70 Washington Square South New York City, 10012', 'Elmer Holmes Bobst Library, 70, Washington Square South, Washington Square Village, Greenwich Village, Manhattan, Manhattan Community Board 2, New York County, NYC, New York, 10012, USA', (40.72942865, -73.9972178045625)],
['Niagara University', 'http://www.niagara.edu', '5795 Lewiston Road Niagara University, 14109', 'Niagara University, Campus Drive, Lewiston Heights, Lewiston Town, Niagara County, New York, 14305, USA', (43.13755555, -79.0375125585894)],
['Nyack College', 'http://www.nyack.edu', '1 South Boulevard Nyack, 10960', '1, South Boulevard, South Nyack, Town of Orangetown, Rockland County, New York, 10960, USA', (41.086188, -73.928926)],
['Pace University', 'http://www.pace.edu', '1 Pace Plaza New York City, 10038', '1, Pace Plaza, Financial District, Manhattan, Manhattan Community Board 1, New York County, NYC, New York, 10038, USA', (40.7116674, -74.0054241)],
["Paul Smith's College", 'http://www.paulsmiths.edu', '7777 State Route 30 Paul Smiths, 12970', 'Paul Smiths, Franklin County, New York, 12970, USA', (44.4386659, -74.2526581)],
['Plaza College', 'http://www.plazacollege.edu', '118-33 Queens Boulevard, Forest Hills New York City, 11375', 'Forest Hills, 71st Avenue, Forest Hills Gardens, Queens County, NYC, New York, 11375, USA', (40.7195766, -73.8448686)],
['Pratt Institute', 'http://www.pratt.edu', '200 Willoughby Avenue Brooklyn, 11205', 'Pratt Institute, 200, Willoughby Avenue, Fort Greene, BK, Kings County, NYC, New York, 11205, USA', (40.69133825, -73.9630163297801)],
['Purchase College, State University of New York', 'http://www.purchase.edu', '735 Anderson Hill Road Purchase, 10577', 'Suny Purchase, 735, Anderson Hill Road, Harrison, Town of Harrison, Westchester County, New York, 10577, USA', (41.0476826, -73.7023562862641)],
['Queens College, City University of New York', 'http://www.qc.cuny.edu', '65-30 Kissena Boulevard Flushing, 11367', 'Queens County, NYC, New York, 11367, USA', (40.7287786775627, -73.821065519744)],
['Relay Graduate School of Education', 'http://relay.edu', '40 W 20th Street New York City, 10011', 'Andrew Heiskell Braille and Talking Book Library, 40, West 20th Street, Flatiron District, Manhattan, Manhattan Community Board 5, New York County, NYC, New York, 10011, USA', (40.7405048, -73.9933185)],
['Rensselaer Polytechnic Institute', 'http://www.rpi.edu', '110 8Th Street Troy, 12180', 'Rensselaer Polytechnic Institute, 110, 8th Street, Downtown, Troy, Rensselaer County, New York, 12180, USA', (42.7298459, -73.6795021620135)],
['Roberts Wesleyan College', 'http://www.roberts.edu', '2301 Westside Drive Rochester, 14624', 'Chili Town, New York, 14624, USA', (43.1190083011979, -77.7357149288694)],
['Rochester Institute of Technology', 'http://www.rit.edu', '1 Lomb Memorial Drive Rochester, 14623', 'Rochester Institute of Technology (RIT), 1, Lomb Memorial Drive, Bailey, Henrietta Town, Monroe County, New York, 14623, USA', (43.08250655, -77.6712166264273)],
['SUNY Canton', 'http://www.canton.edu', '34 Cornell Drive Canton, 13617', 'Southworth Library, 34, Cornell Drive, Canton, Saint Lawrence County, New York, 13617, USA', (44.60328055, -75.1834415989815)],
['SUNY Cobleskill', 'http://www.cobleskill.edu', 'State Route 7 Cobleskill, 12043', 'Cobleskill, Town of Cobleskill, Schoharie County, New York, 12043, USA', (42.677853, -74.4854172)],
['SUNY College at Old Westbury', 'http://www.oldwestbury.edu', '223 Store Hill Road Old Westbury, 11568', 'Campus Center, 223, Store Hill Road, Old Westbury, Nassau County, New York, 11568, USA', (40.79904665, -73.5734267419552)],
['SUNY College at Oneonta', 'http://www.oneonta.edu', 'Ravine Parkway Oneonta, 13820', 'Ravine Parkway, City of Oneonta, Otsego County, New York, 13820, USA', (42.463976, -75.070763)],
['SUNY College of Environmental Science and Forestry', 'http://www.esf.edu', '1 Forestry Drive Syracuse, 13210', 'State University of New York College of Environmental Science and Forestry, 1, Forestry Drive, University Hill, Syracuse, Onondaga County, New York, 13210, USA', (43.0347222, -76.1355556)],
['SUNY College of Optometry', 'http://www.sunyopt.edu', '33 West 42Nd Street New York City, 10036', '33, West 42nd Street, Times Square, Manhattan, Manhattan Community Board 5, New York County, NYC, New York, 10036, USA', (40.7540182244898, -73.9819396326531)],
['SUNY Cortland', 'http://www.cortland.edu', 'Miller Administration Building, Graham Avenue Cortland, 13045', 'Graham Avenue, Cortland, Cortlandville Town, Cortland County, New York, 13045, USA', (42.599024, -76.1872407)],
['SUNY Delhi', 'http://www.delhi.edu', '2 Main Street Delhi, 13753', '2, Main Street, Delhi, Town of Delhi, Delaware County, New York, 13753, USA', (42.273317, -74.921923)],
['SUNY Downstate Medical Center', 'http://www.downstate.edu', '450 Clarkson Avenue Brooklyn, 11203', '450, Clarkson Avenue, Brooklyn Community Board 17 Neighborhoods, BK, Kings County, NYC, New York, 11203, USA', (40.6553702, -73.9450773)],
['SUNY Empire State College', 'http://www.esc.edu', '1 Union Avenue Saratoga Springs, 12866', 'Union Avenue, City of Saratoga Springs, Saratoga County, New York, 12866, USA', (43.0721417, -73.7554765)],
['SUNY Geneseo', 'http://www.geneseo.edu', '1 College Circle Geneseo, 14454', 'State University of New York at Geneseo, 1, College Circle, Geneseo, Geneseo Town, Livingston County, New York, 14454, USA', (42.7965185, -77.8206437)],
['SUNY Maritime College', 'http://www.sunymaritime.edu', '6 Pennyfield Avenue Throggs Neck, 10465', 'Bronx County, NYC, New York, 10465, USA', (40.8264659866272, -73.8184536764782)],
['SUNY Polytechnic Institute', 'http://sunypoly.edu', '100 Seymour Road Utica, 13502', 'State University of New York Polytechnic Institute, 100, Seymour Road, Maynard, Town of Marcy, Oneida County, New York, 13502, USA', (43.13800205, -75.2294359077068)],
['SUNY Upstate Medical University', 'http://www.upstate.edu', '750 E Adams Street Syracuse, 13210', 'State University of New York Upstate Medical University, 750, East Adams Street, University Hill, Syracuse, Onondaga County, New York, 13210, USA', (43.0408333, -76.1391667)],
['Sarah Lawrence College', 'http://www.sarahlawrence.edu', 'One Meadway Bronxville, 10708', 'Bronxville, Town of Eastchester, Westchester County, New York, 10708, USA', (40.9381544, -73.8320784)],
['School of Visual Arts', 'http://www.sva.edu', '209 E 23Rd Street New York City, 10010', 'Flatiron District, NYC, New York, 10010, USA', (40.739849042848, -73.9852690710667)],
['Siena College', 'http://www.siena.edu', '515 Loudon Road Loudonville, 12211', 'Town of Colonie, New York, 12211, USA', (42.7064880684437, -73.7672226619966)],
['Skidmore College', 'http://www.skidmore.edu', '815 N Broadway Saratoga Springs, 12866', '815, North Broadway, Town of Greenfield, Saratoga County, New York, 12866, USA', (43.0958988865961, -73.7796611680201)],
['St. Bonaventure University', 'http://www.sbu.edu', '3261 W. State Road St. Bonaventure, 14778', 'St. Bonaventure, Cattaraugus County, New York, 14778, USA', (42.0803426, -78.4750213)],
['St. Francis College', 'http://www.sfc.edu', '180 Remsen Street Brooklyn Heights, 11201', '180, Remsen Street, Brooklyn Heights, Kings County, NYC, New York, 11201, USA', (40.6932917, -73.9920629)],
['St. John Fisher College', 'http://www.sjfc.edu', '3690 East Avenue Rochester, 14618', 'St John Fisher College, 3690, East Avenue, Pittsford Town, Monroe County, New York, 14618, USA', (43.11502265, -77.5103989420753)],
["St. John's University", 'http://www.stjohns.edu', '8000 Utopia Parkway Queens, 11439', 'Queens County, NYC, New York, 11439, USA', (40.7808088523269, -73.7939922150785)],
["St. Joseph's College", 'http://www.sjcny.edu', '245 Clinton Avenue Brooklyn, 11772', 'East Patchogue, New York, 11772, USA', (40.7722813847329, -72.9979636078277)],
['St. Lawrence University', 'http://www.stlawu.edu', '23 Romoda Drive Canton, 13617', 'Abbott-Young Memorial Temple, 23, Romoda Drive, Canton, Saint Lawrence County, New York, 13617, USA', (44.5931412, -75.1626242)],
['St. Thomas Aquinas College', 'http://www.stac.edu', '125 Route 340 Sparkill, 10976', 'Sparkill, Town of Orangetown, Rockland County, New York, 10976, USA', (41.0289025, -73.9326580670926)],
['State University of New York College at Plattsburgh', 'http://www.plattsburgh.edu', '101 Broad Street Plattsburgh, 12901', 'Broad Street, Plattsburgh, Clinton County, New York, 12901, USA', (44.6949325, -73.4577396)],
['State University of New York at Fredonia', 'http://www.fredonia.edu', '280 Central Avenue Fredonia, 14063', 'Fredonia, New York, 14063, USA', (42.4361970749719, -79.3380339273106)],
['State University of New York at New Paltz', 'http://www.newpaltz.edu', '1 Hawk Drive New Paltz, 12561', 'Hawk Drive, New Paltz, Town of New Paltz, Ulster County, New York, 12561, USA', (41.7404585, -74.0809252)],
['State University of New York at Oswego', 'http://www.oswego.edu', '7060 State Route 104 Oswego, 13126', 'Oswego, New York, 13126, USA', (43.4448074212016, -76.4927360911854)],
['Stony Brook University', 'http://www.stonybrook.edu', '100 Nicolls Road Stony Brook, 11794', 'State University of New York at Stony Brook, 100, Nicolls Road, Stony Brook, Suffolk County, New York, 11794, USA', (40.9156246, -73.1245152)],
['Syracuse University', 'http://www.syracuse.edu', '900 South Crouse Avenue Syracuse, 13244', 'Syracuse, New York, 13244, USA', (43.0313169017541, -76.1326354053919)],
['The City College of New York', 'http://www.ccny.cuny.edu', '160 Convent Avenue New York City, 10031', 'CCNY, 160, Convent Avenue, Manhattanville, Manhattan, Manhattan Community Board 9, New York County, NYC, New York, 10031, USA', (40.81819805, -73.9510089793336)],
['The College at Brockport', 'http://www.brockport.edu', '350 New Campus Drive Brockport, 14420', 'The College at Brockport, 350, New Campus Drive, Brockport, Sweden Town, Monroe County, New York, 14420, USA', (43.209853, -77.9513586719191)],
['The College of New Rochelle', 'http://www.cnr.edu', '29 Castle Place New Rochelle, 10805', 'Castle Place, New Rochelle, Westchester County, New York, 10805, USA', (40.9010096, -73.781199)],
['The College of Saint Rose', 'http://www.strose.edu', '432 Western Avenue Albany, 12203', '432, Western Avenue, Beverwyck, Albany, Albany County, New York, 12203, USA', (42.664274, -73.785103)],
['The College of Westchester', 'http://www.cw.edu', '325 Central Avenue White Plains, 10606', 'White Plains, New York, 10606, USA', (41.0236715234752, -73.7768182287321)],
['The Cooper Union for the Advancement of Science and Art', 'http://cooper.edu', '7 East 7Th Street New York City, 10003', 'East Village, NYC, New York, 10003, USA', (40.7316479424559, -73.9885022928394)],
['The Culinary Institute of America', 'http://www.ciachef.edu', '1946 Campus Drive Hyde Park, 12538', 'Culinary Institute of America, 1946, Campus Dr, Hyde Park, Town of Hyde Park, Dutchess County, New York, 12538, USA', (41.7459268, -73.9331926)],
['The Graduate Center, CUNY', 'http://www.gc.cuny.edu', '365 Fifth Avenue New York City, 10016', 'Kips Bay, NYC, New York, 10016, USA', (40.7454191987458, -73.9797183037984)],
['The Juilliard School', 'http://www.juilliard.edu', '60 Lincoln Center Plaza New York City, 10023', 'Lincoln center, West 65th Street, Lincoln Square, Manhattan, Manhattan Community Board 7, New York County, NYC, New York, 10023, USA', (40.7735404, -73.9844356)],
["The King's College", 'http://www.tkc.edu', '56 Broadway New York City, 10004', "The King's College, 56, Broadway, Financial District, Manhattan, Manhattan Community Board 1, New York County, NYC, New York, 10004, USA", (40.7066535, -74.0123807)],
['The New School', 'http://www.newschool.edu', '66 W 12th Street New York City, 10011', 'The New School, 66, West 12th Street, Washington Square Village, Greenwich Village, Manhattan, Manhattan Community Board 2, New York County, NYC, New York, 10011, USA', (40.73547915, -73.9970708835668)],
['The Rockefeller University', 'http://www.rockefeller.edu', '1230 York Avenue New York City, 10065', 'Rockefeller University, 1230, York Avenue, Lenox Hill, Manhattan, Manhattan Community Board 8, New York County, NYC, New York, 10065, USA', (40.76243945, -73.9558065668409)],
['The Sage Colleges', 'http://www.sage.edu', '65 1st Street Troy, 12180', '1st Street, Downtown, Troy, Rensselaer County, New York, 12180, USA', (42.725762, -73.69406)],
['The State University of New York at Potsdam', 'http://www.potsdam.edu', '44 Pierrepont Avenue Potsdam, 13676', '44, Pierrepont Avenue, Potsdam, Saint Lawrence County, New York, 13676, USA', (44.662401, -74.977479)],
['Touro College', 'http://www.touro.edu', '500 7th Avenue New York City, 10018', 'FedEx Office Print & Ship Center, 500, 7th Avenue, Times Square, Garment District, Manhattan, Manhattan Community Board 5, New York County, NYC, New York, 10018, USA', (40.7530892, -73.9893535)],
['Trocaire College', 'http://trocaire.edu', '360 Choate Avenue Buffalo, 14220', 'Trocaire College, 360, Choate Avenue East, Buffalo, Erie County, New York, 14220, USA', (42.8467327, -78.8127639)],
['Union College', 'http://www.union.edu', '807 Union Street Schenectady, 12308', 'Payne Gate, 807, Union Street, Schenectady, Schenectady County, New York, 12308, USA', (42.8148056, -73.9316225)],
['United States Merchant Marine Academy', 'http://www.usmma.edu', '300 Steamboat Road Kings Point, 11024', '300, Steamboat Road, Great Neck, Nassau County, New York, 11024, USA', (40.812981, -73.760919)],
['United States Military Academy', 'http://www.usma.edu', '646 Swift Road West Point, 10996', 'US Military Academy - West Point, New York, 10996, USA', (41.3921174083589, -73.9694584746879)],
['University at Albany, State University of New York', 'http://www.albany.edu', '1400 Washington Avenue Albany, 12222', '1400, Washington Avenue, Albany, Albany County, New York, 12222, USA', (42.6917413284117, -73.8256615878134)],
['University at Buffalo, State University of New York', 'http://www.buffalo.edu', '12 Capen Hall Buffalo, 14260', 'Buffalo, Erie County, New York, USA', (42.8867166, -78.8783922)],
['University of Rochester', 'http://www.rochester.edu', '300 Wilson Boulevard Rochester, 14627', 'Rochester, New York, 14627, USA', (43.1214901146923, -77.6272321138567)],
['Utica College', 'http://www.utica.edu', '1600 Burrstone Road Utica, 13502', 'Utica College, 1600, Burrstone Road, City of Utica, Town of New Hartford, Oneida County, New York, 13502, USA', (43.09724785, -75.2704843627876)],
['Vassar College', 'http://www.vassar.edu', '124 Raymond Avenue Poughkeepsie, 12604', 'Vassar College, 124, Raymond Avenue, Arlington, Town of Poughkeepsie, Dutchess County, New York, 12604, USA', (41.686786, -73.8956971)],
['Vaughn College of Aeronautics and Technology', 'http://www.vaughn.edu', '86-01 23Rd Avenue Flushing, 11369', 'Queens County, NYC, New York, 11369, USA', (40.7625007662507, -73.8727926937193)],
['Villa Maria College', 'http://www.villa.edu', '240 Pine Ridge Road Buffalo, 14225', 'Cheektowaga, New York, 14225, USA', (42.9281194302114, -78.7627046330652)],
['Wagner College', 'http://wagner.edu', 'One Campus Road Staten Island, 10301', 'Richmond County, NYC, New York, 10301, USA', (40.6294973901304, -74.0938536788437)],
['Webb Institute', 'http://www.webb.edu', '298 Crescent Beach Road Glen Cove, 11542', '298, Crescent Beach Road, Glen Cove, Nassau County, New York, 11542, USA', (40.8831427462155, -73.6467904769636)],
['Wells College', 'http://www.wells.edu', '170 Main Street Aurora, 13026', 'Wells College, 170, Main Street, Aurora, Town of Ledyard, Cayuga County, New York, 13026, USA', (42.7438698, -76.6947011178555)],
['Yeshiva University', 'http://www.yu.edu', '500 W 185Th Street New York City, 10033', '500, West 185th Street, Fort George, Manhattan, Manhattan Community Board 12, New York County, NYC, New York, 10033, USA', (40.8506562, -73.9298679)],
['York College, City University of New York', 'http://www.york.cuny.edu', '94-20 Guy R. Brewer Boulevard Jamaica, 11451', 'Queens County, NYC, New York, 11451, USA', (40.7010339269506, -73.7985684864731)]
)






em_list = (
['http://careers.canisius.edu/cw/en-us/listing', 0, (42.8867166, -78.8783922)],
['http://careers.marist.edu/cw/en-us/listing', 0, (41.7065779, -73.9284101)],
['http://cooper.edu/work/employment-opportunities', 0, (40.7308619, -73.9871558)],
['http://einstein.yu.edu/administration/human-resources/career-opportunities.html', 0, (40.8511468, -73.8444737)],
['http://gts.edu/job-postings', 0, (40.7308619, -73.9871558)],
['http://huc.edu/about/employment-opportunities', 0, (40.7308619, -73.9871558)],
['http://humanresources.vassar.edu/jobs', 0, (41.7065779, -73.9284101)],
['http://inside.manhattan.edu/offices/human-resources/jobs.php', 0, (40.90056, -73.90639)],
['http://jobs.medaille.edu', 0, (42.8867166, -78.8783922)],
['http://jobs.union.edu/cw/en-us/listing', 0, (42.8142432, -73.9395687)],
['http://liu.edu/brooklyn.aspx', 0, (40.64530975, -73.9550230275334)],
['http://newschool.edu/public-engagement', 0, (40.7308619, -73.9871558)],
['http://niagaracc.suny.edu/careers/nccc-jobs.php', 0, (43.136723, -78.8847611)],
['http://sunysccc.edu/About-Us/Office-of-Human-Resources/Employment-Opportunities', 0, (42.8143922952735, -73.9420906329747)],
['http://utica.edu/hr/employment.cfm', 0, (43.1009031, -75.2326641)],
['http://www.bard.edu/employment/employment', 0, (42.2528649, -73.790959)],
['http://www.berkeleycollege.edu/index.htm', 0, (40.7308619, -73.9871558)],
['http://www.canton.edu/human_resources/job_opportunities.html', 0, (44.5956163, -75.1690942)],
['http://www.cazenovia.edu/campus-resources/human-resources/employment-opportunities', 0, (42.9300668, -75.8526915)],
['http://www.colgate.edu/working-at-colgate', 0, (42.8268798, -75.5444159)],
['http://www.college.columbia.edu', 0, (40.8088437, -73.9658566)],
['http://www.columbia.edu/cu/ssw', 0, (40.8088437, -73.9658566)],
['http://www.dental.columbia.edu', 0, (40.8088437, -73.9658566)],
['http://www.dyc.edu/about/administrative-offices/human-resources/career-opportunities.aspx', 0, (42.8867166, -78.8783922)],
['http://www.gs.columbia.edu', 0, (40.8088437, -73.9658566)],
['http://www.houghton.edu/campus/human-resources/employment', 0, (42.4233981, -78.1572319)],
['http://www.hunter.cuny.edu/hr/Employment', 0, (40.7308619, -73.9871558)],
['http://www.jtsa.edu/jobs-at-jts', 0, (40.8088437, -73.9658566)],
['http://www.law.columbia.edu', 0, (40.8088437, -73.9658566)],
['http://www.liu.edu/post', 0, (40.64530975, -73.9550230275334)],
['http://www.mcny.edu/index.php', 0, (40.7093848, -74.0147256)],
['http://www.monroecc.edu/employment', 0, (43.157285, -77.615214)],
['http://www.nccc.edu/careers-2', 0, (44.329497, -74.131279)],
['http://www.nycc.edu/employment-opportunities', 0, (42.910622, -76.7966215)],
['http://www.nyts.edu', 0, (40.8108175295545, -73.9637256464405)],
['http://www.nyu.edu/about/careers-at-nyu.html', 0, (40.7308619, -73.9871558)],
['http://www.paulsmiths.edu/humanresources/employment', 0, (44.4386659, -74.2526581)],
['http://www.potsdam.edu/crane', 0, (44.6752342, -74.9860333)],
['http://www.qcc.cuny.edu/employment/index.html', 0, (40.7684351, -73.7770774)],
['http://www.rit.edu/employment_rit.html', 0, (43.157285, -77.615214)],
['http://www.rochester.edu/working/hr/jobs', 0, (43.1551894, -77.6077078)],
['http://www.simon.rochester.edu/faculty-and-research/faculty-directory/faculty-recruitment/index.aspx', 0, (43.157285, -77.615214)],
['http://www.sunyacc.edu/job-listings', 0, (43.3772932, -73.6131714)],
['http://www.sunywcc.edu/about/jobshuman-resources', 0, (41.0748189, -73.7751326)],
['http://www.webb.edu/employment', 0, (40.882699, -73.644578)],
['http://www.youngwomenscollegeprep.org', 0, (43.1854754, -77.6106861508176)],
['http://www1.cuny.edu/sites/onboard/homepage/getting-started/campus/medgar-evers-college', 0, (40.7684351, -73.7770774)],
['http://www1.sunybroome.edu/about/employment', 0, (42.096968, -75.914341)],
['https://albany.interviewexchange.com/jobsrchresults.jsp', 0, (42.6511674, -73.754968)],
['https://alfredstate.interviewexchange.com/static/clients/481ASM1/index.jsp', 0, (42.2542366, -77.7905509)],
['https://apply.interfolio.com/14414/positions', 0, (40.64530975, -73.9550230275334)],
['https://careers-nyit.icims.com/jobs/search?ss=1', 0, (40.7887113, -73.5995717)],
['https://careers.barnard.edu', 0, (40.8088437, -73.9658566)],
['https://careers.columbia.edu', 0, (40.8088437, -73.9658566)],
['https://careers.columbia.edu/content/how-apply', 0, (40.8088437, -73.9658566)],
['https://careers.mountsinai.org/jobs?page=1', 0, (40.7796637, -73.9438435)],
['https://careers.newschool.edu', 0, (42.6511674, -73.754968)],
['https://careers.pace.edu/postings/search', 0, (40.7308619, -73.9871558)],
['https://careers.pageuppeople.com/876/cw/en-us/listing', 0, (40.7308619, -73.9871558)],
['https://careers.skidmore.edu/postings/search', 0, (43.0821793, -73.7853915)],
['https://clarkson.peopleadmin.com', 0, (44.6697996, -74.9813349)],
['https://clinton.interviewexchange.com/static/clients/552CCM1/index.jsp', 0, (44.69282, -73.45562)],
['https://cobleskill.interviewexchange.com/static/clients/474SCM1/index.jsp', 0, (42.677853, -74.4854172)],
['https://cshl.peopleadmin.com/postings/search', 0, (40.8714873, -73.456788)],
['https://cuny.jobs', 0, (40.7308619, -73.9871558)],
['https://daemen.applicantpro.com/jobs', 0, (42.9783924, -78.7997616)],
['https://employment.acphs.edu/postings/search', 0, (42.6511674, -73.754968)],
['https://employment.potsdam.edu/postings/search', 0, (44.6752342, -74.9860333)],
['https://employment.stlawu.edu/postings/search', 0, (44.5956163, -75.1690942)],
['https://farmingdale.interviewexchange.com/static/clients/383FAM1/index.jsp', 0, (40.7328811, -73.4458564)],
['https://fitnyc.interviewexchange.com/static/clients/391FIM1/index.jsp', 0, (40.7308619, -73.9871558)],
['https://fredonia.interviewexchange.com/static/clients/471SFM1/index.jsp', 0, (42.440058, -79.331711)],
['https://genesee.interviewexchange.com/static/clients/374GCM1/index.jsp', 0, (42.9980144, -78.1875515)],
['https://herkimer.interviewexchange.com/static/clients/505HCM1/index.jsp', 0, (43.0256259, -74.9859889)],
['https://hr.adelphi.edu/position-openings', 0, (40.72319685, -73.6403872966069)],
['https://hr.cornell.edu/jobs', 0, (42.4396039, -76.4968019)],
['https://hvcc.edu/hr/employment-opportunities.html', 0, (42.7284117, -73.6917878)],
['https://iona-openhire.silkroad.com/epostings/index.cfm?fuseaction=app.jobsearch', 0, (40.9665587, -73.7878852)],
['https://ithaca.peopleadmin.com', 0, (42.4396039, -76.4968019)],
['https://jobs.buffalostate.edu', 0, (42.9203639, -78.8770557)],
['https://jobs.cortland.edu', 0, (42.6011813, -76.1804843)],
['https://jobs.excelsior.edu', 0, (42.6511674, -73.754968)],
['https://jobs.geneseo.edu/postings/search', 0, (42.795896, -77.816947)],
['https://jobs.liu.edu/#/list', 0, (40.64530975, -73.9550230275334)],
['https://jobs.mercy.edu/postings/search', 0, (41.013115, -73.849734)],
['https://jobs.naz.edu/postings/search', 0, (43.1635257, -77.6083784825996)],
['https://jobs.niagara.edu/JobPostings.aspx', 0, (43.13755555, -79.0375125585894)],
['https://jobs.plattsburgh.edu/postings/search', 0, (44.69282, -73.45562)],
['https://jobs.purchase.edu/applicants/jsp/shared/frameset/Frameset.jsp', 0, (41.0409305, -73.7145746)],
['https://jobs.sjfc.edu', 0, (43.1635257, -77.6083784825996)],
['https://jobsatupstate.peopleadmin.com/applicants/jsp/shared/search/SearchResults_css.jsp', 0, (43.0481221, -76.1474244)],
['https://law-touro-csm.symplicity.com/students/index.php/pid170913', 0, (41.1073184, -73.7959667)],
['https://maritime.interviewexchange.com/static/clients/373SMM1/index.jsp', 0, (40.8214533, -73.8241910783815)],
['https://mountsaintvincent.edu/campus-life/campus-services/human-resources/employment-opportunities', 0, (40.90056, -73.90639)],
['https://mvcc.csod.com/ats/careersite/search.aspx', 0, (43.079254, -75.221178)],
['https://ncc.interviewexchange.com/static/clients/489NCM1/index.jsp', 0, (40.72319685, -73.6403872966069)],
['https://occc.interviewexchange.com/static/clients/437SOM1/index.jsp', 0, (41.44591415, -74.4224417389405)],
['https://oldwestbury.interviewexchange.com/static/clients/519OWM1/index.jsp', 0, (40.7887113, -73.5995717)],
['https://oswego.interviewexchange.com/static/clients/313OSM1/index.jsp', 0, (43.4547284, -76.5095967)],
['https://pa334.peopleadmin.com/postings/search', 0, (40.8088437, -73.9658566)],
['https://recruiting.ultipro.com/CUL1001CLNRY/JobBoard/5d1a692d-cf6b-4b4f-8652-c60b25898609/?q=&o=postedDateDesc', 0, (41.7847232, -73.9332461)],
['https://rpijobs.rpi.edu', 0, (42.7284117, -73.6917878)],
['https://strose.interviewexchange.com/jobsrchresults.jsp', 0, (42.6511674, -73.754968)],
['https://suny.oneonta.edu/sponsored-programs/employment-opportunities', 0, (42.453492, -75.0629531)],
['https://sunydutchess.interviewexchange.com/static/clients/539DCM1/index.jsp', 0, (41.5965635, -73.9112103)],
['https://sunyocc.peopleadmin.com/postings/search', 0, (43.0481221, -76.1474244)],
['https://sunyopt.peopleadmin.com/postings/search', 0, (40.7308619, -73.9871558)],
['https://sunypoly.interviewexchange.com/static/clients/511SPM1/hiring.jsp', 0, (42.6511674, -73.754968)],
['https://sunysullivan.edu/offices/associate-vp-for-planning-human-resources-facilities/job-opportunities', 0, (41.77415415, -74.6566052645852)],
['https://touro.peopleadmin.com/postings/search', 0, (40.7287818856407, -73.8210681595253)],
['https://trocaire.applicantpro.com/jobs', 0, (42.8867166, -78.8783922)],
['https://utsnyc.edu/about/careers-at-union', 0, (40.8088437, -73.9658566)],
['https://wagner.edu/hr/hr_openings', 0, (40.5834379, -74.1495875)],
['https://workforcenow.adp.com/mdf/recruitment/recruitment.html?cid=b635a855-6cf7-4ee7-ba36-6da36d9f2eea&ccId=19000101_000001&type=MP', 0, (41.1151372, -74.1493948)],
['https://www.alfred.edu/jobs-at-alfred/index.cfm', 0, (42.2542366, -77.7905509)],
['https://www.bankstreet.edu/about-bank-street/job-opportunities', 0, (40.7967148, -73.9647223)],
['https://www.binghamton.edu/human-resources/employment-opportunities/index.html', 0, (42.096968, -75.914341)],
['https://www.brockport.edu/support/human_resources/empop/vacancies', 0, (43.213671, -77.93918)],
['https://www.brooklaw.edu/about-us/job-opportunities.aspx', 0, (40.64530975, -73.9550230275334)],
['https://www.cayuga-cc.edu/about/human-resources', 0, (42.9320202, -76.5672029)],
['https://www.cnr.edu/employment-opportunities', 0, (40.9115386, -73.7826363)],
['https://www.davisny.edu/jobs', 0, (42.1156308, -75.9588092)],
['https://www.dc.edu/human-resources', 0, (41.0465776, -73.9496707)],
['https://www.ecc.edu/work', 0, (42.8867166, -78.8783922)],
['https://www.elmira.edu/Student/Offices_Resources/Employment_Opportunities/index.html', 0, (42.0897965, -76.8077338)],
['https://www.esc.edu/human-resources/employment-opportunities', 0, (43.0821793, -73.7853915)],
['https://www.flcc.edu/jobs', 0, (42.8844625, -77.278399)],
['https://www.fmcc.edu/about/employment-opportunities', 0, (43.0068689, -74.3676437)],
['https://www.fordham.edu/info/23411/job_opportunities', 0, (40.85048545, -73.8404035580209)],
['https://www.ftc.edu/employment', 0, (40.8175985, -73.3540078)],
['https://www.hamilton.edu/offices/human-resources/employment/job-opportunities', 0, (44.7278943, -73.6686982)],
['https://www.hartwick.edu/about-us/employment/human-resources/employment-opportunities', 0, (42.453492, -75.0629531)],
['https://www.helenefuld.edu/employment', 0, (40.7238838, -73.9911486)],
['https://www.hilbert.edu/about/human-resources/hilbert-job-openings', 0, (42.716293, -78.828717)],
['https://www.hofstra.edu/about/jobs/index.html', 0, (40.7063185, -73.618684)],
['https://www.hofstra.edu/academics/colleges/zarb', 0, (40.7063185, -73.618684)],
['https://www.hws.edu/offices/hr/employment/index.aspx', 0, (42.8689552, -76.9777436)],
['https://www.juilliard.edu/jobs', 0, (40.7771311410301, -73.9808786732298)],
['https://www.keuka.edu/hr/employment-opportunities', 0, (42.8689552, -76.9777436)],
['https://www.laguardia.edu/employment', 0, (40.7308619, -73.9871558)],
['https://www.lemoyne.edu/Work-at-Le-Moyne', 0, (43.0481221, -76.1474244)],
['https://www.limcollege.edu/about-lim/careers', 0, (40.7607161, -73.9669623)],
['https://www.mmm.edu/offices/human-resources/Employment', 0, (40.7666562, -73.9508886)],
['https://www.molloy.edu/about-molloy-college/human-resources/careers-at-molloy', 0, (40.6574186, -73.6450664)],
['https://www.monroecollege.edu/About/Employment/u', 0, (42.6511674, -73.754968)],
['https://www.morrisville.edu/contact/offices/human-resources/careers', 0, (42.8986566, -75.6402204)],
['https://www.msmc.edu/employment', 0, (41.5034271, -74.0104179)],
['https://www.msmnyc.edu/about/employment-at-msm', 0, (40.8088437, -73.9658566)],
['https://www.mville.edu/about-manhattanville/human-resources', 0, (41.0409305, -73.7145746)],
['https://www.newpaltz.edu/hr/jobs.html', 0, (41.7464972, -74.0844894)],
['https://www.newschool.edu/performing-arts', 0, (40.7308619, -73.9871558)],
['https://www.nyack.edu/site/employment-opportunities', 0, (40.7308619, -73.9871558)],
['https://www.paycomonline.net/v4/ats/web.php/jobs', 0, (40.7308619, -73.9871558)],
['https://www.qc.cuny.edu/HR/Pages/JobListings.aspx', 0, (40.6524927, -73.7914214158161)],
['https://www.roberts.edu/employment', 0, (43.157285, -77.615214)],
['https://www.rochester.edu/faculty-recruiting/positions', 0, (43.157285, -77.615214)],
['https://www.sage.edu/about/human-resources/employment-opportunities', 0, (42.7284117, -73.6917878)],
['https://www.sarahlawrence.edu/human-resources/job-openings.html', 0, (40.9381544, -73.8320784)],
['https://www.sbu.edu/jobs-at-sbu', 0, (42.0761398888889, -78.475734)],
['https://www.sfc.edu/about/careers', 0, (40.64530975, -73.9550230275334)],
['https://www.sjcny.edu/employment', 0, (40.64530975, -73.9550230275334)],
['https://www.stac.edu/about-stac/jobs-stac', 0, (41.0289025, -73.9326580670926)],
['https://www.stjohns.edu/about/administrative-offices/human-resources/recruitment', 0, (40.6524927, -73.7914214158161)],
['https://www.stonybrookmedicine.edu/careers', 0, (40.9215391, -73.1279744)],
['https://www.sujobopps.com/postings/search', 0, (43.0481221, -76.1474244)],
['https://www.suny.edu/campuses/cornell-vet', 0, (42.4396039, -76.4968019)],
['https://www.suny.edu/careers/employment/index.cfm?s=y', 0, (42.6511674, -73.754968)],
['https://www.sunycgcc.edu/about-cgcc/employment-cgcc', 0, (42.2528649, -73.790959)],
['https://www.sunyjcc.edu/about/human-resources/jobs', 0, (42.0970023, -79.2353259)],
['https://www.sunyjefferson.edu/careers-jefferson/open-positions.php', 0, (44.058053, -75.74324)],
['https://www.sunyulster.edu/campus_and_culture/about_us/jobs.php', 0, (41.8531485, -74.1390329)],
['https://www.tkc.edu/careers-at-kings', 0, (40.7308619, -73.9871558)],
['https://www.tompkinscortland.edu/college-info/employment', 0, (42.4909053, -76.2971553)],
['https://www.ubjobs.buffalo.edu', 0, (42.8867166, -78.8783922)],
['https://www.usmma.edu/about/employment/career-opportunities', 0, (40.8198231, -73.7351316)],
['https://www.vaughn.edu/jobs', 0, (40.7660002, -73.8636574)],
['https://www.villa.edu/about-us/employment-opportunities', 0, (42.8867166, -78.8783922)],
['https://www.warner.rochester.edu/faculty/positions', 0, (43.157285, -77.615214)],
['https://www.wells.edu/jobs', 0, (42.7539591, -76.7024485)],
['https://www.york.cuny.edu/administrative/human-resources/jobs', 0, (40.69983135, -73.8077028537026)],
['https://www.yu.edu/hr/opportunities', 0, (40.8493254985483, -73.9351991867384)],
['https://www2.appone.com/Search/Search.aspx?ServerVar=ConcordiaCollege.appone.com&results=yes', 0, (40.9381544, -73.8320784)],
['https://www3.sunysuffolk.edu/About/Employment.asp', 0, (40.8664874, -73.0356625)]
)


new_grudb = []
multi_entry = []
multi_em = []
unused_entry = []
unused_em = []

used_em = []

for o_entry in grudb_list:
    entry = o_entry[1] 

    working = []


    for o_each_em in em_list:
        each_em = o_each_em[0]

        # Form each em
        each_em = each_em.split('://')[1]

        if 'www' in each_em:
            each_em = each_em.split('.')[1]

        if '/' in each_em:
            each_em = each_em.split('/')[0]

        #if each_em.count('.') > 1:
            #each_em = each_em.split('.')[1]

        print(each_em)

        if each_em in entry:

            # Multi em
            if each_em in used_em:
                multi_em.append(each_em)
            else:
                used_em.append(each_em)


            o_entry[2] = o_each_em[0]

            working.append(o_entry)


    # Good
    if len(working) == 1:
        new_grudb.append(working)

    # Multi entry
    elif len(working) > 1:
        multi_entry.append(working)

    # Unused entry
    else:
        unused_entry.append(o_entry)


# Find unused em
print('000000000')
for i in used_em:
    print(i)
print('111111111')
for i in em_list:
    print(i[0])
    for ii in used_em:
    
        if ii[0] in i[0]:
            break

    else:
        unused_em.append(i)




print('\n Good:')
for i in new_grudb:
    print('\n', i)
print(len(new_grudb))


print('\n Multi entry:')
for i in multi_entry:
    print('\n', i)
print(len(multi_entry))

print('\n Multi em:')
for i in multi_em:
    print('\n', i)
print(len(multi_em))


print('\n Unused entrys:')
for i in unused_entry:
    print('\n', i)
print(len(unused_entry))

print('\n Unused em:')
for i in unused_em:
    print('\n', i)
print(len(unused_em))


# fkin kill me







