(function() {

    $(document).keydown(function(e) {
        if (e.keyCode === 37) {
            const goBackButton = document.getElementById("button-go-back");
            if (goBackButton !== null) {
                goBackButton.click();
            }
        }
    });

    $("#feed-content").on("click", "a.list-group-item", function () {
        markPostViewed(this.id, this.dataset.parentId);
    });

    $("#sites").on("click", "a.action-mark-all-read", function () {
        markAllPostsViewed(this.dataset.parentId);
    });

    function readFeedData(feedId) {
        const currentData = localStorage.getItem(feedId);
        return new Set(currentData ? currentData.split(",") : []);
    }

    function garbageCollectOldEntries(feedId, currentData) {
        let currentReadEntriesOnly;

        const currentEntriesRaw = document.getElementById(feedId).dataset.currentEntries;
        if (currentEntriesRaw.length > 0) {
            // "Garbage Collect" past read entries, as no longer relevant
            const currentEntries = currentEntriesRaw.split(",");
            currentReadEntriesOnly = Array.from(currentData).filter(entry => currentEntries.includes(entry));
        } else {
            // server retrieved no data, so can't cleanup
            currentReadEntriesOnly = Array.from(currentData);
        }

        return currentReadEntriesOnly;
    }

    function markAllPostsViewed(feedId) {
        let currentData = readFeedData(feedId);

        document.querySelectorAll(`a.list-group-item[data-parent-id="${feedId}"]`).forEach(entry => {
            currentData.add(entry.id);
        });

        const currentReadEntriesOnly = garbageCollectOldEntries(feedId, currentData);

        localStorage.setItem(feedId, currentReadEntriesOnly.join(","));
    }

    function markPostViewed(postId, feedId) {
        let currentData = readFeedData(feedId);

        currentData.add(postId);

        const currentReadEntriesOnly = garbageCollectOldEntries(feedId, currentData);

        localStorage.setItem(feedId, currentReadEntriesOnly.join(","));
    }

    // On page load
    up.compiler("nav", function() {
        $("#sites").find("span.last-update-date").each(function() {
            const spanNode = $(this);
            const feedNode = spanNode.parent();
            const parentDivNode = feedNode.parent().parent;

            // If server returned no data, will come empty
            const currentEntries =
                feedNode[0].dataset.currentEntries.length > 0 ? feedNode[0].dataset.currentEntries.split(",") : [];
            const currentReadEntries = readFeedData(feedNode[0].id);

            // No data returned from server, or no new entries
            if (currentEntries.length === 0
                || currentEntries.filter(entry => !currentReadEntries.has(entry)).length === 0) {
                spanNode.hide();
            } else {
                parentDivNode.collapse("show");
            }
        });
    });

    // On page load, and on each site's feed loading
    up.compiler("article", function(element) {
        if (element.children.length === 0) {
            return;
        }

        // <article> -> <div> -> [ <a> ]
        const entries = element.children[0].children;

        const feedId = entries[0].dataset.parentId;
        const currentReadEntries = readFeedData(feedId);

        for (child of entries) {
            if (currentReadEntries.has(child.id)) {
                document.getElementById(child.id)
                        .getElementsByClassName("publish-date")[0]
                        .classList
                        .add("hidden");
            }
        }

        if (entries.filter(entry => !currentReadEntries.has(entry)).length === 0) {
            document.getElementById(feedId)
                    .getElementsByClassName("last-update-date")[0]
                    .classList
                    .add("hidden");
        }
    });
})();