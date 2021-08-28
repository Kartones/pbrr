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

    function readFeedData(feedId) {
        const currentData = localStorage.getItem(feedId);
        return new Set(currentData ? currentData.split(",") : []);
    }

    function markPostViewed(postId, feedId) {
        let currentReadEntriesOnly;
        let currentData = readFeedData(feedId);
        currentData.add(postId);

        const currentEntriesRaw = document.getElementById(feedId).dataset.currentEntries;
        // server retrieved no data, so can't cleanup
        if (currentEntriesRaw.length > 0) {
            // "Garbage Collect" past read entries, as no longer relevant
            const currentEntries = currentEntriesRaw.split(",");
            currentReadEntriesOnly = Array.from(currentData).filter(entry => currentEntries.includes(entry));
        } else {
            currentReadEntriesOnly = Array.from(currentData);
        }

        localStorage.setItem(feedId, currentReadEntriesOnly.join(","));
    }

    // On page load
    up.compiler("nav", function() {
        $("#sites").find("span.last-update-date").each(function() {
            const spanNode = $(this);
            const feedNode = spanNode.parent();
            const parentDivNode = feedNode.parent();

            // If server returned no data, will come empty
            const currentEntries =
                feedNode[0].dataset.currentEntries.length > 0 ? feedNode[0].dataset.currentEntries.split(",") : [];
            const currentReadEntries = readFeedData(feedNode[0].id);

            if (currentEntries.length === 0 || currentReadEntries.size >= currentEntries.length) {
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

        if (currentReadEntries.size >= entries.length) {
            document.getElementById(feedId)
                    .getElementsByClassName("last-update-date")[0]
                    .classList
                    .add("hidden");
        }
    });
})();