-- THIS SCRIPT HAS BEEN MODIFIED TO WORK WITH SQLITE. SQLITELY MODIFIED, IF YOU WILL.

-- Who owns the various regions. In reality, this needs to be at crag level.
CREATE TABLE owners (
    owner_id INT AUTO_INCREMENT,
    owner_name  VARCHAR(64) NOT NULL,
    PRIMARY KEY (owner_id)
);

-- The regional locations of places to climb. Typically, this dictates where you park.
CREATE TABLE regions (
    region_id       INT AUTO_INCREMENT,
    region_name     VARCHAR(64),
    owner_id        INT DEFAULT 2, -- USFS more restrictive than RRGCC, encourages developer caution.
    PRIMARY KEY (region_id),
    FOREIGN KEY (owner_id) REFERENCES owners (owner_id) ON DELETE RESTRICT
);

-- Currently, no support for "sectors" i.e., "Bird Cage" is it's own crag.
CREATE TABLE crags (
    crag_id         INT AUTO_INCREMENT,
    crag_name       VARCHAR(64),
    region_id       INT,
    crag_approach   TEXT,
    PRIMARY KEY (crag_id),
    FOREIGN KEY (region_id) REFERENCES regions (region_id) ON DELETE NO ACTION -- Remove closed crags without deleting Route info; restore it if/when they open up
);

-- Systematize the grading scheme so that the DB can compare difficulties.
CREATE TABLE climb_grades (
    grade_id    INT AUTO_INCREMENT,
    grade_str   CHAR(5),
    PRIMARY KEY (grade_id)
);

CREATE TABLE climbs (
    climb_id                INT AUTO_INCREMENT,
    climb_name              VARCHAR(80) DEFAULT 'Open Project',
    grade_id                INT,
    crag_id                 INT,
    climb_len_ft            INT CHECK (climb_len_ft > 0), -- Climbs must not be stupidly short.
    climb_first_ascent_date DATE DEFAULT CURRENT_TIMESTAMP,
    climb_established_date  DATE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (climb_id),
    FOREIGN KEY (crag_id) REFERENCES crags (crag_id) ON DELETE NO ACTION,
    FOREIGN KEY (grade_id) REFERENCES climb_grades (grade_id) ON DELETE RESTRICT 
);

-- This is the subset table.
CREATE TABLE sport_climbs (
    climb_id            INT AUTO_INCREMENT,
    sport_climb_bolts   INT,
    PRIMARY KEY (climb_id),
    FOREIGN KEY (climb_id) REFERENCES climbs (climb_id) ON DELETE RESTRICT
);

-- Another subset table for traditional climbs.
CREATE TABLE trad_climbs (
    climb_id            INT AUTO_INCREMENT,
    trad_climb_descent CHECK( trad_climb_descent IN ('rap from tree', 'walk off', 'rap rings')), -- Do as I say, not as I do.
    PRIMARY KEY (climb_id),
    FOREIGN KEY (climb_id) REFERENCES climbs (climb_id) ON DELETE RESTRICT
);



-- Create some views for convenience.
CREATE VIEW sport_climbs_view AS 
SELECT * 
  FROM climbs 
       INNER JOIN sport_climbs
       USING (climb_id); 

CREATE VIEW trad_climbs_view AS 
SELECT * 
  FROM climbs 
       NATURAL JOIN trad_climbs; -- Do as I say, not as I do.

CREATE VIEW mixed_climbs_view AS 
SELECT * FROM climbs 
         NATURAL JOIN sport_climbs 
         NATURAL JOIN trad_climbs;

-- If you're curious.
-- DESCRIBE sport_climbs_view;
-- DESCRIBE trad_climbs_view;

-- Store information about individual humans on the climbing scene, as climbers, developers.
CREATE TABLE climbers (
    climber_id              INT AUTO_INCREMENT,
    climber_first_name      VARCHAR(32),
    climber_last_name       VARCHAR(32),
    climber_email           VARCHAR(128) UNIQUE,
    climber_forum_handle    VARCHAR(32) UNIQUE, -- Website username.
    PRIMARY KEY (climber_id)
);

