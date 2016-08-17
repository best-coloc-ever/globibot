<app>

  <h4>Latest messages on server # { serverId }</h4>
  <ul>
    <li each={ message in latestMessages }>{ message.author }: { message.content }</li>
  </ul>

  <h4>Top Message count per user on server # { serverId }</h4>

  <table if={ data }>
    <tr>
      <th>#</th>
      <th>User</th>
      <th>Message count</th>
    </tr>

    <tr each={ item, i in data }>
      <td>{ i + 1 }</td>
      <td><a href={ '/logs/user?id=' + item[0][0] }>{ item[0][1] }</a></td>
      <td>{ item[1] }</td>
    </tr>
  </table>

  <style scoped>
    table, th, td {
      border: 1px solid black;
    }

    li {
      font-family: Helvetica Neue,Helvetica,sans-serif;
      font-size: 12px;
      line-height: 20px;
      color: #8c8c9c;
      list-style-type: none;
    }
  </style>

  <script>
    var self = this;

    this.serverId = riot.route.query().id;
    this.data = null;
    this.latestMessages = [];

    $.get({
      url: '/logs/api/top/' + this.serverId,
      success: function(data) {
        self.data = data; self.update();
      },
      error: function(e) { console.log(e); }
    });

    var ws = new WebSocket('wss://' + window.location.host + '/ws/logs');

    ws.onopen = function() {
      console.log('opened');
    };

    ws.onmessage = function(d) {
      var data = JSON.parse(d.data);

      if (data.server_id == self.serverId) {
        self.latestMessages.push(data);
        if (self.latestMessages.length > 10)
          self.latestMessages.splice(0, self.latestMessages.length - 10);

        for (var d of self.data)
          if (d[0] == data.author)
            d[1] += 1;

        self.data.sort(function(a, b) {
          return b[1] - a[1];
        })

        self.update();
      }
    };
  </script>

</app>
