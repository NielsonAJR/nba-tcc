library(hoopR) # Banco de Dados
library(tidyverse) # Framework do tidyverse
library(readr)
library(dplyr)


dados_basicos <- nba_leaguedashplayerstats(season = "2025-26", 
                                           per_mode = "Per36", 
                                           measure_type = "Base")$LeagueDashPlayerStats

# A função puxa as informações de Altura e Peso pelo PERSON_ID/PLAYER_ID de cada Jogador

pegar_fisico <- function(id) {
  tryCatch({
    res <- nba_commonplayerinfo(player_id = id)
    df <- res$CommonPlayerInfo %>% dplyr::select(PERSON_ID, HEIGHT, WEIGHT)
    # Adiciona uma pausa para não sobrecarregar a API
    Sys.sleep(0.5) 
    return(df)
  }, error = function(e) {
    cat(sprintf("Erro ou dados não encontrados para o ID: %s\n", id))
    return(NULL) # Retorna NULL para IDs sem dados
  })
}

# Roda para todos os 605 jogadores (isso vai levar alguns minutos)
df_todos_fisicos <- map_dfr(dados_basicos$PLAYER_ID, pegar_fisico, .progress = TRUE)

# Combina os dois bancos criados pelo PLAYER_ID E PERSON_ID
dados_basicos <- left_join(dados_basicos, df_todos_fisicos, by = c("PLAYER_ID" = "PERSON_ID"))


# Função para converter altura (6-8 -> metros)
converter_altura <- function(valor) {
  partes <- as.numeric(unlist(strsplit(valor, "-")))
  # (Pés * 30.48) + (Polegadas * 2.54)
  cm <- (partes[1] * 30.48) + (partes[2] * 2.54)
  return(cm / 100) 
}

# Função para converter peso (lbs -> kg)
converter_peso <- function(lbs) {
  return(lbs * 0.453592)
}

dados_basicos <- dados_basicos |>
  rowwise() |>
  mutate(
    Altura = converter_altura(HEIGHT),
    Peso = converter_peso(as.numeric(WEIGHT))
  )