-- Relate climbers to the routes that they were the first to climb. FAs may consist of multiple people.
CREATE TABLE climber_first_ascents (
    climb_id            INT NOT NULL,
    climber_id          INT NOT NULL,   -- No NULLs; if you don't know who made the FA, don't include them in this table.
    PRIMARY KEY (climb_id, climber_id),
    FOREIGN KEY (climber_id) REFERENCES climbers (climber_id) ON DELETE NO ACTION,
    FOREIGN KEY (climb_id) REFERENCES climbs (climb_id) ON DELETE NO ACTION
);

-- Relate climbers to the routes that they established. Multiple names may be related to each climb.
CREATE TABLE climber_climbs_established (
    climb_id        INT NOT NULL,
    climber_id      INT NOT NULL,
    PRIMARY KEY (climb_id, climber_id),
    FOREIGN KEY (climb_id) REFERENCES climbs (climb_id) ON DELETE NO ACTION,
    FOREIGN KEY (climber_id) REFERENCES climbers (climber_id) ON DELETE NO ACTION
);


-- Populate the grades table with the needlessly complex grading scheme 
INSERT INTO climb_grades (grade_str, grade_id)
VALUES ('5.0',  1), -- 1
       ('5.1',  2), -- 2
       ('5.2',  3), -- 3
       ('5.3',  4), -- ...
       ('5.4',  5),
       ('5.5',  6),
       ('5.6',  7),
       ('5.7',  8),
       ('5.8',  9),
       ('5.9',  10),
       ('5.10',     11),
       ('5.10a',    12),
       ('5.10b',    13),
       ('5.10c',    14),
       ('5.10d',    15),
       ('5.11',     16),
       ('5.11a',    17),
       ('5.11b',    18),
       ('5.11c',    19),
       ('5.11d',    20),
       ('5.12',     21),
       ('5.12a',    22),
       ('5.12b',    23),
       ('5.12c',    24),
       ('5.12d',    25),
       ('5.13',     26),
       ('5.13a',    27),
       ('5.13b',    28),
       ('5.13c',    29),
       ('5.13d',    30),
       ('5.14',     31),
       ('5.14a',    32),
       ('5.14b',    33),
       ('5.14c',    34),
       ('5.14d',    35),
       ('5.15',     36),
       ('5.15a',    37),
       ('5.15b',    38),
       ('5.15c',    39),
       ('5.15d',    40);


-- Populate owners table with preliminary list.
INSERT INTO owners (owner_name, owner_id)
VALUES ('Red River Gorge Climbers Coalition', 1),  -- 1
       ('United States Forest Service', 2),        -- 2
       ('John and Elizabeth Muir', 3),             -- 3
       ('Other Private Ownership', 4);             -- 4


-- Populate regions list with current regions list.
INSERT INTO regions (region_id, region_name, owner_id)
VALUES ( 1, 'Muir Valley',              3),
       ( 2, 'Gray''s Branch Region',    2),
       ( 3, 'Lower Gorge Region',       2),
       ( 4, 'Northern Gorge Region',    2),
       ( 5, 'Middle Gorge Region',      2),
       ( 6, 'Upper Gorge Region',       2),
       ( 7, 'Eastern Gorge Region',     2),
       ( 8, 'Tunnel Ridge Road Region', 2),
       ( 9, 'Natural Bridge Region',    2),
       (10, 'Southern Region',          1),
       (11, 'Miller Fork',              2),
       (12, 'Foxtown',                  4);


-- Populate climbers with some climbers.
-- Randomly generated names, with automatically generated emails, and manually-added usernames.
INSERT INTO climbers (
    climber_first_name, 
    climber_last_name, 
    climber_email, 
    climber_forum_handle,
    climber_id)
