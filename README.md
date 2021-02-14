# PBRR - Pretty Basic RSS Reader

## Intro

Building a simple RSS reader that fetches feeds from an OPML file and generates a simple html hierarchy with the posts grouped per site.

No complex website intentions, just cron-based runs dumping new entries, not even deleting old ones (list will anyway only reflect latest N items). Keep minimum state.

## Setup

Just need Docker, but to setup without containers:
```
pip3 install -r /code/requirements.txt
```

For now, hardcoded to search for `subscriptions.xml` OPML file under a `feeds/` folder relative to execution path.

## Running

From the outside:
```
make run
```

Without Docker:
```
python3 run.py
```

Root `index.html` with lists of sites will be placed at `feeds/index.html` once finished fetching.

## Development

```
make shell
python3 run.py
```

## Testing

*Here be dragons*

For the time being, no intention of adding tests to the project.

## TODOs

- move templates to html files under `templates/`
- add bootstrap and some minimalistic css.
- add colors to terminal and homogenize format of errors, etc.
- extract categories from opml, tag each site with them (maybe good for next point of settings file), css accordion to expand-contract each category
- Need to store a json file with at least basic settings: key sitename, value dict with time of last fetch (for headers)
- probably also interesting to put into settings file opml xml filename and reduce path dependencies to just data path
- Proper headers like modified-after, etc.
- Check which site field to use for `Site.last_updated`, some sites lie, others don't have it.
- Seen a few feeds that output the xml as a file, see if can handle easily via feedparser
- Seen a feed that throws 403 because of `ddos-guard`
- run mypy on pre-commit if possible

## License

See [LICENSE](LICENSE).
