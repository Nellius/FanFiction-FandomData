# FanFiction-FandomData

Make fandom data json files by scaping

- Not crossover: [Anime/Manga](https://www.fanfiction.net/anime/), [Books](https://www.fanfiction.net/book/), [Cartoons](https://www.fanfiction.net/cartoon/), [Comics](https://www.fanfiction.net/comic/), [Games](https://www.fanfiction.net/game/), [Misc](https://www.fanfiction.net/misc/), [Plays](https://www.fanfiction.net/play/), [Movies](https://www.fanfiction.net/movie/), [TV](https://www.fanfiction.net/tv/)
- Crossover: [Anime/Manga](https://www.fanfiction.net/crossovers/anime/), [Books](https://www.fanfiction.net/crossovers/book/), [Cartoons](https://www.fanfiction.net/crossovers/cartoon/), [Comics](https://www.fanfiction.net/crossovers/comic/), [Games](https://www.fanfiction.net/crossovers/game/), [Misc](https://www.fanfiction.net/crossovers/misc/), [Plays](https://www.fanfiction.net/crossovers/play/), [Movies](https://www.fanfiction.net/crossovers/movie/), [TV](https://www.fanfiction.net/crossovers/tv/)

## Execute

```bash
# python 3.7.4
git clone git@github.com:Nellius/FanFiction-FandomData.git
cd Fanfiction-FandomData
# requirements
pip install undetected_chromedriver bs4 lxml
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