VALUES  ('Unknown', '', NULL, NULL, 1),                                                -- 1
        ('Rob', 'McFall', 'robby_mcfall@yahoo.com', 'mcfallyall', 2),                  -- 2
        ('Jane', 'Doe', 'jane.doe@domain.com', 'OhDeerMe', 3),                         -- 3
        ('Buddy', 'Everett', 'buddy_everett@hotmail.com', 'bud', 4),                   -- 4
        ('Freeman', 'Barron', 'freeman_barron@hotmail.com', 'not_morgan_freeman', 5),  -- 5
        ('Leroy', 'Neal', 'leroy_neal@hotmail.com', 'leroyw', 6),      -- 6
        ('Arlie', 'Wagner', 'arlie_wagner@hotmail.com', 'arliew', 7),      -- 7
        ('Ora', 'Crosby', 'ora_crosby@hotmail.com', 'orca', 8),        -- 8
        ('Alonso', 'Snyder', 'alonso_snyder@gmail.com', 'mr_pretzel', 9),      -- 9
        ('Jack', 'Clarke', 'jack_clarke@yahoo.com', 'jackc', 10),       -- 10 
        ('Gail', 'Becker', 'gail_becker@gmail.com', 'beckerg', 11),     -- 11
        ('Audra', 'Shaw', 'audra_shaw@yahoo.com', 'audras', 12),        -- 12
        ('Janette', 'Hoover', 'janette_hoover@gmail.com', 'Janie', 13),     -- 13
        ('Veronica', 'Turner', 'veronica_turner@hotmail.com', 'Vicky', 14),     -- 14
        ('Wilson', 'Rhodes', 'wilson_rhodes@gmail.com', 'Wiiiiillllllssooonnn', 15),        -- 15
        ('Louisa', 'Lowery', 'louisa_lowery@gmail.com', 'lou', 16),     -- 16
        ('Benito', 'Vang', 'benito_vang@yahoo.com', 'benny', 17),       -- 17
        ('Lucien', 'Kane', 'lucien_kane@hotmail.com', 'mr_fox', 18),        -- 18
        ('Werner', 'Ibarra', 'werner_ibarra@gmail.com', 'von_braun', 19),       -- 19
        ('Sang', 'Lutz', 'sang_lutz@yahoo.com', 'singsong', 20),        -- 20
        ('Dick', 'Moss', 'dick_moss@gmail.com', '*censored*', 21),      -- 21
        ('Christie', 'Dillon', 'christie_dillon@gmail.com', 'caberet_player', 22),      -- 22
        ('Erin', 'Frye', 'erin_frye@yahoo.com', 'ErinF', 23),       -- 23
        ('Clark', 'Griffith', 'clark_griffith@hotmail.com', 'griff', 24),       -- 24
        ('Sheryl', 'Pierce', 'sheryl_pierce@yahoo.com', 'she', 25),     -- 25
        ('Lee', 'Sampson', 'lee_sampson@yahoo.com', 'le_me', 26),       -- 26
        ('Carroll', 'Moody', 'carroll_moody@gmail.com', 'mr_moody', 27),        -- 27
        ('Solomon', 'Atkinson', 'solomon_atkinson@gmail.com', 'not_rowan', 28),     -- 28
        ('Isidro', 'Shepard', 'isidro_shepard@yahoo.com', 'izzy', 29),      -- 29
        ('Lon', 'Bond', 'lon_bond@yahoo.com', 'Mr_Bond', 30),       -- 30
        ('Kasey', 'Reid', 'kasey_reid@gmail.com', 'ka_re', 31),     -- 31
        ('Tom', 'Landry', 'tom_landry@gmail.com', 't-land', 32),        -- 32
        ('Mildred', 'Ho', 'mildred_ho@hotmail.com', 'millie', 33),      -- 33
        ('Lacy', 'Mckinney', 'lacy_mckinney@hotmail.com', 'l_mckin', 34),       -- 34
        ('Donn', 'Houston', 'donn_houston@gmail.com', 'tx_don', 35),        -- 35
        ('Candace', 'Sellers', 'candace_sellers@yahoo.com', 'not_buying', 36),      -- 36
        ('Ernie', 'Caldwell', 'ernie_caldwell@gmail.com', 'still_missing_bert', 37),        -- 37
        ('Kirsten', 'Conway', 'kirsten_conway@yahoo.com', 'con_woman', 38),     -- 38
        ('Alyson', 'Herrera', 'alyson_herrera@hotmail.com', 'allie', 39),       -- 39
        ('Shad', 'Freeman', 'shad_freeman@gmail.com', 's_free', 40),        -- 40
        ('Ebony', 'Joyce', 'ebony_joyce@hotmail.com', 'darkly_joyous', 41),     -- 41
        ('Max', 'House', 'max_house@hotmail.com', 'min_mouse', 42),     -- 42
        ('Mandy', 'Hall', 'mandy_hall@yahoo.com', 'dandy_mall', 43),        -- 43
        ('Olivia', 'Snow', 'olivia_snow@gmail.com', 'ollie', 44),       -- 44
        ('Ed', 'Moyer', 'ed_moyer@yahoo.com', 'ed', 45),        -- 45
        ('Becky', 'Chaney', 'becky_chaney@hotmail.com', 'becks', 46),       -- 46
        ('Brant', 'Sharp', 'brant_sharp@gmail.com', 'dull_boy', 47),        -- 47
        ('Tamra', 'Hartman', 'tamra_hartman@hotmail.com', 'hearty', 48),        -- 48
        ('Jesse', 'Cross', 'jesse_cross@gmail.com', 'jess_c', 49),      -- 49
        ('Luke', 'Heath', 'luke_heath@hotmail.com', 'luke_h', 50),      -- 50
        ('Lance', 'Berg', 'lance_berg@hotmail.com', 'lanceburger', 51),     -- 51
        ('Melody', 'Richards', 'melody_richards@yahoo.com', 'tuning_standby', 52),      -- 52
        ('Kara', 'Myers', 'kara_myers@yahoo.com', 'kara_m', 53),        -- 53
        ('Art', 'Cammers', 'art.cammers@aol.com', 'caribe', 54),        -- 54
        ('Jeff', 'Castro', 'jeff.castro@gmail.com', 'jeffy', 55),                       -- 55
        ('Jared', 'Hancock', 'hcjared@gmail.com', 'jare_bear', 56),                     -- 56
        ('Skip', 'Wolfe', 'wolf_pack@ahyoo.com', 'wolf_pack', 57),                      -- 57
        ('Mark', 'Ryan', 'mry@aol.com', 'mr_ryan', 58);                                 -- 58

