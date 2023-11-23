const COLORS = [
  "#0066cc",
  "#f887ff",
  "#66cc33",
  "#990099",
  "#ff9900",
  "#3366cc",
  "#cc3300",
  "#339966",
  "#cc0099",
  "#ff6600",
  "#6699cc",
  "#cc0066",
  "#009999",
  "#ff3300",
  "#336699",
  "#cc9900",
  "#006699",
  "#ff3366",
  "#339999",
  "#ffcc00",
  "#003366",
  "#cc6633",
  "#99cc00",
  "#ffcc33",
  "#006666",
  "#cc6600",
  "#66cc00",
  "#ff9933",
  "#006633",
  "#cc9966",
  "#339933",
  "#ccff00",
  "#003366",
  "#ff6633",
  "#336600",
  "#ccff33",
  "#003300",
  "#ffcc66",
  "#3F2476",
  "#ef4b92",
  "#003333",
  "#ff6666",
  "#339900",
  "#ccff66",
  "#003322",
  "#ff9999",
  "#66cc66",
  "#ff99cc",
  "#003311",
  "#cc6666",
  "#33cc66",
  "#dc0000",
  "#003300",
  "#ff6666",
  "#66cc99",
  "#cc99ff",
  "#003322",
  "#ff6699",
  "#339966",
  "#cc66cc",
];

// Hex-based
const COLOR_OPACITY = 40;

let siteColorMap = {};

function calculateColor(site) {
  site = site.toLowerCase();

  const index = site
    .split("")
    .map((char) => char.charCodeAt(0))
    .reduce((acc, value) => acc + value, 0);
  return index % COLORS.length;
}

function colorForSite(site) {
  site = site.toLowerCase();

  if (!siteColorMap[site]) {
    siteColorMap[site] = calculateColor(site);
  }
  return COLORS[siteColorMap[site]];
}

function initAccordion(element) {
  document.addEventListener("click", function (e) {
    if (!e.target.matches(element + " .post-button")) {
      return;
    } else {
      e.target.parentElement.classList.toggle("active");
    }
  });
}

function read(setStateFunction) {
  const timestampMark = Date.now();
  let allFeeds = [];

  fetch(`sites.json?t=${timestampMark}`)
    .then((response) => response.json())
    .then((sitesList) =>
      Promise.all(
        sitesList.sites.map((filename) =>
          fetch(`${filename}?t=${timestampMark}`)
        )
      )
    )
    .then((responses) =>
      Promise.all(responses.map((response) => response.json()))
    )
    .then((sites) => sites.map((site) => _parseSite(site, allFeeds)))
    .then(() => _onDataReady(allFeeds, setStateFunction));
}

function _parseSite(jsonData, allFeeds) {
  Object.entries(jsonData.entries)
    .map(([_, entry]) => ({
      title: entry.title,
      date: entry.date,
      formattedDate: _formattedDate(entry.date),
      url: entry.url,
      content: entry.content,
      site: jsonData.title,
      site_category: jsonData.category,
      site_category_icon: jsonData.category_icon,
    }))
    .forEach((entry) => allFeeds.push(entry));
}

function _onDataReady(allFeeds, setStateFunction) {
  allFeeds.sort((first, second) => (second.date > first.date ? 1 : -1));

  if (setStateFunction) {
    setStateFunction(allFeeds);
  } else {
    console.error("Missing setStateFunction() after reading feeds");
  }
}

function _zeroPadded(value) {
  return value < 10 ? `0${value}` : `${value}`;
}

function _formattedDate(timestamp) {
  const date = new Date(timestamp * 1000);

  return `${_zeroPadded(date.getDate())}/${_zeroPadded(
    date.getMonth() + 1
  )}/${date.getFullYear()} ${_zeroPadded(date.getHours())}:${_zeroPadded(
    date.getMinutes()
  )}`;
}
