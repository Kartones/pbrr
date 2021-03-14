(function() {

    getLastVisit = function (categoryId) {
        const storedVisit = localStorage.getItem("last-visit-" + categoryId);

        return storedVisit != null ? parseInt(storedVisit) : 0;
    };

    $("#sites").find("span.last-update-date").each(function() {
        let spanNode = $(this);
        let parentDivNode = spanNode.parent().parent();
        const categoryId = parentDivNode[0].id;

        if (spanNode.data("ts") <= getLastVisit(categoryId)) {
            spanNode.hide();
        } else {
            parentDivNode.collapse("show");
        }
    });

    $("#sites").on("click", "button.category", function() {
        const buttonNode = $(this);
        // Collapse uses `data-target=#xxxxx`
        const categoryId = buttonNode.data("target").substring(1);

        // inside the target `div`, there's an `a` per site, with a children `span` with the `data-ts` we want
        let timestamps = $(buttonNode.data("target")).children()
                    .map(function() {
                        return $(this).children().data("ts");
                    })
                    // sort in reverse order
                    .sort((a, b) => b - a);

        // If possible, store the ts of the last post, to be more precise
        if (timestamps.length > 0 && timestamps[0] > 0) {
            localStorage.setItem("last-visit-" + categoryId, timestamps[0]);
        } else {
            localStorage.setItem("last-visit-" + categoryId, Date.now());
        }
    });

})();