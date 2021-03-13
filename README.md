# PBRR - Pretty Basic RSS Reader

## Intro

Building a simple RSS reader that fetches feeds from an OPML file and generates a simple html hierarchy with the posts grouped per site and category (if the OPML file had categories).

No intention of building any complex website, just cron-based runs dumping new entries, not even deleting old ones (list will anyway only reflect latest N items). Keep minimum state.

Here's how it looks:

![PBRR screenshot](doc/screenshot.png)

If a feed/site has no news (returns an http 304), it will keep the existing list of posts.

It uses `localStorage` to keep track of your last visit and display/hide the latest post timestamp badge on the site name. Not very advanced at the moment but decent enough to see new posts.

## Setup

Just need Docker, but to setup without containers:
```
pip3 install -r /code/requirements.txt
```

## Running

From the outside:
```
make run
```

Without Docker:
```
python3 run.py feeds subscriptions.xml
```

Root `index.html` with lists of sites will be placed at `feeds/index.html` once finished fetching.

Also, a `settings.json` file will be generated. Inside it, you can add urls to the skip urls setting (e.g. if a feed is not working with PBRR). It's a list of strings, you can manually add new entries, for example `"https://site-to-skip.test"`.

## Development

```
make shell
python3 run.py feeds subscriptions.xml
```

Uses:
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/), because makes parsing HTML and XML way more pleasant
- [Bootstrap 3](https://getbootstrap.com/docs/3.4/), because my CSS skills equal to `null`
- [feedparser](https://feedparser.readthedocs.io) for easier handling of feeds, and yet, they keep causing headaches
- [Unpoly](https://unpoly.com/) for AJAX, because you don't always need React

## Testing

*Here be dragons*

For the time being, no intention of adding tests to the project.

## TODOs

- run mypy on pre-commit if possible

## License

See [LICENSE](LICENSE).
