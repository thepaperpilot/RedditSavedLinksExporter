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
                case "start":
                    $("#loadbar").slideUp();
                    $("#progressbar").slideDown();
                    break;
                case "link":
                    updater.showMessage(json.content);
                    break;
                case "done":
                    $("#progressbar").slideUp();
                    $("#navbar").slideDown();
                    break;
                case "export":
                    saveAs(new Blob([json.content], {type: json.type}), json.name, true);
                    break;
                case "remove":
                    $("#" + json.content).remove();
                    break;
            }
        };
        $("#load_oauth").click(function(event) {
            updater.socket.send('{"message": "load_oauth"}');
        });
        $("#load_json").click(function(event) {
            event.preventDefault();
            $("#file").trigger('click');
        });
        $("#file").change(function(event) {
            var reader = new FileReader();
            reader.onload = function() {
                updater.socket.send('{"message": "load_json","content": ' + this.result + '}');
            };
            reader.readAsText(this.files[0]);
        });
        $("#json").click(function(event) {
            updater.socket.send('{"message": "json"}');
        });
        $("#csv").click(function(event) {
            updater.socket.send('{"message": "csv"}');
        });
        $("#md").click(function(event) {
            updater.socket.send('{"message": "md"}');
        });
        $("#html").click(function(event) {
            updater.socket.send('{"message": "html","content": "' + document.getElementById("bodies").checked + '"}');
        });
        $("#htmlcontainer").hover(function(event) {
            $("#htmlconfig").css("display", "inline");
        }, function(event) {
            $("#htmlconfig").css("display", "none");
        });
        $("#bodies").change(function(event) {
            $(".body").toggle(this.checked);
        });
        $("#delete").click(function(event) {
            if (window.confirm("This will delete ALL of your saved reddit links. It will take a long time. Are you sure?"))
                updater.socket.send('{"message": "delete"}');
        });
        $("#signout").click(function(event) {
            window.location.assign("/auth");
        });
    },

    showMessage: function(message) {
        var node = $(message);
        $("#container").append(node);
        updater.link++;
        $("#num").text(updater.link);
    }
};
