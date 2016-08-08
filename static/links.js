$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    updater.start();
});

var updater = {
    socket: null,
    link: 1,

    start: function() {
        var url = "ws://" + location.host + "/linksocket";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            json = JSON.parse(event.data);
            switch (json.message) {
                case "link":
                    updater.showMessage(json.content);
                    break;
                case "done":
                    $("#navbar").slideDown();
                    break;
                case "export":
                    saveAs(new Blob([json.content], {type: json.type}), json.name, true);
                    break;
            }
        };
        $("#json").click(function(event) {
            updater.socket.send("json");
        });
        $("#csv").click(function(event) {
            updater.socket.send("csv");
        });
        $("#md").click(function(event) {
            updater.socket.send("md");
        });
        $("#html").click(function(event) {
            updater.socket.send("html");
        });
    },

    showMessage: function(message) {
        var node = $(message);
        node.hide();
        $("#container").append(node);
        node.slideDown();
        updater.link++;
        $("#num").text(updater.link);
    }
};