-- Populate the crags table with two regions's worth.
INSERT INTO crags (crag_id, crag_name, region_id) 
VALUES (  1, 'Animal Crackers Wall',            1),
       (  2, 'The Arsenal',                     1),
       (  3, 'Bibliothek',                      1),
       (  4, 'The Boneyard',                    1),
       (  5, 'The Bowling Alley',               1),
       (  6, 'Bruisebrothers Wall',             1),
       (  7, 'Coyote Cliff',                    1),
       (  8, 'The Fire Wall',                   1),
       (  9, 'Great Arch',                      1),
       (  10, 'Great Wall',                      1),
       (  11, 'Guide Wall',                      1),
       (  12, 'The Hideout',                     1),
       (  13, 'Indy Wall',                       1),
       (  14, 'Inner Sanctum',                   1),
       (  15, 'Ivory Tower',                     1),
       (  16, 'Land Before Time Wall',           1),
       (  17, 'Midnight Surf',                   1),
       (  18, 'Persepolis',                      1),
       (  19, 'Practice Wall',                   1),
       (  20, 'The Sanctuary',                   1),
       (  21, 'Shawnee Shelter',                 1),
       (  22, 'Slab City',                       1),
       (  23, 'Solarium',                        1),
       (  24, 'South Side',                      1),
       (  25, 'The Stadium',                     1),
       (  26, 'The Stronghold',                  1),
       (  27, 'Sunbeam Buttress',                1),
       (  28, 'Sunnyside',                       1),
       (  29, 'Tectonic Wall and Johnny''s Wall',1),
       (  30, 'Washboard Wall',                  1);
