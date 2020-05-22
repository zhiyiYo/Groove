import json
with open('Data\\initProfile.json') as f:
    profile = json.load(f)
profile['isFirstTimeToRun'] = False
with open('Data\\initProfile.json','w') as f:
    json.dump(profile, f)
    

