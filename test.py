from fuzzywuzzy import fuzz
from pprint import pprint

song = 'SILENT SIREN - ぐるぐるワンダーランド'
text = 'Silent siren - ぐるぐるワンダーランド'

print(fuzz.token_set_ratio(song,text))