dados_analise <- dados_basicos |>
  dplyr::select(PLAYER_NAME, TEAM_ABBREVIATION,  GP, AGE, PTS, AST, REB, OREB, DREB, TOV, STL, 
                BLK, FG_PCT, FG3_PCT, FT_PCT, Peso, Altura) |>
  dplyr::mutate(
    Season = 2026,
    Position = case_when(
      PLAYER_NAME %in% c("Trae Young", "Luka Dončić", "Stephen Curry", "Ja Morant", 
                         "LaMelo Ball", "Darius Garland", "Russell Westbrook", 
                         "Dejounte Murray", "James Harden", "Shai Gilgeous-Alexander", 
                         "CJ McCollum", "De'Aaron Fox", "Fred VanVleet", 
                         "Tyrese Maxey", "Jrue Holiday", "Tyrese Haliburton", 
                         "D'Angelo Russell", "Cole Anthony", "Mike Conley", "Chris Paul", 
                         "Kevin Porter Jr.", "Monte Morris", "Spencer Dinwiddie", 
                         "Devonte' Graham", "Immanuel Quickley", "Dennis Schröder", 
                         "Davion Mitchell", "Marcus Smart", "Kyle Lowry", "Kyrie Irving", 
                         "Coby White", "Damian Lillard", "Malcolm Brogdon", "Tyus Jones",
                         "Cameron Payne", "Tre Mann", "Gabe Vincent", "Jalen Suggs", 
                         "Frank Jackson", "Eric Bledsoe", "Patrick Beverley", 
                         "Raul Neto", "Cory Joseph", "Duane Washington Jr.", 
                         "Lonzo Ball", "Killian Hayes", "Ricky Rubio", "Payton Pritchard", 
                         "Kemba Walker", "Tre Jones", "Ish Smith", "Aaron Holiday", 
                         "Theo Maledon", "Lou Williams", "George Hill", "Facundo Campazzo", 
                         "Jose Alvarado", "Derrick Rose", "Brandon Williams", "D.J. Augustin", 
                         "Jevon Carter", "Jordan McLaughlin", "T.J. McConnell", "Trey Burke", 
                         "Saben Lee", "Dennis Smith Jr.", "Dalano Banton", "Trent Forrest", 
                         "Markelle Fultz", "Malachi Flynn", "Rajon Rondo", "Isaiah Thomas", 
                         "Keifer Sykes", "Brandon Goodwin", "Goran Dragic", "Elfrid Payton", 
                         "Kira Lewis Jr.", "Kris Dunn", "David Duke Jr.", "Miles McBride", 
                         "Brad Wanamaker", "Lindell Wigginton", "Justin Robinson", 
                         "Mychal Mulder", "Chris Chiozza", "Javonte Smart", 
                         "Devin Cannady", "Hassani Gravett", "Zavier Simpson",
                         "Kevin Pangos", "Tim Frazier", "Jared Harper", 
                         "Brandon Knight", "Devon Dotson", "Derrick Walton Jr.", 
                         "Jeff Dowtin Jr.", "Tyler Johnson", "Ryan Arcidiacono", 
                         "Cassius Winston", "Myles Powell", "Tremont Waters", 
                         "Malik Newman", "Sharife Cooper", "McKinley Wright IV", 
                         "Darren Collison", "Carlik Jones", "Emmanuel Mudiay", "Tyrell Terry", 
                         "Cat Barber", "JaQuori McLaughlin", "Jaysean Paige", "Ben Simmons", 
                         "Dyson Daniels", "Jacob Gilyard", "Jamal Murray", "Jamaree Bouyea",
                         "Jason Preston", "John Wall", "Kennedy Chandler", "Matthew Dellavedova",
                         "Michael Carter-Williams", "Quenton Jackson", "Ryan Rollins", 
                         "Scotty Pippen Jr.", "Trevor Hudgins", "TyTy Washington Jr.", "Mark Sears", 
                         "Keyonte George", "Scoot Henderson", "Stephon Castle", "Jeremiah Fears",
                         "Alex Morales", "Amen Thompson", "Anthony Black", "Bub Carrington", 
                         "Chucky Hepburn", "Collin Gillespie", "Craig Porter Jr.", "Daniss Jenkins", 
                         "Devin Carter", "Egor Dëmin", "Isaiah Collier", "Isaiah Stevens", 
                         "Jahmir Young", "Jamal Shead", "Javon Small", "KJ Simpson", "Kasparas Jakučionis",
                         "Keaton Wallace", "LJ Cryer", "Marcus Sasser", "Miles Kelly", "Nikola Topić",
                         "Nolan Traore", "Pat Spencer", "RayJ Dennis", "Rob Dillingham", "Ryan Nembhard",
                         "Sean Pedulla", "Tyler Kolek", "Tyrese Proctor", "Tyson Etienne",
                         "Walter Clayton Jr.", "Yuki Kawamura") ~ "PG",
#
      PLAYER_NAME %in% c("Joel Embiid", "Nikola Jokić", "Karl-Anthony Towns", "LeBron James", 
                         "Jonas Valančiūnas", "Nikola Vučević", "Christian Wood", "Bam Adebayo", 
                         "Bobby Portis", "Rudy Gobert", "Kevin Love", "Deandre Ayton", 
                         "Montrezl Harrell", "Anthony Davis", "Jakob Poeltl", "Jarrett Allen", 
                         "Jusuf Nurkić", "Clint Capela", "Ivica Zubac", "Mo Bamba", 
                         "Dwight Powell", "Al Horford", "Alperen Sengun", "JaVale McGee", 
                         "Daniel Gafford", "P.J. Washington", "Precious Achiuwa", "Jaxson Hayes", 
                         "Naz Reid", "Mitchell Robinson", "LaMarcus Aldridge", "Robert Williams III",   
                         "Isaiah Stewart", "Andre Drummond", "Moritz Wagner", "Isaiah Hartenstein", 
                         "Drew Eubanks", "Myles Turner", "Chimezie Metu", "Hassan Whiteside", 
                         "Steven Adams", "Kevon Looney", "Mason Plumlee", "Richaun Holmes", 
                         "Damian Jones", "Willy Hernangomez", "Nemanja Bjelica", "DeMarcus Cousins", 
                         "Dewayne Dedmon", "Nic Claxton", "Onyeka Okongwu", "Daniel Theis", 
                         "Dwight Howard", "Jeremiah Robinson-Earl", "Kelly Olynyk", "Serge Ibaka", 
                         "Blake Griffin", "Goga Bitadze", "Mike Muscala", "Tristan Thompson", 
                         "Omer Yurtseven", "Isaiah Jackson", "Jock Landale", "Robin Lopez", 
                         "Khem Birch", "Alex Len", "Taj Gibson", "Zach Collins", 
                         "Bismack Biyombo", "Derrick Favors", "DeAndre Jordan", "Thomas Bryant", 
                         "Luka Garza", "Moses Brown", "Tony Bradley", "Brook Lopez", 
                         "Gorgui Dieng", "Olivier Sarr", "Nick Richards", "Cody Zeller", 
                         "Enes Freedom", "Killian Tillie", "Paul Reed", "Paul Millsap", 
                         "Boban Marjanovic", "Frank Kaminsky", "Bruno Fernando", "Nerlens Noel", 
                         "Udoka Azubuike", "Greg Monroe", "Charles Bassey", "Neemias Queta", 
                         "Willie Cauley-Stein", "Udonis Haslem", "Luke Kornet", "Ed Davis", 
                         "Kai Jones", "Vernon Carey Jr.", "Marko Simonovic", "Tacko Fall", 
                         "Micah Potter", "Cheick Diallo", "Daniel Oturu", "Norvel Pelle", 
                         "Jordan Bell", "Javin DeLaurier", "Jaime Echenique", "Jay Huff", 
                         "Jon Teske", "Chance Comanche", "Christian Koloko", "Dario Saric",
                         "Jalen Duren", "James Wiseman", "Jaylin Williams", "John Butler Jr.",
                         "Mark Williams", "Meyers Leonard", "Moussa Diabaté", "Noah Vonleh",
                         "Orlando Robinson", "Walker Kessler", "Victor Wembanyama", "Tristan Vukcevic",
                         "Alex Sarr", "Zach Edey", "Adem Bona", "Ariel Hukporti", "Branden Carlson", 
                         "Colin Castleton", "Dereck Lively II", "Derik Queen", "Donovan Clingan",
                         "Duop Reath", "Dylan Cardwell", "Guerschon Yabusele", "Hunter Dickinson", 
                         "Johni Broome", "Kel'el Ware", "Khaman Maluach", "Kyle Filipowski", "Lachlan Olbrich",
                         "Lawson Lovering", "Maxime Raynaud", "Moussa Cisse", "N'Faly Dante", "Oscar Tshiebwe",
                         "Oscar Tshiebwe", "PJ Hall", "Rocco Zikarsky", "Ryan Kalkbrenner",
                         "Trayce Jackson-Davis", "Trey Jemison III", "Vladislav Goldin",
                         "Yang Hansen", "Yanic Konan Niederhäuser", "Yves Missi") ~ "C",
#
      PLAYER_NAME %in% c("DeMar DeRozan", "Giannis Antetokounmpo", "Kevin Durant", "Miles Bridges", 
                         "Pascal Siakam", "Julius Randle", "Jaren Jackson Jr.", "Harrison Barnes", 
                         "Tobias Harris", "Bojan Bogdanovic", "Domantas Sabonis", "Scottie Barnes", 
                         "Kyle Kuzma", "Aaron Gordon", "Evan Mobley", "Kristaps Porziņģis", 
                         "Wendell Carter Jr.", "Carmelo Anthony", "Jae'Sean Tate", "Jerami Grant", 
                         "Dorian Finney-Smith", "John Collins", "Marcus Morris Sr.", "Cameron Johnson", 
                         "Trey Lyles", "Jeff Green", "Danilo Gallinari", "Paul George", 
                         "Darius Bazley", "Herbert Jones", "Georges Niang", "Brandon Clarke", 
                         "Obi Toppin", "Jaden McDaniels", "Jae Crowder", "Chuma Okeke", 
                         "Robert Covington", "Grant Williams", "Doug McDermott", "Marvin Bagley III", 
                         "P.J. Tucker", "Kyle Anderson", "Otto Porter Jr.", "Jarred Vanderbilt", 
                         "Taurean Prince", "Nicolas Batum", "Rui Hachimura", "Jalen Smith", 
                         "Aleksej Pokusevski", "Isaiah Roby", "Rudy Gay", "JaMychal Green", 
                         "Maxi Kleber", "Lamar Stevens", "Draymond Green", "James Johnson", 
                         "Eric Paschall", "Thaddeus Young", "Larry Nance Jr.", "Stanley Johnson", 
                         "Terry Taylor", "Davis Bertans", "Derrick Jones Jr.", "Justise Winslow", 
                         "Zeke Nnaji", "Dean Wade", "Xavier Tillman", "Day'Ron Sharpe", 
                         "Anthony Gill", "Marquese Chriss", "Sandro Mamukelashvili", "Patrick Williams", 
                         "Wenyen Gabriel", "Nathan Knight", "Santi Aldama", "Juancho Hernangomez", 
                         "Markieff Morris", "Ish Wainright", "Gary Clark", "Semi Ojeleye", 
                         "Reggie Perry", "Jericho Sims", "KZ Okpala", "Tyler Cook", 
                         "JT Thor", "Vlatko Čančar", "Mamadi Diakite", "Jabari Parker", 
                         "Jalen Johnson", "Jamorko Pickett", "Usman Garuba", "Devontae Cacok", 
                         "Alize Johnson",  "Bol Bol", "D.J. Wilson", "Chris Silva", 
                         "Freddie Gillespie", "Malik Fitts", "Isaiah Todd", "Gabriel Deck", 
                         "Petr Cornelie", "Sekou Doumbouya", "Juwan Morgan", "Moses Wright", 
                         "Sam Dekker", "Emanuel Terry", "David Roddy", "Deonte Burton",
                         "Dominick Barlow", "Zion Williamson", "Isaiah Mobley", "Jabari Smith Jr.",
                         "Jabari Walker", "Jake LaRavia", "Jamal Cain", "Jarrell Brantley",
                         "Jeremy Sochan", "Jonathan Isaac", "Kenneth Lofton Jr.", "Luka Samanic",
                         "Mfiondu Kabengele", "Michael Foster Jr.", "Nikola Jović", "Ousmane Dieng",
                         "Paolo Banchero", "RaiQuan Gray", "Ron Harper Jr.", "Tari Eason", "Xavier Cooks",
                         "Norchad Omier", "Chet Holmgren", "GG Jackson", "Matas Buzelis",
                         "Olivier-Maxence Prosper", "Amari Williams", "Asa Newell", "Carter Bryant",
                         "Collin Murray-Boyles", "DaRon Holmes II", "Danny Wolf", "Drew Peterson",
                         "Drew Timme", "E.J. Liddell", "Emanuel Miller", "Enrique Freeman", 
                         "Grant Nelson", "Gui Santos", "Hunter Tyson", "Isaac Jones", "Jahmyl Telfort",
                         "Jalen Wilson", "Jarace Walker", "Joan Beringer", "Jonathan Mogbo", "Jordan Walsh",
                         "Josh Oduro", "Julian Reese", "Karlo Matković", "Kobe Brown",
                         "Mouhamadou Gueye", "Mouhamed Gueye", "Noa Essengue", "Noah Clowney",
                         "Oso Ighodaro", "Pete Nance", "Quinten Post", "Rasheer Fleming", 
                         "Nae'Qwan Tomlin", "Skal Labissiere", "Taylor Hendricks",
                         "Tidjane Salaün", "Tolu Smith", "Toumani Camara", "Tyler Smith") ~ "PF",
#
      PLAYER_NAME %in% c("Jayson Tatum", "Jaylen Brown", "RJ Barrett", "Khris Middleton", 
                         "Saddiq Bey", "Keldon Johnson", "Andrew Wiggins", "Brandon Ingram", 
                         "Jimmy Butler III", "Franz Wagner", "Mikal Bridges", "Kelly Oubre Jr.", 
                         "Lauri Markkanen", "Kevin Huerter", "Terance Mann", "Devin Vassell", 
                         "Norman Powell", "OG Anunoby", "Gordon Hayward", "Chris Boucher", 
                         "Justin Holiday", "Max Strus", "De'Andre Hunter", "Cedi Osman", 
                         "KJ Martin", "Deni Avdija", "Josh Giddey", "Jonathan Kuminga", 
                         "Bruce Brown", "Pat Connaughton", "Corey Kispert", "Oshae Brissett", 
                         "Dillon Brooks", "Isaac Okoro", "Reggie Bullock Jr.", "Royce O'Neale", 
                         "Caleb Martin", "Cody Martin", "Torrey Craig", "Ziaire Williams", 
                         "Cam Reddish", "Jordan Nwora", "Javonte Green", "Nassir Little", 
                         "Jeremy Lamb", "Danny Green", "Trendon Watford", "Kenrich Williams", 
                         "Jalen McDaniels", "CJ Elleby", "Keita Bates-Diop", "Trey Murphy III", 
                         "Josh Jackson", "Joe Ingles", "Naji Marshall", "Juan Toscano-Anderson", 
                         "Joshua Primo", "Kessler Edwards", "DeAndre' Bembry", "Troy Brown Jr.", 
                         "Svi Mykhailiuk", "Danuel House Jr.", "David Nwaba", "Timothe Luwawu-Cabarrot", 
                         "Greg Brown III", "Maurice Harkless", "Ignas Brazdeikis", "Aaron Nesmith", 
                         "Thanasis Antetokounmpo", "Kelan Martin", "Yuta Watanabe", "Rodney Hood", 
                         "Joe Harris", "Admiral Schofield", "Kent Bazemore", "Andre Iguodala", 
                         "Isaiah Livers", "Dylan Windler", "Jaylen Hoard", "Justin Anderson", 
                         "Trevor Ariza", "Keljin Blevins", "Kevin Knox II", "Michael Porter Jr.", 
                         "Georgios Kalaitzakis", "Justin Champagnie", "Jake Layman", "Braxton Key", 
                         "Sam Hauser", "Alfonzo McKinnie", "Leandro Bolmaro", "Theo Pinson", 
                         "Louis King", "Haywood Highsmith", "Didi Louzada", "Abdel Nader", 
                         "Paul Watson", "Chaundee Brown Jr.", "James Ennis III", "BJ Johnson", 
                         "Cameron Oliver", "Wes Iwundu", "Justin Jackson", "Aleem Ford", 
                         "Cameron McGriff", "Yves Pons", "Isaac Bonga", "Solomon Hill", 
                         "Eugene Omoruyi", "Robert Woodard II", "Paris Bass", "Trevon Scott", 
                         "Xavier Sneed", "Chandler Hutchison", "Jemerrio Jones", "Matt Ryan", 
                         "Aaron Henry", "George King", "Zylan Cheatham", "Feron Hunt", 
                         "Arnoldas Kulboka", "Anthony Lamb", "AJ Griffin", "Buddy Boeheim",
                         "Caleb Houstan", "Chima Moneke", "Cole Swider", "Darius Days",
                         "Jack White", "Jordan Hall", "Josh Minott", "Julian Champagnie", "Justin Minaya",
                         "Kawhi Leonard", "Keegan Murray", "MarJon Beauchamp", "Patrick Baldwin Jr.", 
                         "Simone Fontecchio", "T.J. Warren", "Tyler Dorsey", "Alex Antetokounmpo", 
                         "Trentyn Flowers", "Brandon Miller", "Brice Sensabaugh", "Cooper Flagg", 
                         "Riley Minix", "Kon Knueppel", "Blake Hinson", "Payton Sandfort", 
                         "Cam Whitmore", "Jaime Jaquez Jr.", "Dariq Whitehead", "Ace Bailey",
                         "Adou Thiero", "Andersson Garcia", "Ausar Thompson", "Bobi Klintman",
                         "CJ Huntley", "Chaney Johnson", "Chris Livingston", "Dalton Knecht", 
                         "David Jones Garcia", "Dillon Jones", "Harrison Ingram", "Hugo González",
                         "Isaiah Crawford", "Jacob Toppin", "Jalen Slawson", "Jamison Battle", 
                         "Jayson Kent", "Jett Howard", "Jordan Miller", "Julian Phillips", 
                         "Justin Edwards", "Keshad Johnson", "Kevin McCullar Jr.", "Kris Murray",
                         "Kyshawn George", "Leaky Black", "Leonard Miller", "Liam McNeeley", 
                         "Malevy Leons", "Mohamed Diawara", "Myron Gardner", "Nigel Hayes-Davis",
                         "Noah Penda", "Ronald Holland II", "Ryan Dunn", "Sidy Cissoko", "Spencer Jones",
                         "Tosan Evbuomwan", "Tristan Enaruna", "Tristan da Silva", "Tyler Burton",
                         "Will Riley", "Zaccharie Risacher") ~ "SF",
#
      PLAYER_NAME %in% c("Devin Booker","Donovan Mitchell", "Zach LaVine", "Anthony Edwards", 
                         "Terry Rozier", "Jordan Poole", "Desmond Bane", "Tyler Herro", 
                         "Jalen Brunson", "Gary Trent Jr.", "Jordan Clarkson", "Buddy Hield", 
                         "Reggie Jackson", "Jalen Green", "Evan Fournier", "Cade Cunningham", 
                         "Malik Monk", "Will Barton", "Kentavious Caldwell-Pope", "Derrick White", 
                         "Anfernee Simons", "Caris LeVert", "Seth Curry", "Malik Beasley", 
                         "Bogdan Bogdanović", "Alec Burks", "Bradley Beal", "Patty Mills", 
                         "Luguentz Dort", "Duncan Robinson", "Lonnie Walker IV", "Luke Kennard", 
                         "Josh Hart", "De'Anthony Melton", "Eric Gordon", "Grayson Allen", 
                         "Chris Duarte", "Bones Hyland", "Nickeil Alexander-Walker", "Ayo Dosunmu", 
                         "Gary Harris", "Josh Richardson", "Bryn Forbes", "Ben McLemore", 
                         "Klay Thompson", "Garrison Mathews", "Hamidou Diallo", "Terrence Ross", 
                         "Amir Coffey", "Tim Hardaway Jr.", "Talen Horton-Tucker", "Josh Christopher", 
                         "Landry Shamet", "Cam Thomas", "Jaylen Nowell", "Furkan Korkmaz", 
                         "Gary Payton II", "R.J. Hampton", "Damion Lee", "Shake Milton", 
                         "Austin Reaves", "Aaron Wiggins", "Austin Rivers", "Avery Bradley", 
                         "Lance Stephenson", "Donte DiVincenzo", "Matisse Thybulle", "John Konchar", 
                         "Brandon Boston", "Delon Wright", "Ty Jerome", "Josh Green", 
                         "Terence Davis", "Garrett Temple", "Alex Caruso", "Armoni Brooks", 
                         "Wayne Ellington", "Quentin Grimes", "Rodney McGruder", "Keon Johnson", 
                         "Wesley Matthews", "Frank Ntilikina", "Moses Moody", "Romeo Langford", 
                         "Davon Reed", "Lindy Waters III", "Isaiah Joe", "Tomas Satoransky", 
                         "Vít Krejčí", "Tony Snell", "Collin Sexton", "Jared Butler", 
                         "Matt Thomas", "Sterling Brown", "James Bouknight", "Josh Okogie", 
                         "Jarrett Culver", "Markus Howard", "Elijah Hughes", "Victor Oladipo", 
                         "PJ Dozier", "Skylar Mays", "Daishen Nix", "Kyle Guy", 
                         "Malcolm Hill", "Denzel Valentine", "Joe Wieskamp", "Jahmi'us Ramsey", 
                         "Xavier Moon", "Cassius Stanley", "Jay Scrubb", "Trevelin Queen", 
                         "Melvin Frazier Jr.", "Quinndary Weatherspoon", "Charlie Brown Jr.", 
                         "Mason Jones", "Sam Merrill", "Carsen Edwards", "Brodric Thomas",
                         "Rayjon Tucker", "Nik Stauskas", "Tyrone Wallace", "Ruben Nembhard Jr.", 
                         "Langston Galloway", "Marcus Garrett", "Gabriel Lundberg", "Gabe York", 
                         "Mac McClung", "Dakota Mathias", "Craig Sword", "Miye Oni",
                         "Jordan Schakel", "Wayne Selden", "Damyean Dotson", "Shaquille Harrison", 
                         "Scotty Hopson", "Rob Edwards", "Deividas Sirvydis", "Joel Ayayi", 
                         "Shaq Buchanan", "Ahmad Caver", "Jarron Cumberland", "DaQuan Jeffries",
                         "Joe Johnson", "Jaylen Morris", "Jaden Springer", "Scottie Lewis", 
                         "Jordan Goodwin", "Tyler Hall", "Nate Hinton", "DeJon Jarreau", 
                         "David Johnson", "CJ Miles", "Matt Mooney", "Ade Murkey", "Trayvon Palmer", 
                         "MJ Walker", "A.J. Lawson", "AJ Green", "Alondes Williams", "Andrew Nembhard",
                         "Bennedict Mathurin", "Blake Wesley", "Bryce McGowens", "Christian Braun", 
                         "Dalen Terry", "Dereon Seabron", "Donovan Williams", "Dru Smith",
                         "Edmond Sumner", "JD Davison", "Jaden Hardy", "Jaden Ivey",
                         "Jalen Williams", "Jared Rhoden", "Johnny Davis", "Johnny Juzang",
                         "Kendall Brown", "Kendrick Nunn", "Keon Ellis", "Kevon Harris", "Kobi Simmons",
                         "Lester Quinones", "Malaki Branham", "Max Christie", "Nate Williams",
                         "Ochai Agbaji", "Peyton Watson", "Shaedon Sharpe", "Stanley Umude",
                         "Trevor Keels", "Tyrese Martin", "Vince Williams Jr.", "Wendell Moore Jr.",
                         "Tristen Newton", "Cormac Ryan", "Zyon Pullin", "Koby Brea", 
                         "Cedric Coward", "AJ Johnson", "Adama Bal", "Ajay Mitchell", "Alijah Martin",
                         "Andre Jackson Jr.", "Antonio Reeves", "Baylor Scheierman", "Ben Saraf",
                         "Ben Sheppard", "Bez Mbeng", "Bilal Coulibaly", "Brandin Podziemski",
                         "Bronny James", "Brooks Barnhizer", "Caleb Love", "Cam Christie", "Cam Spencer",
                         "Cason Wallace", "Chaz Lanier", "Chris Mañon", "Chris Youngblood", 
                         "Colby Jones", "Cody Williams", "Curtis Jones", "Daeqwon Plowden",
                         "Darius Brown", "Drake Powell", "Dylan Harper", "Elijah Harkless",
                         "Ethan Thompson", "Gradey Dick", "Hayden Gray", "Hunter Sallis", 
                         "Ja'Kobe Walter", "Jahmai Mashack", "Jalen Pickett", "Jamir Watkins",
                         "Jared McCain", "Jase Richardson", "Javonte Cooke", "Jaylen Clark", 
                         "Jaylen Wells", "Jaylon Tyson", "John Poulakidas", "John Tonje", 
                         "Johnny Furphy", "Jordan Hawkins", "Julian Strawther", "Kadary Richmond", 
                         "Kam Jones", "Keshon Gilbert", "Kobe Bufkin", "Kobe Sanders", 
                         "Lucas Williamson", "Luke Travers", "Malachi Smith", "Max Shulga",
                         "Micah Peavy", "Nick Smith Jr.", "Nique Clifford", "Pacôme Dadiet",
                         "Pelle Larsson", "Rayan Rupert", "Reed Sheppard", "Sion James",
                         "Taelon Peter", "Terrence Shannon Jr.", "Toby Okani", 
                         "Tre Johnson", "Trey Alexander", "VJ Edgecombe", "Will Richard") ~ "SG",
      TRUE ~ "To_Map" 
    ),
    across(c(PTS, AGE, AST, REB, OREB, DREB ,TOV, BLK, FG_PCT, FG3_PCT, FT_PCT), as.numeric),
    Position = as.factor(Position)
    )


correcoes <- tibble(
  PLAYER_NAME = c("Chris Youngblood", "Jahmyl Telfort", "Jaylen Wells", 
                  "LJ Cryer", "Lawson Lovering", "Tolu Smith"),
  Altura_fix  = c(1.93, 2.01, 2.01, 1.83, 2.13, 2.11),
  Peso_fix    = c(100.24, 99.79, 92.99, 90.72, 106.59, 111.13)
)

dados_analise <- dados_analise |>
  left_join(correcoes, by = "PLAYER_NAME") |>
  mutate(
    Altura = ifelse(is.na(Altura), Altura_fix, Altura),
    Peso   = ifelse(is.na(Peso),   Peso_fix,   Peso)
  ) |>
  dplyr::select(-Altura_fix, -Peso_fix)

# Facilitar carregamentos futuros
dados_analise |> write.csv("data/nba_2026.csv", row.names = FALSE)

