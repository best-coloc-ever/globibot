<app>

  <server each={ server in servers } data={ server }></server>

  <script>
    var self = this;

    this.servers = opts.servers;

    var ws = new WebSocket('ws://' + window.location.host + '/ws');

    ws.onopen = function() {
      console.log('ws open');
    };

    ws.onclose = function() {
      console.log('ws closed');
    };

    ws.onmessage = function(e) {
      message = JSON.parse(e.data);
      for (var server of self.tags.server) {
        if (server.id == message.server.id) {
          server.onMessage(message);
        }
      }
    };
  </script>

</app>
