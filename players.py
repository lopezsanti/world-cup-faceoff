"""
players.py

Hardcoded squad reference data for the 32 nations competing at the
2026 FIFA World Cup (USA / Canada / Mexico), including each team's
flag emoji, confederation, and five star players with their current
(2025-2026 season) club affiliations and approximate senior caps.
"""

# England's flag has no standalone regional-indicator emoji (it is a UK
# subdivision), so it is built from the standard Unicode tag sequence.
ENGLAND_FLAG = "\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F"


SQUAD_DATA = {
    "USA": {
        "flag_emoji": "🇺🇸",
        "confederation": "CONCACAF",
        "star_players": [
            {"name": "Christian Pulisic", "position": "Forward", "club": "AC Milan", "caps": 76},
            {"name": "Weston McKennie", "position": "Midfielder", "club": "Juventus", "caps": 58},
            {"name": "Tyler Adams", "position": "Midfielder", "club": "Bournemouth", "caps": 41},
            {"name": "Sergiño Dest", "position": "Defender", "club": "PSV Eindhoven", "caps": 38},
            {"name": "Folarin Balogun", "position": "Forward", "club": "AS Monaco", "caps": 19},
        ],
    },
    "Canada": {
        "flag_emoji": "🇨🇦",
        "confederation": "CONCACAF",
        "star_players": [
            {"name": "Alphonso Davies", "position": "Defender", "club": "Bayern Munich", "caps": 61},
            {"name": "Jonathan David", "position": "Forward", "club": "Juventus", "caps": 65},
            {"name": "Stephen Eustáquio", "position": "Midfielder", "club": "FC Porto", "caps": 49},
            {"name": "Tajon Buchanan", "position": "Midfielder", "club": "Villarreal", "caps": 44},
            {"name": "Cyle Larin", "position": "Forward", "club": "Real Mallorca", "caps": 70},
        ],
    },
    "Mexico": {
        "flag_emoji": "🇲🇽",
        "confederation": "CONCACAF",
        "star_players": [
            {"name": "Santiago Giménez", "position": "Forward", "club": "AC Milan", "caps": 35},
            {"name": "Edson Álvarez", "position": "Midfielder", "club": "West Ham United", "caps": 76},
            {"name": "Raúl Jiménez", "position": "Forward", "club": "Fulham", "caps": 95},
            {"name": "Hirving Lozano", "position": "Forward", "club": "San Diego FC", "caps": 80},
            {"name": "Julián Quiñones", "position": "Forward", "club": "Club América", "caps": 22},
        ],
    },
    "Argentina": {
        "flag_emoji": "🇦🇷",
        "confederation": "CONMEBOL",
        "star_players": [
            {"name": "Lionel Messi", "position": "Forward", "club": "Inter Miami", "caps": 191},
            {"name": "Julián Álvarez", "position": "Forward", "club": "Atlético Madrid", "caps": 45},
            {"name": "Lautaro Martínez", "position": "Forward", "club": "Inter Milan", "caps": 75},
            {"name": "Enzo Fernández", "position": "Midfielder", "club": "Chelsea", "caps": 41},
            {"name": "Rodrigo De Paul", "position": "Midfielder", "club": "Atlético Madrid", "caps": 80},
        ],
    },
    "Brazil": {
        "flag_emoji": "🇧🇷",
        "confederation": "CONMEBOL",
        "star_players": [
            {"name": "Vinícius Júnior", "position": "Forward", "club": "Real Madrid", "caps": 41},
            {"name": "Rodrygo", "position": "Forward", "club": "Real Madrid", "caps": 38},
            {"name": "Endrick", "position": "Forward", "club": "Real Madrid", "caps": 14},
            {"name": "Raphinha", "position": "Forward", "club": "FC Barcelona", "caps": 36},
            {"name": "Casemiro", "position": "Midfielder", "club": "Manchester United", "caps": 75},
        ],
    },
    "France": {
        "flag_emoji": "🇫🇷",
        "confederation": "UEFA",
        "star_players": [
            {"name": "Kylian Mbappé", "position": "Forward", "club": "Real Madrid", "caps": 90},
            {"name": "Ousmane Dembélé", "position": "Forward", "club": "Paris Saint-Germain", "caps": 49},
            {"name": "Aurélien Tchouaméni", "position": "Midfielder", "club": "Real Madrid", "caps": 36},
            {"name": "Antoine Griezmann", "position": "Forward", "club": "Atlético Madrid", "caps": 137},
            {"name": "Mike Maignan", "position": "Goalkeeper", "club": "AC Milan", "caps": 27},
        ],
    },
    "England": {
        "flag_emoji": ENGLAND_FLAG,
        "confederation": "UEFA",
        "star_players": [
            {"name": "Jude Bellingham", "position": "Midfielder", "club": "Real Madrid", "caps": 41},
            {"name": "Harry Kane", "position": "Forward", "club": "Bayern Munich", "caps": 106},
            {"name": "Phil Foden", "position": "Midfielder", "club": "Manchester City", "caps": 41},
            {"name": "Bukayo Saka", "position": "Forward", "club": "Arsenal", "caps": 45},
            {"name": "Declan Rice", "position": "Midfielder", "club": "Arsenal", "caps": 60},
        ],
    },
    "Germany": {
        "flag_emoji": "🇩🇪",
        "confederation": "UEFA",
        "star_players": [
            {"name": "Jamal Musiala", "position": "Midfielder", "club": "Bayern Munich", "caps": 38},
            {"name": "Florian Wirtz", "position": "Midfielder", "club": "Liverpool", "caps": 33},
            {"name": "Kai Havertz", "position": "Forward", "club": "Arsenal", "caps": 51},
            {"name": "Joshua Kimmich", "position": "Midfielder", "club": "Bayern Munich", "caps": 100},
            {"name": "Niclas Füllkrug", "position": "Forward", "club": "Borussia Dortmund", "caps": 26},
        ],
    },
    "Spain": {
        "flag_emoji": "🇪🇸",
        "confederation": "UEFA",
        "star_players": [
            {"name": "Lamine Yamal", "position": "Forward", "club": "FC Barcelona", "caps": 35},
            {"name": "Pedri", "position": "Midfielder", "club": "FC Barcelona", "caps": 45},
            {"name": "Rodri", "position": "Midfielder", "club": "Manchester City", "caps": 60},
            {"name": "Nico Williams", "position": "Forward", "club": "Athletic Bilbao", "caps": 33},
            {"name": "Álvaro Morata", "position": "Forward", "club": "AC Milan", "caps": 84},
        ],
    },
    "Portugal": {
        "flag_emoji": "🇵🇹",
        "confederation": "UEFA",
        "star_players": [
            {"name": "Cristiano Ronaldo", "position": "Forward", "club": "Al-Nassr", "caps": 219},
            {"name": "Bruno Fernandes", "position": "Midfielder", "club": "Manchester United", "caps": 86},
            {"name": "Bernardo Silva", "position": "Midfielder", "club": "Manchester City", "caps": 95},
            {"name": "Rafael Leão", "position": "Forward", "club": "AC Milan", "caps": 38},
            {"name": "João Cancelo", "position": "Defender", "club": "Al-Hilal", "caps": 60},
        ],
    },
    "Netherlands": {
        "flag_emoji": "🇳🇱",
        "confederation": "UEFA",
        "star_players": [
            {"name": "Virgil van Dijk", "position": "Defender", "club": "Liverpool", "caps": 86},
            {"name": "Cody Gakpo", "position": "Forward", "club": "Liverpool", "caps": 43},
            {"name": "Frenkie de Jong", "position": "Midfielder", "club": "FC Barcelona", "caps": 68},
            {"name": "Xavi Simons", "position": "Midfielder", "club": "RB Leipzig", "caps": 32},
            {"name": "Memphis Depay", "position": "Forward", "club": "Corinthians", "caps": 102},
        ],
    },
    "Belgium": {
        "flag_emoji": "🇧🇪",
        "confederation": "UEFA",
        "star_players": [
            {"name": "Kevin De Bruyne", "position": "Midfielder", "club": "Napoli", "caps": 106},
            {"name": "Romelu Lukaku", "position": "Forward", "club": "Napoli", "caps": 117},
            {"name": "Jeremy Doku", "position": "Forward", "club": "Manchester City", "caps": 31},
            {"name": "Amadou Onana", "position": "Midfielder", "club": "Aston Villa", "caps": 27},
            {"name": "Youri Tielemans", "position": "Midfielder", "club": "Aston Villa", "caps": 75},
        ],
    },
    "Croatia": {
        "flag_emoji": "🇭🇷",
        "confederation": "UEFA",
        "star_players": [
            {"name": "Luka Modrić", "position": "Midfielder", "club": "AC Milan", "caps": 184},
            {"name": "Joško Gvardiol", "position": "Defender", "club": "Manchester City", "caps": 42},
            {"name": "Mateo Kovačić", "position": "Midfielder", "club": "Manchester City", "caps": 100},
            {"name": "Marcelo Brozović", "position": "Midfielder", "club": "Al-Nassr", "caps": 95},
            {"name": "Ivan Perišić", "position": "Forward", "club": "PSV Eindhoven", "caps": 145},
        ],
    },
    "Switzerland": {
        "flag_emoji": "🇨🇭",
        "confederation": "UEFA",
        "star_players": [
            {"name": "Granit Xhaka", "position": "Midfielder", "club": "Bayer Leverkusen", "caps": 134},
            {"name": "Manuel Akanji", "position": "Defender", "club": "Manchester City", "caps": 64},
            {"name": "Breel Embolo", "position": "Forward", "club": "AS Monaco", "caps": 70},
            {"name": "Ruben Vargas", "position": "Forward", "club": "Bayer Leverkusen", "caps": 48},
            {"name": "Yann Sommer", "position": "Goalkeeper", "club": "Inter Milan", "caps": 95},
        ],
    },
    "Uruguay": {
        "flag_emoji": "🇺🇾",
        "confederation": "CONMEBOL",
        "star_players": [
            {"name": "Federico Valverde", "position": "Midfielder", "club": "Real Madrid", "caps": 73},
            {"name": "Darwin Núñez", "position": "Forward", "club": "Al-Hilal", "caps": 47},
            {"name": "Ronald Araújo", "position": "Defender", "club": "FC Barcelona", "caps": 42},
            {"name": "Manuel Ugarte", "position": "Midfielder", "club": "Manchester United", "caps": 35},
            {"name": "Facundo Pellistri", "position": "Forward", "club": "Manchester United", "caps": 30},
        ],
    },
    "Colombia": {
        "flag_emoji": "🇨🇴",
        "confederation": "CONMEBOL",
        "star_players": [
            {"name": "James Rodríguez", "position": "Midfielder", "club": "León", "caps": 110},
            {"name": "Luis Díaz", "position": "Forward", "club": "Bayern Munich", "caps": 65},
            {"name": "Jhon Arias", "position": "Midfielder", "club": "Wolverhampton Wanderers", "caps": 33},
            {"name": "Davinson Sánchez", "position": "Defender", "club": "Galatasaray", "caps": 75},
            {"name": "Rafael Santos Borré", "position": "Forward", "club": "Werder Bremen", "caps": 50},
        ],
    },
    "Ecuador": {
        "flag_emoji": "🇪🇨",
        "confederation": "CONMEBOL",
        "star_players": [
            {"name": "Moisés Caicedo", "position": "Midfielder", "club": "Chelsea", "caps": 40},
            {"name": "Piero Hincapié", "position": "Defender", "club": "Bayer Leverkusen", "caps": 38},
            {"name": "Pervis Estupiñán", "position": "Defender", "club": "Brighton & Hove Albion", "caps": 45},
            {"name": "Kendry Páez", "position": "Midfielder", "club": "Strasbourg", "caps": 15},
            {"name": "Enner Valencia", "position": "Forward", "club": "Internacional", "caps": 95},
        ],
    },
    "Chile": {
        "flag_emoji": "🇨🇱",
        "confederation": "CONMEBOL",
        "star_players": [
            {"name": "Alexis Sánchez", "position": "Forward", "club": "Udinese", "caps": 173},
            {"name": "Arturo Vidal", "position": "Midfielder", "club": "Colo-Colo", "caps": 150},
            {"name": "Ben Brereton Díaz", "position": "Forward", "club": "Real Betis", "caps": 35},
            {"name": "Gabriel Suazo", "position": "Defender", "club": "Toulouse FC", "caps": 40},
            {"name": "Claudio Bravo", "position": "Goalkeeper", "club": "Real Betis", "caps": 148},
        ],
    },
    "Senegal": {
        "flag_emoji": "🇸🇳",
        "confederation": "CAF",
        "star_players": [
            {"name": "Sadio Mané", "position": "Forward", "club": "Al-Nassr", "caps": 110},
            {"name": "Kalidou Koulibaly", "position": "Defender", "club": "Al-Hilal", "caps": 88},
            {"name": "Édouard Mendy", "position": "Goalkeeper", "club": "Al-Ahli", "caps": 45},
            {"name": "Nicolas Jackson", "position": "Forward", "club": "Chelsea", "caps": 22},
            {"name": "Ismaïla Sarr", "position": "Forward", "club": "Crystal Palace", "caps": 65},
        ],
    },
    "Morocco": {
        "flag_emoji": "🇲🇦",
        "confederation": "CAF",
        "star_players": [
            {"name": "Achraf Hakimi", "position": "Defender", "club": "Paris Saint-Germain", "caps": 75},
            {"name": "Youssef En-Nesyri", "position": "Forward", "club": "Al-Hilal", "caps": 70},
            {"name": "Sofyan Amrabat", "position": "Midfielder", "club": "Fenerbahçe", "caps": 60},
            {"name": "Hakim Ziyech", "position": "Forward", "club": "Galatasaray", "caps": 65},
            {"name": "Yassine Bounou", "position": "Goalkeeper", "club": "Al-Hilal", "caps": 55},
        ],
    },
    "Nigeria": {
        "flag_emoji": "🇳🇬",
        "confederation": "CAF",
        "star_players": [
            {"name": "Victor Osimhen", "position": "Forward", "club": "Galatasaray", "caps": 35},
            {"name": "Ademola Lookman", "position": "Forward", "club": "Atalanta", "caps": 30},
            {"name": "Wilfred Ndidi", "position": "Midfielder", "club": "Besiktas", "caps": 64},
            {"name": "Samuel Chukwueze", "position": "Forward", "club": "AC Milan", "caps": 38},
            {"name": "Alex Iwobi", "position": "Midfielder", "club": "Fulham", "caps": 60},
        ],
    },
    "Cameroon": {
        "flag_emoji": "🇨🇲",
        "confederation": "CAF",
        "star_players": [
            {"name": "André-Frank Zambo Anguissa", "position": "Midfielder", "club": "Napoli", "caps": 55},
            {"name": "Bryan Mbeumo", "position": "Forward", "club": "Manchester United", "caps": 24},
            {"name": "Vincent Aboubakar", "position": "Forward", "club": "Al-Qadsiah", "caps": 95},
            {"name": "Eric Maxim Choupo-Moting", "position": "Forward", "club": "FC Bayern Munich", "caps": 78},
            {"name": "Christopher Wooh", "position": "Defender", "club": "Stade Rennais", "caps": 28},
        ],
    },
    "Ghana": {
        "flag_emoji": "🇬🇭",
        "confederation": "CAF",
        "star_players": [
            {"name": "Mohammed Kudus", "position": "Forward", "club": "Tottenham Hotspur", "caps": 41},
            {"name": "Thomas Partey", "position": "Midfielder", "club": "Villarreal", "caps": 55},
            {"name": "Jordan Ayew", "position": "Forward", "club": "Leicester City", "caps": 110},
            {"name": "Antoine Semenyo", "position": "Forward", "club": "Bournemouth", "caps": 25},
            {"name": "Iñaki Williams", "position": "Forward", "club": "Athletic Bilbao", "caps": 32},
        ],
    },
    "South Africa": {
        "flag_emoji": "🇿🇦",
        "confederation": "CAF",
        "star_players": [
            {"name": "Percy Tau", "position": "Forward", "club": "Al-Ahly", "caps": 75},
            {"name": "Lyle Foster", "position": "Forward", "club": "Burnley", "caps": 28},
            {"name": "Teboho Mokoena", "position": "Midfielder", "club": "Mamelodi Sundowns", "caps": 35},
            {"name": "Ronwen Williams", "position": "Goalkeeper", "club": "Mamelodi Sundowns", "caps": 50},
            {"name": "Evidence Makgopa", "position": "Forward", "club": "Orlando Pirates", "caps": 18},
        ],
    },
    "Japan": {
        "flag_emoji": "🇯🇵",
        "confederation": "AFC",
        "star_players": [
            {"name": "Takefusa Kubo", "position": "Forward", "club": "Real Sociedad", "caps": 55},
            {"name": "Kaoru Mitoma", "position": "Forward", "club": "Brighton & Hove Albion", "caps": 40},
            {"name": "Wataru Endo", "position": "Midfielder", "club": "Liverpool", "caps": 70},
            {"name": "Ritsu Doan", "position": "Forward", "club": "SC Freiburg", "caps": 60},
            {"name": "Ao Tanaka", "position": "Midfielder", "club": "Leeds United", "caps": 35},
        ],
    },
    "South Korea": {
        "flag_emoji": "🇰🇷",
        "confederation": "AFC",
        "star_players": [
            {"name": "Son Heung-min", "position": "Forward", "club": "LAFC", "caps": 134},
            {"name": "Lee Kang-in", "position": "Midfielder", "club": "Paris Saint-Germain", "caps": 45},
            {"name": "Kim Min-jae", "position": "Defender", "club": "Bayern Munich", "caps": 70},
            {"name": "Hwang Hee-chan", "position": "Forward", "club": "Wolverhampton Wanderers", "caps": 65},
            {"name": "Cho Gue-sung", "position": "Forward", "club": "Mainz 05", "caps": 30},
        ],
    },
    "Australia": {
        "flag_emoji": "🇦🇺",
        "confederation": "AFC",
        "star_players": [
            {"name": "Jackson Irvine", "position": "Midfielder", "club": "St. Pauli", "caps": 75},
            {"name": "Riley McGree", "position": "Midfielder", "club": "Middlesbrough", "caps": 35},
            {"name": "Craig Goodwin", "position": "Forward", "club": "Sparta Rotterdam", "caps": 45},
            {"name": "Mathew Ryan", "position": "Goalkeeper", "club": "Real Sociedad", "caps": 95},
            {"name": "Mitchell Duke", "position": "Forward", "club": "Fagiano Okayama", "caps": 50},
        ],
    },
    "Iran": {
        "flag_emoji": "🇮🇷",
        "confederation": "AFC",
        "star_players": [
            {"name": "Mehdi Taremi", "position": "Forward", "club": "Inter Milan", "caps": 90},
            {"name": "Sardar Azmoun", "position": "Forward", "club": "AS Roma", "caps": 80},
            {"name": "Alireza Jahanbakhsh", "position": "Forward", "club": "Feyenoord", "caps": 70},
            {"name": "Saman Ghoddos", "position": "Midfielder", "club": "Al-Sadd", "caps": 55},
            {"name": "Ali Gholizadeh", "position": "Forward", "club": "Charleroi", "caps": 50},
        ],
    },
    "Saudi Arabia": {
        "flag_emoji": "🇸🇦",
        "confederation": "AFC",
        "star_players": [
            {"name": "Salem Al-Dawsari", "position": "Forward", "club": "Al-Hilal", "caps": 95},
            {"name": "Saleh Al-Shehri", "position": "Forward", "club": "Al-Hilal", "caps": 45},
            {"name": "Firas Al-Buraikan", "position": "Forward", "club": "Al-Ahli", "caps": 40},
            {"name": "Abdullah Al-Hamdan", "position": "Forward", "club": "Al-Hilal", "caps": 25},
            {"name": "Nawaf Al-Abid", "position": "Midfielder", "club": "Al-Ittihad", "caps": 30},
        ],
    },
    "Qatar": {
        "flag_emoji": "🇶🇦",
        "confederation": "AFC",
        "star_players": [
            {"name": "Akram Afif", "position": "Forward", "club": "Al-Sadd", "caps": 100},
            {"name": "Almoez Ali", "position": "Forward", "club": "Al-Duhail", "caps": 95},
            {"name": "Hassan Al-Haydos", "position": "Midfielder", "club": "Al-Sadd", "caps": 175},
            {"name": "Boualem Khoukhi", "position": "Defender", "club": "Al-Sadd", "caps": 110},
            {"name": "Pedro Miguel", "position": "Defender", "club": "Al-Sadd", "caps": 60},
        ],
    },
    "New Zealand": {
        "flag_emoji": "🇳🇿",
        "confederation": "OFC",
        "star_players": [
            {"name": "Chris Wood", "position": "Forward", "club": "Nottingham Forest", "caps": 90},
            {"name": "Liberato Cacace", "position": "Defender", "club": "Empoli", "caps": 30},
            {"name": "Joe Bell", "position": "Midfielder", "club": "Standard Liège", "caps": 35},
            {"name": "Sarpreet Singh", "position": "Midfielder", "club": "SV Sandhausen", "caps": 28},
            {"name": "Marko Stamenić", "position": "Midfielder", "club": "Red Star Belgrade", "caps": 20},
        ],
    },
    "Egypt": {
        "flag_emoji": "🇪🇬",
        "confederation": "CAF",
        "star_players": [
            {"name": "Mohamed Salah", "position": "Forward", "club": "Liverpool", "caps": 105},
            {"name": "Omar Marmoush", "position": "Forward", "club": "Manchester City", "caps": 28},
            {"name": "Mohamed Elneny", "position": "Midfielder", "club": "Arsenal", "caps": 100},
            {"name": "Mostafa Mohamed", "position": "Forward", "club": "FC Nantes", "caps": 35},
            {"name": "Zizo", "position": "Forward", "club": "Zamalek SC", "caps": 30},
        ],
    },
}


def get_player_data(team_name):
    """Return the squad dict for team_name, or None if the team is not found."""
    if not isinstance(team_name, str):
        return None

    if team_name in SQUAD_DATA:
        return SQUAD_DATA[team_name]

    normalized = team_name.strip().lower()
    for name, data in SQUAD_DATA.items():
        if name.lower() == normalized:
            return data

    return None


def get_flag(team_name):
    """Return the flag emoji for team_name, or None if the team is not found."""
    data = get_player_data(team_name)
    return data["flag_emoji"] if data else None


def get_all_wc_teams():
    """Return a sorted list of all team names present in SQUAD_DATA."""
    return sorted(SQUAD_DATA.keys())