INSERT INTO crags (crag_id, crag_name, region_id)
VALUES (  31, 'Alcatraz',                     11),
       (  32, 'Camelot',                      11),
       (  33, 'Chaos',                        11),
       (  34, 'Cloud 9',                      11),
       (  35, 'Cooper''s Cove',               11),
       (  36, 'Corner Pocket',                11),
       (  37, 'Deep End',                     11),
       (  38, 'Fruit Wall',                   11),
       (  39, 'Graveyard',                    11),
       (  40, 'The Hal Garner Memorial Crag', 11),
       (  41, 'Highlands',                    11),
       (  42, 'The Infirmary',                11),
       (  43, 'The Laboratory',               11),
       (  44, 'Monastery',                    11),
       (  45, 'The Morgue',                   11),
       (  46, 'The Nursery',                  11),
       (  47, 'The Pharmacy',                 11),
       (  48, 'The Portal',                   11),
       (  49, 'Rando Crag',                   11),
       (  50, 'Real Deep End',                11),
       (  51, 'The Record Shop',              11),
       (  52, 'Sanitarium',                   11),
       (  53, 'Scotch Wall',                  11),
       (  54, 'Secret Garden',                11),
       (  55, 'Serenity Point',               11),
       (  56, 'Vine Wall',                    11);

    --   More Crags that need 
    --    Adena Wall
    --    Alcatraz
    --    Animal Crackers
    --    Area 6
    --    Asylum
    --    Auxier Ridge
    --    Backside Wall
    --    Bald Rock Cove
    --    Bear Wollor Hollor
    --    Bee Branch Rock
    --    Beer Trailer Crag
    --    Between Wall
    --    Bibliothek
    --    Blackburn Rock
    --    Board Wall
    --    Bob Marley Crag
    --    Brighton Wall
    --    Bronaugh Wall
    --    Bruisbrothers Wall
    --    Buzzard Ridge
    --    Buzzard's Roost
    --    Camelot
    --    Camp Store Crag
    --    Chaos
    --    Chica Bonita Wall
    --    Chimney Top
    --    Clearcut Wall
    --    Cloud 9
    --    Coffin Ridge
    --    Cooper's Cover
    --    Corner Pocket
    --    Courtesy Wall
    --    Courthouse Rock
    --    Coyote Cliff
    --    Curbside
    --    D. Boone Hut Crag
    --    Deep End
    --    Dip Wall
    --    Doorish Wall
    --    Double Arch
    --    Drive-By Crag
    --    Drop Out Wall
    --    Dunkan Rock
    --    Eagle Point Buttress
    --    Eastern Sky Bridge Ridge
    --    Fortress Wall
    --    Friction Slab
    --    Fruit Wall
    --    Funk Rock City
    --    Gladie Rock
    --    Graveyard
    --    Grays Wall
    --    Great Arch
    --    Great Wall
    --    Guide Wall
    --    Half Moon
    --    Haystack Rock
    --    Hen's Nest
    --    Highlands
    --    Historic Wall
    --    Hole in the Wall
    --    Indian Creek Crag
    --    Indy Wall
    --    Inner Sanctum
    --    Ivory Tower
    --    Jailhouse Rock
    --    Jazz Rock
    --    Jewel Pinnacle
    --    Lady Slipper - Emerald City
    --    Lady Slipper - Global Village
    --    Land Before Time Wall
    --    Left Field
    --    Left Flank
    --    Long Wall
    --    Lost Ridge
    --    Lower Sky Bridge Ridge
    --    Lower Small Wall
    --    Lumpy Wall
    --    Mariba Fork
    --    McCow Pasture
    --    Middle Small Wall
    --    Midnight Surf
    --    Millitary Wall
    --    Minas Tirith
    --    Monastery
    --    Moonshiner's Wall
    --    Mt. Olive Rock
    --    Muscle Beach
    --    Neverland
    --    North 40
    --    Oil Crack Rock
    --    Pebble Beach
    --    Pepper Wall
    --    Persepolis
    --    Phantasia
    --    Pinch-em Tight Ridge
    --    Pistol Ridge
    --    Practice Wall
    --    Princess Arch
    --    Proving Grounds
    --    Purgatory
    --    Purple Valley
    --    Quarry Rock
    --    Rando Crag
    --    Raven Rock
    --    Real Deep End
    --    Rival Wall
    --    Roadside Crag
    --    Rough Trailer
    --    Salt Wall
    --    Sanitarium
    --    Sassafras Rock
    --    Scotch Wall
    --    Secret Garden
    --    See Rocks
    --    Serenity Point
    --    Shady Grove
    --    Shawnee Shelter
    --    Sheltowee Wall
    --    Sky Bridge
    --    Slab City
    --    Solar Collector and Gold Coast
    --    Solarium
    --    Soul Canyon
    --    South Park
    --    South Side
    --    Spring Wall
    --    Staircase Wall
    --    Star Gap Arch Area
    --    Sunbeam Buttress
    --    Sunnyside
    --    Symphony Wall
    --    Tarr Ridge
    --    Technotnic Wall and Johnny's Wall
    --    Teeth Buttress
    --    The Arena
    --    The Arsenal
    --    The Bear's Den
    --    The Boneyard
    --    The Bowling Alley
    --    The Bright Side
    --    The Chocolate Factory





