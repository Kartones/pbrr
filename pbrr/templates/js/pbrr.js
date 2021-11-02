// about:config & privacy.file_unique_origin = false for firefox

function initAccordion(element) {
  document.addEventListener('click', function (e) {
    if (!e.target.matches(element + ' .post-button')) {
      return;
    } else {
      e.target.parentElement.classList.toggle('active');
    }
  });
}

function read(setStateFunction) {
  let allFeeds = [];

  fetch('sites.json')
    .then(response => response.json())
    .then(sitesList => Promise.all(sitesList.sites.map(filename => fetch(filename))))
    .then(responses => Promise.all(responses.map(response => response.json())))
    .then(sites => sites.map(site => _parseSite(site, allFeeds)))
    .then(() => _presentData(allFeeds, setStateFunction));
}

function _parseSite(jsonData, allFeeds) {
  Object.entries(jsonData.entries)
    .map(([_, entry]) => ({
      'title': entry.title,
      'date': entry.date,
      'formattedDate': _formattedDate(entry.date),
      'url': entry.url,
      'content': entry.content,
      'site': jsonData.title,
    }))
    .forEach(entry => allFeeds.push(entry));
}

// TODO: rename
function _presentData(allFeeds, setStateFunction) {
  allFeeds.sort((first, second) => second.date > first.date ? 1 : -1);

  if (setStateFunction) {
    setStateFunction(allFeeds);
  } else {
    console.error('Missing setStateFunction() after reading feeds');
  }
}

function _formattedDate(timestamp) {
  const date = new Date(timestamp * 1000);
  return `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()} ${date.getHours()}:${date.getMinutes()}`;
}