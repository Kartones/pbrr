(function() {

    const lastVisit = (function () {
        const storedVisit = localStorage.getItem("last-visit");

        localStorage.setItem("last-visit", Date.now());

        return storedVisit != null ? parseInt(storedVisit) : 0;
    })();

    $("#sites").find("span.last-update-date").each(function() {
        if ($(this).data("ts") < lastVisit) {
            $(this).hide();
        }
    });

})();