-- Populate the climbs table with some routes!
INSERT INTO climbs (climb_id, climb_name, grade_id, crag_id, climb_len_ft, climb_first_ascent_date, climb_established_date)
    VALUES ( 1, 'Grand Bohemian',       12, 44, 70, '2004-1-1', '1998-9-2'),-- 1 sport
           ( 2, 'Nomad',                12, 44, 75, '2013-1-1', NULL),      -- 2 sport
           ( 3, 'Mission Creep',        11, 44, 60, NULL, '     2013-1-1'), -- 3 sport
           ( 4, 'The Heretic',           8, 44, 45, NULL,       NULL),      -- 4 trad
           ( 5, 'Spork',                11, 44, 70, NULL,       NULL),      -- 5 mixed route, with elements of sport AND trad.
           ( 6, 'Vagabond',             12, 44, 65, NULL,       '2013-1-1'),-- 6 
           ( 7, 'Parajna',              12, 44, 50, NULL,       NULL),      -- 7
           ( 8, 'Licifer''s Unicycle',  10, 44, 60, '2014-1-1', '2014-1-1'),-- 8
           ( 9, 'Choss Gully Wrangling', 8, 44, 80, NULL,       NULL),      -- 9
           (10, 'Return to Balance',    11, 22, 50, '2005-1-1', '2003-8-2'),-- 10
           (11, 'Child of the Earth',   12, 22, 60, NULL,       NULL),      -- 11
           (12, 'Sacred Stones',        11,	22, 65, NULL,       NULL),      -- 12
           (13, 'Go West',	             7,	22, 70, NULL,       NULL),      -- 13 trad
           (14, 'Flash Point',          12,	22, 45, NULL,       NULL),      -- 14 trad
           (15, 'Strip the Willows',    11, 22, 80, NULL,       NULL),      -- 15
           (16, 'Thrillbillies',        10,	22, 90, NULL,       NULL),      -- 16
           (17, 'Iron Lung',            12, 22, 50, NULL,       NULL),      -- 17
           (18, 'Narcissus',            13, 44, 40, '2014-1-1', '2013-1-1');-- 18

INSERT INTO sport_climbs (climb_id, sport_climb_bolts)
    VALUES ( 1, 10), -- Grand Bohemian has 10 bolts,
           ( 5,  4), -- Spork has 4 bolts.
           (10,  5),
           (11,  6),
           (12,  7),
           (15,  8),
           (16,  9),
           (17,  6);

INSERT INTO trad_climbs (climb_id, trad_climb_descent)
    VALUES ( 4, 'rap rings'),      -- The Heretic has a bolt anchor to descend on.
           ( 5, 'rap rings'),      -- Spork has a bolt anchor to descend on.
           (13, 'rap rings'),
           (14, 'rap rings');


INSERT INTO climber_first_ascents (climber_id, climb_id)
    VALUES (2, 1),
           (2, 2),
           (54, 8),
           (55, 8),
           (56, 10),
           (57, 10),
           (58, 10),
           (54, 18),
           (55, 18);

-- TODO: Move estab dates to climbs INSERT.
INSERT INTO climber_climbs_established (climb_id, climber_id)
    VALUES ( 1,  1),
           (10,  1),
           ( 8, 54),
           ( 3,  2),
           ( 6,  2),
           (18, 54),
           (18, 55);

-- Q: Can we insert into a view? 
-- A: "Can not modify more than one base table through a join view"

-- Include logic for the complicated process that is adding a new route.
-- SOURCE logic/add_new_climb.sql;

-- Include example statements, some of which define views.
-- SOURCE examples/example_queries.sql;
-- SOURCE examples/having_example.sql;
-- SOURCE examples/home_page_table.sql;
-- SOURCE examples/monastery_hist_query.sql;
-- SOURCE examples/name_to_climber_id.sql;

-- Comments have to be EXACTLY THIS FORMAT FOR MY SILLY REFORMATTING TOOL TO WORK.
-- Two dashes, one space, SOURCE ...

	