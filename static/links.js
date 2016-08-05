$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    updater.start();
});

var updater = {
    socket: null,

    start: function() {
        var url = "ws://" + location.host + "/linksocket";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            updater.showMessage(event.data);
        };
    },

    showMessage: function(message) {
        var node = $(message);
        node.hide();
        $("#container").append(node);
        node.slideDown();
    }
};
