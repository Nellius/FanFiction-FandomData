# FanFiction-FandomData

Make fandom data json files

## Execute

```bash
# python 3.7.4
git clone git@github.com:Nellius/FanFiction-FandomData.git
cd Fanfiction-FandomData
# requirements
pip install requests bs4 lxml
# run
python make_fandom_data.py
```

## JSON files

### fandom.json

Fandom database divided by section. It has the same structure as the layout of Fanfiction.net.

### unified-fandom.json

Unified fandom database sorted by fandom name.

### exceptional-fandom.json

Crossover fandom database which name contain ' & '. For [Fanfiction.net: Filter and Sorter](https://github.com/Nellius/UserScripts/tree/master/Fanfiction.net-Filter-and-Sorter).
