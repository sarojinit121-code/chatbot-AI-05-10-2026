"""
Seed database for LocalLens Tourism Chatbot
Populates tourism.db with extensive data for Tamil Nadu, Kerala, Pondicherry & Karnataka destinations.
Includes deep-dive place metadata: How to reach, Nearby attractions, Insider tips, Timings, Entry fees, Food.
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'tourism.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop old destinations table if columns need update
    cursor.execute('DROP TABLE IF EXISTS destinations')
    cursor.execute('DROP TABLE IF EXISTS itineraries')

    # Create destinations table with deep dive fields
    cursor.execute('''
    CREATE TABLE destinations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        state TEXT NOT NULL,
        city TEXT NOT NULL,
        place_name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        best_time TEXT,
        timings TEXT,
        entry_fee TEXT,
        highlights TEXT,
        famous_food TEXT,
        tag TEXT,
        how_to_reach TEXT,
        nearby_attractions TEXT,
        insider_tips TEXT
    )
    ''')

    # Create itineraries table
    cursor.execute('''
    CREATE TABLE itineraries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        duration_days INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        plan_json TEXT NOT NULL,
        estimated_budget TEXT
    )
    ''')

    # Create chat_sessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_sessions (
        session_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create chat_messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        meta_json TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
    )
    ''')

    # Seed Destinations Data with Complete Deep-Dive Details
    destinations = [
        # OOTY
        (
            'Tamil Nadu', 'Ooty', 'Doddabetta Peak', 'Viewpoint & Hills',
            'The highest peak in the Nilgiri Hills at 2,637 meters (8,650 ft). Offers an awe-inspiring panoramic 360-degree vista of the Nilgiris, Coimbatore plains, and Mysore plateau.',
            'October to May (Morning 8:30 AM - 11:00 AM for clear skies)', '9:00 AM - 6:00 PM', '₹10 per person, ₹50 for camera',
            'Telescope House, 360-degree Nilgiri Panorama, Shola Forest canopy, Chilly mountain breeze',
            'Hot Cardamom Chai, Steaming Vadas, Roasted Sweet Corn at summit',
            'Must-Visit Peak',
            'Located 9 km from Ooty town center. Easily reached by local government buses from Ooty bus stand (Route 11) or rental taxi/auto (approx ₹300-₹400 round trip). Nearest airport: Coimbatore (88 km).',
            'Doddabetta Tea Factory (1.5 km), Botanical Garden (7 km), Rose Garden (8 km)',
            'Visit before 10:30 AM; after 11 AM thick mist frequently blankets the valley, obstructing telescope viewing. Carry a warm windbreaker jacket.'
        ),
        (
            'Tamil Nadu', 'Ooty', 'Government Botanical Garden', 'Nature & Botanical',
            'Spread over 55 acres on the lower slopes of Doddabetta peak, housing over 650 species of exotic and indigenous plants, a 20-million-year-old fossilized tree trunk, and terraced Italian gardens.',
            'September to May (Annual Flower Show in May)', '7:00 AM - 6:30 PM', '₹40 (Adults), ₹20 (Kids), Camera ₹50',
            '20-Million-Year-Old Fossil Tree, Fern House, Italian Lawns, Toda Hill, Orchidarium',
            'Ooty Homemade Chocolates, Eucalyptus oil products, Fresh strawberries',
            'Top Attraction',
            'Just 2.5 km from Ooty Railway Station & Bus Stand. Frequent auto-rickshaws (₹80-₹100) and town buses connect directly to the main gate.',
            'Government Rose Garden (3.5 km), Ooty Lake (4 km), Stone House (1.5 km)',
            'Wear comfortable walking shoes as the garden is spread across steep terraced slopes. The lower lawn is ideal for peaceful family picnics.'
        ),
        (
            'Tamil Nadu', 'Ooty', 'Ooty Lake & Boat House', 'Boating & Leisure',
            'An iconic 65-acre artificial lake constructed in 1824 by John Sullivan, surrounded by whispering eucalyptus groves. Features paddle, rowing, and motor boat cruises, plus a mini train for kids.',
            'All year round (Best during sunset 4:00 PM - 6:00 PM)', '9:00 AM - 6:00 PM', '₹15 (Entry), Boating ₹180 - ₹450',
            'Row & Pedal Boating, Motor Safari Boat, Lakeside Cycling, Mini Toy Train for Kids, Horse Riding',
            'Nilgiri Fresh Strawberries with cream, Hot Molaga Bajjis, Chocolate Fudge',
            'Family Favorite',
            'Only 1.5 km from Ooty Bus Stand and Ooty Railway Station. Within walking distance or a 5-minute auto ride (₹60).',
            'Deer Park (adjacent to lake), Thread Garden (300 m), Rose Garden (2.5 km)',
            'Arrive by 4:00 PM to get boating tickets before queues peak. Pedal boating in the late afternoon offers magical mountain reflections on calm waters.'
        ),
        (
            'Tamil Nadu', 'Ooty', 'Government Rose Garden', 'Floral & Leisure',
            'One of the largest rose gardens in India situated on Elk Hill slopes at 2,200m, featuring over 20,000 rose varieties across 5 curving terraces.',
            'March to June (Full bloom season)', '8:30 AM - 6:00 PM', '₹40 (Adults), ₹20 (Kids), Camera ₹50',
            'Over 2,800 cultivars of roses, Miniature roses, Rare green and black roses, Nila Maadam panoramic observation platform',
            'Natural rose water, Rose gulkand, Herbal tea',
            'Scenic & Romantic',
            'Located 3 km from the Ooty bus stand on the slopes of Elk Hill. Quick auto ride (₹80) from town center.',
            'Botanical Garden (3.5 km), Ooty Lake (3.8 km), Elk Hill Murugan Temple (1.5 km)',
            'Climb to the topmost observation pergola (Nila Maadam) for a majestic top-down vista of terraced rose carpets and Ooty town below.'
        ),
        (
            'Tamil Nadu', 'Ooty', 'Pykara Lake & Waterfalls', 'Waterfalls & Nature',
            'Scenic river and lake nestled 21 km from Ooty amidst pristine shola forests and Toda tribal homeland. Features majestic cascades breaking into twin falls and high-speed boating.',
            'September to March (Post-monsoon water flow is at its peak)', '9:30 AM - 5:30 PM', '₹10 (Entry), Speed Boating ₹800 (for 8 people)',
            'Twin Cascading Falls, Forest Speedboat Cruise, Dense Pine Woods, Wenlock Downs backdrop',
            'Hot Maggi noodles, Spiced tea, Steamed sweet corn',
            'Adventure & Nature',
            'Located 21 km from Ooty along the Ooty-Mysore highway. Accessible via state transport buses heading to Gudalur/Mysore or hire cab (₹1200 round trip including waiting).',
            'Wenlock Downs 9th Mile (7 km), Pine Forest (9 km), Kamaraj Sagar Dam (12 km)',
            'Wear non-slip sports shoes as the trek down from the parking lot to the base of Pykara Falls has slippery rocks. Battery buggies are available for seniors.'
        ),
        (
            'Tamil Nadu', 'Ooty', 'Nilgiri Mountain Railway (Toy Train)', 'Heritage & Railway',
            'UNESCO World Heritage toy train built in 1908 connecting Mettupalayam to Ooty via Coonoor. Uses an ingenious rack-and-pinion system through 16 tunnels and 250 bridges.',
            'All year round (Clear mornings best)', 'Departures: 9:15 AM & 2:00 PM from Ooty', '₹30 (Second Class) to ₹205 (First Class)',
            'Vintage steam locomotive, Deep Nilgiri gorges, Lush tea valleys, Historic Swiss-engineered cog wheels',
            'Nilgiri spiced vadas and tea sold on station platforms',
            'UNESCO Heritage',
            'Departs from Udagamandalam (Ooty) Railway Station located in town center. Connected by rail to Mettupalayam and Coonoor.',
            'Ooty Lake (1.5 km), Rose Garden (2 km), Coonoor Sim’s Park (18 km by train)',
            'Tickets sell out weeks in advance on IRCTC. If online tickets are full, reach Ooty station at 6:00 AM for the limited same-day unreserved quota counter.'
        ),
        (
            'Tamil Nadu', 'Ooty', 'Tea Museum & Factory', 'Culture & Factory Tour',
            'Situated on the slopes adjacent to Doddabetta Peak, this working tea factory demonstrates orthodox and CTC tea leaf processing, drying, and grading with free freshly brewed tea.',
            'All year round', '9:00 AM - 6:30 PM', '₹10 (Entry fee)',
            'Live CTC tea processing demonstration, Tea tasting counter, Chocolate making room, Nilgiri tea souvenir shop',
            'Freshly brewed Cardamom & Masala Tea, White Tea, Homemade chocolates',
            'Cultural Experience',
            'Located 4 km from Ooty town on the Doddabetta Road. Autos charge approximately ₹150 from town.',
            'Doddabetta Peak (3 km), Botanical Garden (3.5 km)',
            'Don\'t miss the complimentary cup of freshly brewed hot cardamom tea at the end of the factory tour. Great spot to buy authentic single-estate black and green tea.'
        ),

        # CHENNAI
        (
            'Tamil Nadu', 'Chennai', 'Marina Beach', 'Beach & Heritage',
            'The second longest natural urban beach in the world stretching 13 km along the Coromandel Coast of the Bay of Bengal, featuring a promenade, lighthouse, and evening street food carnival.',
            'November to February (Evenings 4:30 PM - 9:00 PM)', 'Open 24 hours (Stalls 4:00 PM - 10:30 PM)', 'Free Entry (Lighthouse ticket ₹20)',
            'Madras Lighthouse with elevator, Memorials of Anna, MGR & Karunanidhi, Sandy promenade, Seaside kite flying, Horse rides',
            'Freshly fried fish (Nethili, Vanjaram fry), Pattani Sundal, Murukku Sandwich, Mango slices with chili powder',
            'Iconic Landmark',
            'Located in the heart of Chennai along Kamarajar Promenade. Reachable via MRTS train to Light House or Chepauk station, Chennai Metro (LIC / Government Estate station + short auto), or MTC buses.',
            'Kapaleeshwarar Temple (3 km), San Thome Cathedral (1.5 km), Fort St. George (4 km)',
            'Climb or take the elevator up the Marina Lighthouse between 3 PM - 5 PM for an aerial 360-degree view of the Coromandel coast and Chennai skyline. Swimming in the sea is strictly prohibited due to strong undercurrents.'
        ),
        (
            'Tamil Nadu', 'Chennai', 'Kapaleeshwarar Temple, Mylapore', 'Spiritual & Heritage',
            'A 7th-century Dravidian architectural masterpiece dedicated to Lord Shiva and Karpagambal. Renowned for its vibrant 37-meter rainbow gopuram, monolithic pillars, and sacred temple tank.',
            'October to March (Festival season Panguni Uthiram in March/April is magnificent)', '5:30 AM - 12:00 PM, 4:00 PM - 9:30 PM', 'Free Entry',
            'Majestic Dravidian Sculptures, Sacred Theppakulam (Temple Tank), Vahana pavilion, Traditional Nadaswaram music, Evening Aarthi',
            'Mylapore Ghee Pongal, Crispy Medu Vada, Traditional Kumbakonam Degree Coffee, Murugan Idli',
            'Spiritual Gem',
            'Located in central Mylapore, Chennai. Nearest railway station: Thirumayilai MRTS (500 meters). Connected by all south-bound MTC buses and Chennai Metro (AG-DMS + 10 min auto).',
            'San Thome Cathedral (1.8 km), Marina Beach (2.5 km), Ramakrishna Math (1 km)',
            'Strict traditional dress code: Men must wear pants or dhoti (no shorts), women sarees or salwar kameez. Remove footwear outside near the north tower.'
        ),
        (
            'Tamil Nadu', 'Chennai', 'San Thome Basilica', 'Heritage & Cathedral',
            'A magnificent neo-Gothic cathedral built in the 16th century by Portuguese explorers over the tomb of St. Thomas, one of the original twelve apostles of Jesus Christ.',
            'All year round', '6:00 AM - 9:00 PM', 'Free Entry',
            'Underground Tomb of St. Thomas, Neo-Gothic spires, Stained glass windows from Portugal, Museum with 1st-century apostle relics',
            'South Indian snacks at seaside cafes, San Thome bakery puffs',
            'Global Pilgrimage',
            'Located on Santhome High Road, right by the southern end of Marina Beach. Light House MRTS station is 1 km away.',
            'Marina Beach (500 m), Kapaleeshwarar Temple (1.8 km), Besant Nagar Beach (4 km)',
            'Visit the underground tomb chapel located behind the main altar for quiet contemplation and historical relics dating back 2,000 years.'
        ),
        (
            'Tamil Nadu', 'Chennai', 'Fort St. George & Museum', 'History & Colonial',
            'Built in 1644 by the British East India Company, it is the first English fortress in India. Houses St. Mary’s Church (oldest Anglican church in India), the Tamil Nadu Secretariat, and colonial weaponry.',
            'October to March', '9:00 AM - 5:00 PM (Museum closed on Fridays)', '₹25 (Indians), ₹300 (Foreigners)',
            'Colonial Cannons, St. Mary’s Church (1680), Robert Clive memorabilia, British regimental flags, Old Madras coin collection',
            'Traditional South Indian Thali in George Town, Badam Milk',
            'Historical Bastion',
            'Located near Chennai Port in Rajaji Salai. Nearest suburban railway station: Chennai Fort (500m) or Chennai Central (1.5 km).',
            'High Court Buildings (1 km), Marina Beach (3 km), Parry’s Corner Spice Market (1 km)',
            'Carry a government photo ID (Aadhaar or Passport) as Fort St. George is a protected government administrative headquarters with security checkpoints.'
        ),
        (
            'Tamil Nadu', 'Chennai', 'Besant Nagar (Elliot\'s) Beach', 'Beach & Lifestyle',
            'A cleaner, relaxed seaside promenade featuring the iconic Karl Schmidt Memorial, vibrant youth cafes, and tranquil sunset strolling away from downtown congestion.',
            'November to March', 'Open 24 hours (Bustling 4:30 PM - 11:00 PM)', 'Free Entry',
            'Karl Schmidt Memorial, Paved Seaside Promenade, Ashtalakshmi Temple nearby, Velankanni Church',
            'Wood-fired seaside pizza, Filter coffee, Coakers sweet corn, Podi Dosa at Murugan Idli',
            'Youth & Leisure',
            'Located in Besant Nagar, South Chennai. Reachable via Adyar bus depot (2 km) or cab/auto from anywhere in Chennai.',
            'Ashtalakshmi Temple (800 m), Theosophical Society gardens (2 km), Guindy National Park (5 km)',
            'The road along the beach is vehicle-free on weekend mornings, making it popular for joggers and fitness enthusiasts.'
        ),
        (
            'Tamil Nadu', 'Chennai', 'DakshinaChitra Heritage Museum', 'Art & Culture',
            'A living-history open-air museum on East Coast Road showcasing 18 authentic heritage houses from Tamil Nadu, Kerala, Karnataka, and Andhra Pradesh with live craft artisans.',
            'October to March', '10:00 AM - 6:00 PM (Closed on Tuesdays)', '₹175 (Adults), ₹75 (Children)',
            'Traditional Chettinad Mansion, Kerala wooden Tharavadu, Live pottery wheels, Puppet shows, Silk weaving looms',
            'Traditional South Indian Thali served inside, Fresh tender coconuts along ECR',
            'Living Heritage',
            'Located at Muttukadu on East Coast Road (ECR), 25 km south of central Chennai. Take ECR-bound buses (Route 588, 599) or cab/self-drive down the scenic coastline.',
            'Muttukadu Boat House (1 km), Kovalam Beach (5 km), Mahabalipuram (20 km)',
            'Plan at least 3 hours to stroll through all four state zones. Artisans demonstrate pottery and block printing where visitors can try hands-on crafts.'
        ),

        # MAHABALIPURAM (MAMALLAPURAM)
        (
            'Tamil Nadu', 'Mahabalipuram', 'Shore Temple', 'UNESCO World Heritage',
            'A breathtaking 8th-century granite temple complex built by the Pallava King Narasimhavarman II overlooking the surging waves of the Bay of Bengal.',
            'October to March (Cool sea breeze, sunrise is spectacular)', '6:00 AM - 6:00 PM', '₹40 (Indians), ₹600 (Foreigners) - Composite ASI ticket',
            'Monolithic granite shrines, Carved relief of reclining Vishnu, Sculpted Nandi bulls along enclosure wall, Ocean backdrop',
            'Fresh grilled seafood at beach shacks, Fish curry meals, Coconut water',
            'UNESCO World Wonder',
            'Located 55 km south of Chennai on East Coast Road (ECR). Regular buses run from Chennai CMBT/Koyambedu and Thiruvanmiyur, or hire an ECR cab (1.5 hours drive).',
            'Pancha Rathas (1.5 km), Arjuna’s Penance (1 km), Krishna’s Butter Ball (1 km)',
            'The single ₹40 ASI ticket grants entry to Shore Temple, Pancha Rathas, and surrounding monuments on the same day. Keep the ticket safe.'
        ),
        (
            'Tamil Nadu', 'Mahabalipuram', 'Arjuna\'s Penance & Krishna\'s Butter Ball', 'Heritage & Rock Sculptures',
            'One of the largest open-air rock bas-reliefs in the world (96 x 43 ft) depicting the Descent of the Ganges, paired with a gigantic 250-tonne boulder balancing precariously on a 45-degree slope.',
            'October to March', '6:00 AM - 6:00 PM', 'Free (Rock relief open area)',
            'Life-size elephant sculptures, Flowing celestial beings, 250-tonne gravity-defying boulder, Panchapandava cave temple',
            'Local coconut water, South Indian snacks, Fried seafood',
            'Geological & Art Marvel',
            'Located in the town center of Mahabalipuram, within easy walking distance from Shore Temple.',
            'Shore Temple (800 m), Pancha Rathas (1.2 km), Light House (500 m)',
            'A must-do photo spot: Stand beside Krishna\'s Butter Ball pretending to push the boulder. The rock has remained balanced for over 1,200 years.'
        ),

        # KODAIKANAL
        (
            'Tamil Nadu', 'Kodaikanal', 'Kodaikanal Lake', 'Lake & Boating',
            'A magnificent star-shaped artificial lake created in 1863 by Sir Vere Levinge spanning 60 acres, nestled amidst emerald slopes and pine trees.',
            'All year round (September to May best)', '6:00 AM - 5:00 PM', 'Free (Boating ₹150 - ₹400)',
            'Pedal & Row Boating, 5 km perimeter Tandem Bicycle Rides, Lakeside Horse Riding, Sunset views',
            'Roasted Marshmallows, Hot Plum Cakes, Fresh Peaches & Pears, Homemade Kodai fudge',
            'Heart of Kodai',
            'Situated at the very center of Kodaikanal town. Walkable from most town hotels or short auto ride (₹50-₹80). Nearest railway: Kodai Road (80 km).',
            'Bryant Park (200 m), Coaker’s Walk (600 m), Kurinji Andavar Temple (4 km)',
            'Renting a tandem bicycle to ride around the 5 km lake perimeter in the crisp morning air is one of Kodaikanal’s signature experiences.'
        ),
        (
            'Tamil Nadu', 'Kodaikanal', 'Coaker\'s Walk', 'Viewpoint & Walkway',
            'A 1-kilometer pedestrian paved pathway winding around Mount Nebo, offering breathtaking bird\'s-eye panoramas of the plains of Madurai and mist-shrouded valleys.',
            'October to May (Morning 7:30 AM - 10:00 AM or Sunset 4:30 PM)', '7:00 AM - 7:00 PM', '₹30 per person, Camera ₹30',
            'Sweeping valley views, Telescope House, Mountain mist breeze, Rare Brocken Spectre cloud phenomenon',
            'Steamed sweet corn, Spiced tea, Milagai Bajji, Hot onion pakodas',
            'Romantic Walk',
            'Located just 500 meters from Kodaikanal Lake and bus stand; accessible easily by foot.',
            'Bryant Park (adjacent, 50 m), Kodaikanal Lake (500 m), Sacred Heart Church (1 km)',
            'Visit early in the morning when the plains are clearly visible before clouds rise up and engulf the gorge.'
        ),
        (
            'Tamil Nadu', 'Kodaikanal', 'Pillar Rocks', 'Nature & Geology',
            'Three colossal vertical granite boulders standing 122 meters (400 ft) high against a sheer precipice, shrouded in dancing white mist and deep pine gorges.',
            'September to April', '9:00 AM - 4:30 PM', '₹10 per person',
            '400-foot sheer granite pillars, Mist-covered canyon, Chamber between pillars called Devil’s Kitchen nearby, Manicured viewpoint garden',
            'Hot Onion Pakodas, Masala Chai, Homemade Kodai fudge',
            'Breathtaking Rocks',
            'Located 8 km from Kodaikanal town center along the scenic Pillar Rocks Road. Regular cabs and minibuses operate from town.',
            'Guna Caves / Devil\'s Kitchen (1 km), Pine Forest (2.5 km), Moir Point (3 km)',
            'Patience is key here: Thick mist frequently hides the pillars, but within 5 to 10 minutes a mountain gust often sweeps the clouds away, unveiling the dramatic vertical rocks.'
        ),
        (
            'Tamil Nadu', 'Kodaikanal', 'Pine Forest', 'Nature & Cinema',
            'A dense, preserved pine plantation established by Mr. Bryant in 1906. Famous backdrop in countless Tamil, Malayalam, and Hindi cinema scenes (Manjummel Boys, Devar Magan).',
            'All year round', '8:00 AM - 5:00 PM', '₹10 per person',
            'Towering century-old pine canopies, Natural needle-strewn forest floor, Cinematic photography, Horse trail rides',
            'Roasted peanuts, Pine cone souvenirs, Spiced tea',
            'Cinema Iconic',
            'Located 6 km from Kodaikanal town on the way to Pillar Rocks. Accessible by auto or taxi.',
            'Pillar Rocks (2.5 km), Guna Caves (1.5 km), Green Valley View (3 km)',
            'Avoid wearing slippery footwear as the pine needle carpet on the hillside slope can be slick. Ideal for family and couple photoshoot sessions.'
        ),
        (
            'Tamil Nadu', 'Kodaikanal', 'Dolphin\'s Nose', 'Trekking & Adventure',
            'A flat, protruding rock resembling a dolphin’s nose hovering above a 6,600 ft abyss. Requires a scenic 3 km moderate hike through rugged village trails.',
            'October to April (Daytime only)', '6:00 AM - 5:30 PM', 'Free (Guide optional ₹200)',
            'Thrilling rock ledge extending over deep gorge, View of Catherine Falls below, Rustic village trail, Echo point',
            'Freshly brewed ginger tea and maggi at cliffside stalls',
            'Adventure Trail',
            'Located 8 km from Kodaikanal town at Vattakanal village. Take a cab to Vattakanal, followed by a 1.5 km downhill trek to the rock ledge.',
            'Vattakanal Falls (1 km), Echo Rock (200 m), Altaf\'s Cafe Vattakanal',
            'The trek back up is moderately steep and takes about 45 minutes; carry water and avoid trekking after 4:30 PM due to sudden fog and lack of lighting.'
        ),

        # MADURAI
        (
            'Tamil Nadu', 'Madurai', 'Meenakshi Amman Temple', 'Spiritual & Architecture',
            'World-famous historic Hindu temple dedicated to Goddess Meenakshi (Parvati) and Sundareswarar (Shiva), featuring 14 towering sculpted gopurams and the celebrated Thousand Pillar Hall.',
            'October to March (Chithirai Festival in April is legendary)', '5:00 AM - 12:30 PM, 4:00 PM - 10:00 PM', 'Free (Special Darshan ₹100, Art Museum ₹5)',
            'Thousand Pillar Hall with 985 carved pillars, Musical Stone Pillars, Golden Lotus Tank (Porthamarai Kulam), Night Palliyarai ceremony at 9 PM',
            'Madurai Famous Jigarthanda, Bun Parotta, Kari Dosa, Murugan Idli Shop soft idlis with 4 chutneys',
            'World Heritage Marvel',
            'Located in the center of Madurai city. Only 1.5 km from Madurai Junction Railway Station and 12 km from Madurai Airport (IXM). Plentiful autos and city buses.',
            'Thirumalai Nayakkar Mahal (1.5 km), Gandhi Memorial Museum (4 km), Pudhu Mandapam (adjacent)',
            'Mobile phones, cameras, and leather belts are strictly banned inside the temple; deposit them at the official cloakroom outside the East Tower. Traditional dress code mandatory.'
        ),
        (
            'Tamil Nadu', 'Madurai', 'Thirumalai Nayakkar Mahal', 'Palace & Heritage',
            'A 17th-century Indo-Saracenic royal palace built in 1636 by King Thirumalai Nayak. Boasts gargantuan 82-foot circular pillars, Italian stucco arches, and an evening sound-and-light show.',
            'October to March', '9:00 AM - 5:00 PM (Light & Sound Show: 6:45 PM Tamil, 8:00 PM English)', '₹10 (Palace Entry), ₹50 (Light & Sound Show)',
            'Giant White Stucco Pillars (82 ft high, 19 ft wide), Royal Throne Room (Swarga Vilasam), Celestial Pavilions, Evening Sound & Light history show',
            'Madurai Bun Parotta at nearby roadside stalls, Hot filter coffee',
            'Royal Architecture',
            'Located 1.5 km southeast of Meenakshi Amman Temple. Easy 10-minute auto-rickshaw ride (₹60).',
            'Meenakshi Amman Temple (1.5 km), Saint Mary’s Cathedral (1 km), South Gate market',
            'Attend the 6:45 PM Sound & Light show (in Tamil) or 8:00 PM (in English) to hear the dramatic history of the Nayak dynasty and King Thirumalai\'s conquests.'
        ),
        (
            'Tamil Nadu', 'Madurai', 'Gandhi Memorial Museum', 'History & National',
            'Housed in the historic Tamukkam Palace of Rani Mangammal. Preserves the blood-stained garment worn by Mahatma Gandhi when he was assassinated in 1948, along with rare photo archives.',
            'All year round', '10:00 AM - 1:00 PM, 2:00 PM - 5:30 PM (Closed on Fridays)', 'Free Entry',
            'Blood-stained Dhoti of Mahatma Gandhi, Freedom Struggle Photo Archives, Ancient Tamukkam palace architecture, Peace park',
            'Local millet snacks, fresh herbal juices sold outside',
            'National Landmark',
            'Located in the Tamukkam area, 4 km north of Meenakshi Temple. Connected by city buses and autos (₹100).',
            'Government Museum (adjacent), Vandiyur Mariamman Teppakulam (5 km), Alagar Kovil (18 km)',
            'Take a quiet walk in the open grounds surrounding the palace. The museum documents how Gandhi decided to wear only a loincloth during his visit to Madurai in 1921.'
        ),

        # RAMESHWARAM
        (
            'Tamil Nadu', 'Rameshwaram', 'Ramanathaswamy Temple', 'Spiritual & Char Dham',
            'One of the 12 sacred Jyotirlinga shrines and Char Dham pilgrimage sites. Renowned worldwide for the longest pillared corridor in the world (1,212 carved sandstone pillars) and 22 holy theerthams.',
            'October to April', '5:00 AM - 1:00 PM, 3:00 PM - 9:00 PM', 'Free (22 Sacred Theerthams bath pass ₹25)',
            'World’s Longest Temple Corridor, 22 Sacred Wells holy bath, Agniteertham sea shore, Mani Darshan at 5:00 AM',
            'Hot Rameshwaram Idlis, Ghee Roast Dosa, Filter Coffee, Fresh coastal fish curry meals',
            'Sacred Jyotirlinga',
            'Located on Pamban Island in Rameshwaram town center. Just 1.5 km from Rameshwaram Railway Station. Autos available 24/7.',
            'Agniteertham (200 m), Ramar Patham (3 km), APJ Abdul Kalam National Memorial (4 km)',
            'Pilgrim sequence: Take a holy dip in the sea at Agniteertham first, then enter the temple for the sacred bath across the 22 wells before getting main deity darshan. Change of dry clothes required.'
        ),
        (
            'Tamil Nadu', 'Rameshwaram', 'Dhanushkodi Ghost Town & Beach', 'Offbeat & Coastal',
            'The abandoned ghost town destroyed during the catastrophic 1964 cyclone. Located at the southeastern tip of Pamban Island where the Bay of Bengal meets the Indian Ocean at Arichal Munai.',
            'October to March (Early morning 6:30 AM to catch calm ocean colors)', '6:00 AM - 6:00 PM (Police checkpoints restrict entry post sunset)', 'Free Entry',
            'Arichal Munai (India\'s southernmost land tip), Old submerged railway station ruins, Blown-away church arches, Confluence of two oceans',
            'Freshly fried sea fish from fishermen shacks, Sweet tender coconut, Spiced buttermilk',
            'Epic Ghost Town',
            'Located 18 km from Rameshwaram town. A brand-new scenic national highway leads straight to Arichal Munai. Accessible by town bus (Route 3), taxi, or private car (30 min drive).',
            'Kothandaramaswamy Temple (8 km), Ramanathaswamy Temple (18 km), Pamban Bridge (28 km)',
            'Notice the striking difference between the two sides of the road at Arichal Munai: the Bay of Bengal (Mahodadhi) is calm and emerald green, while the Indian Ocean (Ratnakara) has roaring azure waves.'
        ),
        (
            'Tamil Nadu', 'Rameshwaram', 'Pamban Rail Bridge', 'Engineering & Scenic',
            'India\'s first sea bridge opened in 1914 spanning 2.06 km across the Palk Strait, featuring a historic Scherzer rolling lift span that opens to allow cargo ships and ferries to pass.',
            'All year round (Sunset view from road bridge is mesmerizing)', 'Viewable anytime from the parallel Annai Indira Gandhi Road Bridge', 'Free Viewpoint',
            'Breathtaking azure sea views, Trains chugging over the ocean, Historic rolling lift span, Fisherman boats sailing underneath',
            'Tender coconut water, Sea salt crystal packets, Shell handicrafts sold on bridge',
            'Engineering Wonder',
            'Connects Mandapam on the Indian mainland to Pamban Island on Rameshwaram. All vehicles and trains to Rameshwaram cross this bridge.',
            'Ramanathaswamy Temple (14 km), Kalam Memorial (10 km), Mandapam beach (4 km)',
            'Stop your vehicle safely at designated pedestrian viewpoints on the high-level road bridge to photograph trains traversing the historic sea railway below.'
        ),

        # KANYAKUMARI
        (
            'Tamil Nadu', 'Kanyakumari', 'Vivekananda Rock Memorial', 'Spiritual & Monument',
            'A sacred monument built in 1970 on a rocky island 500 meters off the mainland where Swami Vivekananda attained enlightenment during 3 days of deep meditation in 1892.',
            'October to March', '8:00 AM - 4:00 PM', '₹20 (Entry), Ferry ₹50 (Ordinary) / ₹200 (Special)',
            'Ferry Boat Cruise through ocean waves, Dhyana Mandapam (silent meditation hall), Vivekananda Footprint, Triveni Sangam ocean panorama',
            'Fresh banana chips fried in pure coconut oil, Palm jaggery halwa, Nanjil fish curry meals',
            'Iconic National Monument',
            'Located 500 meters off the southern coast of Kanyakumari. Reached by regular ferry services from the Kanyakumari ferry terminal. Railway station is 1 km away.',
            'Thiruvalluvar Statue (adjacent island), Triveni Sangam (500 m), Gandhi Memorial (600 m)',
            'The Dhyana Mandapam inside the memorial is an exceptional space of profound silence and cool sea breeze. Take 15 minutes to meditate there.'
        ),
        (
            'Tamil Nadu', 'Kanyakumari', 'Thiruvalluvar Statue', 'Culture & Monument',
            'A towering 133-foot (40.5 m) stone sculpture of the ancient Tamil poet-philosopher Thiruvalluvar, standing on a nearby rock island symbolizing the 133 chapters of the Tirukkural.',
            'October to March', '8:00 AM - 4:00 PM (Accessible via ferry)', 'Combined with Vivekananda Rock ferry ticket',
            '133-foot tall granite colossus, 3-tier pedestal representing Virtue, Wealth & Love, Panoramic view of mainland coast',
            'Spiced pineapples, roasted peanuts, jackfruit chips',
            'Tamil Pride',
            'Reachable by the same ferry boat service that operates to Vivekananda Rock Memorial.',
            'Vivekananda Rock Memorial (200 m), Kanyakumari Beach (500 m)',
            'Walk inside the pedestal of the statue to see carved verses of the Tirukkural in Tamil and English.'
        ),
        (
            'Tamil Nadu', 'Kanyakumari', 'Sunset View Point & Triveni Sangam', 'Nature & Spectacle',
            'The southernmost tip of the Indian subcontinent where the Arabian Sea, Indian Ocean, and Bay of Bengal converge. Renowned for simultaneous moonrise and sunset on Chitra Pournami full moon days.',
            'November to February (Best sunset 5:30 PM - 6:30 PM, sunrise 6:00 AM)', 'Open 24 hours', 'Free Entry',
            'Confluence of three oceans (Triveni Sangam), Multicolored sands, Spectacular sunsets into the ocean, Sunrise view from beach',
            'Spiral potatoes, Roasted corn, Local seashell souvenirs',
            'Natural Wonder',
            'Located at the southern tip of Kanyakumari town, walking distance from all beach hotels.',
            'Bhagavathy Amman Temple (300 m), Gandhi Memorial (200 m), View Tower (800 m)',
            'Kanyakumari is one of the rare places in India where you can watch the sunrise and sunset from the same beach.'
        ),

        # THANJAVUR
        (
            'Tamil Nadu', 'Thanjavur', 'Brihadisvara Temple (Big Temple)', 'UNESCO Heritage & Chola',
            'A thousand-year-old architectural marvel built by Emperor Raja Raja Chola I in 1010 CE. Built entirely of hard granite with an 80-tonne single-stone vimana dome that casts no shadow at noon.',
            'October to March', '6:00 AM - 12:30 PM, 4:00 PM - 8:30 PM', 'Free Entry',
            'Massive monolithic Nandi (12 ft high, 20 tonnes), 216-ft Vimana tower, Ancient 11th-century Tamil fresco paintings, Chola royal inscriptions',
            'Thanjavur Royal Biryani, Ashoka Halwa, Bombay Halwa, Hot degree coffee',
            'Chola Architectural Wonder',
            'Located in the center of Thanjavur city. Only 1 km from Thanjavur Old Bus Stand and 2 km from Thanjavur Junction Railway Station.',
            'Thanjavur Maratha Palace (2 km), Saraswathi Mahal Library (2 km), Sivaganga Park (adjacent)',
            'Visit at 5:00 PM when the scorching granite stones cool down. As the setting sun bathes the golden vimana in amber light, the temple radiates an otherworldly glow.'
        ),
        (
            'Tamil Nadu', 'Thanjavur', 'Thanjavur Maratha Palace & Saraswathi Mahal Library', 'Royalty & Antiquity',
            'Official royal residence of Nayak and Maratha rulers, housing one of the oldest libraries in Asia with over 60,000 rare palm leaf and paper manuscripts.',
            'October to March', '10:00 AM - 1:00 PM, 1:30 PM - 5:30 PM', '₹30 per person, Camera ₹50',
            'Rare Palm-Leaf Manuscripts in Sanskrit and Tamil, Royal Arsenal & Weapons Tower, Giant 92-ft Whale Skeleton, Thanjavur Art Gallery bronze idols',
            'Thanjavur Dancing Dolls (Thalaiyatti Bommai), Tanjore Gold Foil Paintings',
            'Royal Antiquity',
            'Located in the center of Thanjavur, 2 km from the Big Temple. Accessible by local town bus or auto (₹50).',
            'Brihadisvara Temple (2 km), Schwartz Church (500 m), Royal Palace Museum',
            'Don\'t miss the Thanjavur Art Gallery inside the palace complex, which contains the world’s finest collection of Chola bronze Nataraja sculptures.'
        ),

        # PONDICHERRY
        (
            'Pondicherry', 'Pondicherry', 'White Town (French Quarter)', 'Heritage & Architecture',
            'The colonial French Quarter characterized by pastel yellow and mustard villas, bougainvillea-covered wrought-iron gates, cobblestone lanes, and chic French-Creole cafes.',
            'October to March (Best explored on foot or bicycle early morning / late evening)', 'Free to explore streetscapes 24/7', 'Free Entry',
            'French colonial architecture, Rue de la Marine, Boutique bistros, Guided cycling heritage tours, Street photography',
            'French croissants, Baguettes, Pain au Chocolat, Woodfired sourdough pizza, French-Creole sea prawns',
            'French Riviera of the East',
            'Located along the seaside in central Puducherry. 1 km from Puducherry Railway Station. Best explored by renting a bicycle (₹100/day) or scooter (₹350/day).',
            'Promenade Rock Beach (adjacent, 100 m), Sri Aurobindo Ashram (500 m), French War Memorial (300 m)',
            'Rent a vintage bicycle from Mission Street or Goubert Avenue early in the morning around 7:00 AM to photograph the quiet mustard-yellow French streets before cars arrive.'
        ),
        (
            'Pondicherry', 'Pondicherry', 'Promenade Beach (Rock Beach)', 'Beach & Promenade',
            'A 1.5-kilometer scenic seaside promenade along the Bay of Bengal, completely closed to all motor vehicles every evening from 6:00 PM to 7:30 AM for peaceful pedestrian strolls.',
            'October to March (Breezy evenings)', 'Open 24 hours (Vehicle-free 6 PM - 7:30 AM)', 'Free Entry',
            'Historic Gandhi Statue, French War Memorial, Old French Lighthouse, Giant sea-facing rocks, Evening cultural shows',
            'Italian Gelato ice creams, Cafe des Arts iced coffee, Nutella crepes, Hot samosas',
            'Seaside Vibe',
            'Runs parallel to White Town along Goubert Avenue in Puducherry town center.',
            'White Town (adjacent), Sri Aurobindo Ashram (400 m), Bharathi Park (300 m)',
            'Take a seat on the stone seawall around 6:30 PM to feel the salty ocean breeze as the street turns into a vibrant, car-free carnival of walkers and street artists.'
        ),
        (
            'Pondicherry', 'Pondicherry', 'Auroville & Matrimandir', 'Spiritual & Universal Township',
            'An experimental universal township founded in 1968 by Mirra Alfassa (The Mother). Features the breathtaking golden geodesic sphere \'Matrimandir\', dedicated to human unity and silent contemplation.',
            'October to March', 'Visitors Centre: 9:00 AM - 5:30 PM', 'Free (Inner Chamber requires advance booking 3-7 days prior)',
            'Golden Matrimandir sphere, Sacred Banyan Tree meditation zone, Visitors Centre international exhibitions, Sustainable organic craft boutiques',
            'Wood-fired vegan pizzas, Sourdough bread from Auroville Bakery, Spirulina smoothies, Organic Kombucha',
            'Spiritual Serenity',
            'Located 12 km north of Pondicherry town. Reachable by scooter, auto (₹300-₹400), or private cab via East Coast Road.',
            'Auroville Beach (6 km), Quiet Beach (5 km), Matrimandir Viewpoint (1 km walk from Visitors Centre)',
            'Walking from the Visitors Centre to the Matrimandir viewing point takes about 15 minutes through shaded forest paths; free electric shuttle vans are available for elderly visitors.'
        ),

        # KERALA - MUNNAR
        (
            'Kerala', 'Munnar', 'Eravikulam National Park', 'Wildlife & Sanctuary',
            'A high-altitude wildlife national park home to the largest surviving population of the endangered Nilgiri Tahr (mountain goat) and the rare Neelakurinji flower that blooms once every 12 years.',
            'September to May (Closed Feb-March for Tahr calving season)', '7:30 AM - 4:00 PM', '₹200 (Adults), ₹150 (Children)',
            'Endangered Nilgiri Tahr sightings, Anamudi Peak (highest peak in South India, 2,695m), Rolling shola grasslands, Safari bus ride through tea estates',
            'Kerala banana chips fried in coconut oil, Cardamom tea, Hot kappa and fish curry',
            'Wildlife & Peaks',
            'Located 13 km from Munnar town center along the Munnar-Udumalpet road. Forest department mini-buses take visitors from ticket counter to Rajamalai peak.',
            'Munnar Tea Museum (11 km), Mattupetty Dam (24 km), Lakkam Waterfalls (25 km)',
            'Book tickets online in advance via eravikulamnationalpark.in to skip the 1-2 hour entry ticket counter queues during peak holiday weekends.'
        ),
        (
            'Kerala', 'Munnar', 'Mattupetty Dam & Lake', 'Nature & Boating',
            'A concrete gravity dam built high in the mountains surrounded by rolling tea plantations, mist-covered Shola forests, and frequent wild elephant sightings drinking at the water banks.',
            'October to May', '9:30 AM - 5:00 PM', '₹10 (Entry), Speed Boating ₹500 (15 min for 5 people)',
            'Thrilling Speedboat cruise across reservoir, Echo Point acoustic fun, Wild elephant herds, Sprawling tea garden views',
            'Spiced buttermilk, Kerala flaky parotta with veg korma, Tender coconut',
            'Scenic Dam',
            'Located 13 km from Munnar town center on Top Station Road. Accessible by taxi or local KSRTC bus.',
            'Echo Point (4 km), Kundala Dam (14 km), Top Station (18 km)',
            'Combine Mattupetty Dam with Echo Point and Kundala Lake in a single morning circuit before the mountain roads get congested with afternoon tour buses.'
        )
    ]

    cursor.executemany('''
    INSERT INTO destinations (
        state, city, place_name, category, description, best_time, timings, entry_fee, 
        highlights, famous_food, tag, how_to_reach, nearby_attractions, insider_tips
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', destinations)

    # Seed Itineraries
    itineraries = [
        # OOTY 2 DAYS
        (
            'Ooty', 2, '2-Day Classic Ooty Nature, Hills & Tea Experience',
            'Comprehensive weekend itinerary covering peaks, lakes, UNESCO toy train and sprawling gardens.',
            json.dumps({
                "summary": "Perfect 2-day getaway to the Queen of Hill Stations. Balances cool heights, fragrant tea factories, and serene boat cruises.",
                "days": [
                    {
                        "day": 1,
                        "title": "Iconic Peaks, Tea Aromas & Botanical Splendor",
                        "morning": "Start at 8:30 AM at Doddabetta Peak for crisp valley views from the Telescope House before mist rolls in. Visit the adjacent Doddabetta Tea Factory & Museum for live tea-making and hot spiced tea.",
                        "afternoon": "Head down to Government Botanical Garden at 1:00 PM. Stroll through the 20-million-year-old fossil tree and Italian garden. Have lunch with authentic Chettinad/South Indian meals in Ooty town.",
                        "evening": "At 4:00 PM, reach Ooty Lake & Boat House. Enjoy pedal boating under the eucalyptus trees, followed by shopping for homemade chocolates on Commercial Road.",
                        "food_tip": "Grab freshly made hazelnut dark chocolates at King Star or Moddy's Confectionery."
                    },
                    {
                        "day": 2,
                        "title": "Toy Train Heritage, Rose Cascades & Pykara Waterfalls",
                        "morning": "Board the famous Nilgiri Mountain Railway (Toy Train) from Ooty to Coonoor or visit the Government Rose Garden with 20,000+ vibrant blooms across terraced hills.",
                        "afternoon": "Drive 20 km out towards Pykara Lake. Enjoy lunch at the Pykara lake boathouse restaurant surrounded by pine forests.",
                        "evening": "Take a thrilling speedboat ride on Pykara Lake and witness the roaring Pykara Waterfalls. Head back to Ooty admiring sunset reflections over Wenlock Downs (9th Mile shooting point).",
                        "food_tip": "Savor hot bajjis with Nilgiri masala chai beside Pykara Lake."
                    }
                ],
                "budget_estimate": "₹3,500 - ₹6,000 per person (excluding stay)",
                "travel_tip": "Book Toy Train tickets on IRCTC 30 days in advance. Carry a warm jacket as evenings drop below 12°C."
            }),
            "₹3,500 - ₹6,000"
        ),

        # CHENNAI 2 DAYS
        (
            'Chennai', 2, '2-Day Cultural, Temple & Coastal Chennai Circuit',
            'Explore 1,000 years of Dravidian heritage, colonial bastions, and the world\'s 2nd longest beach.',
            json.dumps({
                "summary": "Immerse in the timeless charm of Madras — majestic temples, classical arts, colonial forts, and mouthwatering street food.",
                "days": [
                    {
                        "day": 1,
                        "title": "Mylapore Spiritual Heritage & Marina Beach Breeze",
                        "morning": "Start at 6:30 AM with darshan at Kapaleeshwarar Temple in Mylapore. Soak in Dravidian architecture and the temple tank. Enjoy traditional Ghee Pongal and Kumbakonam Degree Coffee at Rayar's Mess or Murugan Idli.",
                        "afternoon": "Visit San Thome Basilica, followed by the British era Fort St. George & Museum to inspect cannons and East India Company artifacts.",
                        "evening": "Stroll down Marina Beach around 4:30 PM. Climb the Madras Lighthouse for aerial ocean views, watch local cricket, and relish fiery Nethili fry and Sundal.",
                        "food_tip": "Don't miss authentic Jigarthanda and hot Podi Dosa in Mylapore."
                    },
                    {
                        "day": 2,
                        "title": "Cultural Village & Seaside Dining on ECR",
                        "morning": "Drive down the scenic East Coast Road (ECR) to DakshinaChitra Heritage Museum. Experience live pottery, weaving, and traditional heritage houses.",
                        "afternoon": "Enjoy a fresh seafood coastal lunch at an ECR seaside shack or resort. Visit Guindy National Park or the Government Museum in Egmore.",
                        "evening": "Relax at Besant Nagar (Elliot's) Beach. Watch the sunset near Karl Schmidt Memorial and dine at a rooftop seaside bistro.",
                        "food_tip": "Try Chennai's iconic Murukku Sandwich at Sowcarpet or a hearty Chettinad thali."
                    }
                ],
                "budget_estimate": "₹2,500 - ₹4,500 per person",
                "travel_tip": "Use Chennai Metro and auto-rickshaw apps (Ola/Uber) to navigate peak traffic effortlessly."
            }),
            "₹2,500 - ₹4,500"
        ),

        # KODAIKANAL 2 DAYS
        (
            'Kodaikanal', 2, '2-Day Misty Valleys, Pine Trails & Lake Bliss',
            'The Princess of Hill Stations unveiled — lakes, dramatic pillar rocks, and misty walks.',
            json.dumps({
                "summary": "Rejuvenate among cloud-kissed peaks, eucalyptus breeze, and whispering pine trails in Kodaikanal.",
                "days": [
                    {
                        "day": 1,
                        "title": "Lakeside Cycling, Coaker's Walk & Bryant Park",
                        "morning": "Start your morning with a brisk walk along Coaker's Walk for mist cascading over mountain ridges. Step directly into adjacent Bryant Park for blooming exotic flowers.",
                        "afternoon": "Rent a bicycle or tandem bike and ride around the 5 km perimeter of Kodaikanal Lake. Indulge in warm homemade pasta or Tibetan momos in town.",
                        "evening": "Take a 4:00 PM sunset pedal boat ride across the star-shaped lake. Browse Tibetan market shops for wooden handicrafts and warm shawls.",
                        "food_tip": "Pick up Kodai spicy dark chocolate and fresh pear preserves from local bakers."
                    },
                    {
                        "day": 2,
                        "title": "Pillar Rocks, Pine Woods & Guna Caves",
                        "morning": "Head early to Pillar Rocks to catch the towering 400-foot monoliths before mist fully blankets the gorge. Continue to the mysterious Guna Caves.",
                        "afternoon": "Walk into the iconic Pine Forest, snapping photos under the towering wooden canopies. Enjoy a picnic lunch with freshly roasted sweet corn and hot momos.",
                        "evening": "Drive to Silver Cascade Waterfalls. Stop by the upper lake viewpoint for a final panoramic goodbye snap.",
                        "food_tip": "Sip hot steaming cardamon chai with crispy onion pakodas near Pillar Rocks."
                    }
                ],
                "budget_estimate": "₹3,000 - ₹5,500 per person",
                "travel_tip": "Carry umbrella and sturdy shoes as hill weather changes quickly with sudden rain showers."
            }),
            "₹3,000 - ₹5,500"
        ),

        # MADURAI & RAMESHWARAM 3 DAYS
        (
            'Madurai', 3, '3-Day Spiritual Wonder: Madurai & Rameshwaram Coastal Circuit',
            'Marvel at Meenakshi Amman Temple, cross the Pamban Bridge, and explore the ghost town of Dhanushkodi.',
            json.dumps({
                "summary": "The ultimate cultural & spiritual voyage bridging ancient Pandya royalty with the sacred shores of Rameshwaram.",
                "days": [
                    {
                        "day": 1,
                        "title": "Madurai Temple Grandeur & Royal Palaces",
                        "morning": "Visit Sri Meenakshi Amman Temple at 6:30 AM. Marvel at the Thousand Pillar Hall, musical pillars, and vibrant temple carvings.",
                        "afternoon": "Tour Thirumalai Nayakkar Mahal with its massive white stucco pillars. Relish Madurai's famous Bun Parotta and Kari Dosa for lunch.",
                        "evening": "Witness the mesmerizing night procession (Palliyarai) at Meenakshi Temple at 9:00 PM. Drink chilled Madurai Famous Jigarthanda.",
                        "food_tip": "Must-try: Murugan Idli Shop soft idlis with 4 chutneys and Famous Jigarthanda."
                    },
                    {
                        "day": 2,
                        "title": "Pamban Sea Bridge & Rameshwaram Jyotirlinga",
                        "morning": "Take an early 3-hour morning drive/train to Rameshwaram across the iconic Pamban Sea Bridge over turquoise waters.",
                        "afternoon": "Check in, visit Agniteertham for holy dip, and take the sacred bath at the 22 holy wells (Theerthams) inside Ramanathaswamy Temple.",
                        "evening": "Walk the world's longest pillared temple corridor (1,212 pillars) bathed in evening temple lamps.",
                        "food_tip": "Try hot South Indian banana leaf meals served around the temple streets."
                    },
                    {
                        "day": 3,
                        "title": "Dhanushkodi Land's End & Kalam Memorial",
                        "morning": "Drive to Dhanushkodi and Arichal Munai at sunrise. Witness the meeting point of the Indian Ocean and Bay of Bengal along pristine sandbars.",
                        "afternoon": "Inspect the eerie cyclone ruins of the church and railway station. Visit Dr. APJ Abdul Kalam National Memorial on the return drive.",
                        "evening": "Catch a coastal sunset from the Pamban Road Bridge watching fishing boats glide beneath the rolling railway span.",
                        "food_tip": "Fresh tender coconut and fried sea fish from beachside fishermen shacks."
                    }
                ],
                "budget_estimate": "₹5,000 - ₹9,000 per person",
                "travel_tip": "Wear traditional modest attire for temple entry (dhoti/pant for men, saree/salwar for women)."
            }),
            "₹5,000 - ₹9,000"
        ),

        # PONDICHERRY 2 DAYS
        (
            'Pondicherry', 2, '2-Day Franco-Tamil Heritage, Beaches & Auroville',
            'Savor French pastries, cycle along mustard-yellow White Town, and find peace at Auroville.',
            json.dumps({
                "summary": "Where French colonial elegance meets spiritual Tamil Nadu. Cafes, pristine sands, and tranquil meditation.",
                "days": [
                    {
                        "day": 1,
                        "title": "French Quarter Strolls & Rock Beach Breeze",
                        "morning": "Rent a vintage bicycle and cruise through White Town. Admire colonial villas, bougainvillea gates, and French street signs. Enjoy breakfast at Baker Street or Cafe des Arts.",
                        "afternoon": "Visit Sri Aurobindo Ashram for quiet meditation, then stroll past the French War Memorial.",
                        "evening": "Walk along the pedestrian-only Promenade Beach. Sit by the rocky shoreline, admire the Gandhi Statue, and indulge in wood-fired pizza and gelato.",
                        "food_tip": "Croissants, Ratatouille, and authentic Italian Gelato on Goubert Avenue."
                    },
                    {
                        "day": 2,
                        "title": "Golden Matrimandir & Paradise Beach Sun",
                        "morning": "Drive 12 km to Auroville. Walk through the banyan tree grove and view the awe-inspiring golden Matrimandir sphere.",
                        "afternoon": "Take a short ferry ride through Chunnambar backwaters to the isolated golden sands of Paradise Beach.",
                        "evening": "Enjoy water sports or relax under thatch shacks at Paradise Beach. Return for seaside French-Creole dinner.",
                        "food_tip": "Organic vegan bowls and sourdough treats at Auroville bakery."
                    }
                ],
                "budget_estimate": "₹3,500 - ₹6,500 per person",
                "travel_tip": "Book Matrimandir inner chamber passes at least 3-7 days in advance online."
            }),
            "₹3,500 - ₹6,500"
        )
    ]

    cursor.executemany('''
    INSERT INTO itineraries (city, duration_days, title, description, plan_json, estimated_budget)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', itineraries)

    conn.commit()
    conn.close()
    print("Database tourism.db successfully reseeded with deep-dive place fields!")

if __name__ == '__main__':
    init_db()
