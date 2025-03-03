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

  fetch(`last-updated.json?t=${timestampMark}`)
    .then((response) => response.json())
    .then((lastUpdated) => {
      const lastUpdatedElement = document.getElementById("last-updated");
      if (lastUpdatedElement) {
        lastUpdatedElement.innerHTML = _formattedDate(lastUpdated.timestamp);
      }
    })
    .catch((error) => {
      console.error("Error fetching last-updated.json", error);
    });
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
