(function() {

    getLastVisit = function (categoryId) {
        const storedVisit = localStorage.getItem("last-visit-" + categoryId);

        return storedVisit != null ? parseInt(storedVisit) : 0;
    };

    $("#sites").on("click", "button.category", function() {
        const buttonNode = $(this);
        // Collapse uses `data-target=#xxxxx`
        const categoryId = buttonNode.data("target").substring(1);

        localStorage.setItem("last-visit-" + categoryId, Date.now());
    });

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

})();