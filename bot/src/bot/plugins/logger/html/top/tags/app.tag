<app>

  <h4>Latest messages on server # { serverId }</h4>
  <ul>
    <li each={ data in latestMessages }> <span style="color:#aaa">#{ data.channel.name }</span> @<a class="latestMSGUser" href={ '/logs/user?id=' + data.author.id }>{ data.author.name }</a>: { data.message.clean_content }</li>
  </ul>

  <h4>Top Message count per user on server # { serverId }</h4>

  <table if={ data } style="width:100%;min-width:600px;table-layout:fixed;">
    <tr>
      <th style="width:10%">#</th>
      <th style="width:50%">User</th>
      <th style="width:20%; color: blue"><a onclick={ changeSort.bind(undefined, compareCount) }>Message count</a></th>
      <th style="width:20%; color: blue"><a onclick={ changeSort.bind(undefined, compareActive) }>Last active</a></th>
    </tr>

    <tr each={ item, i in data }>
      <td>{ i + 1 }</td>
      <td><a href={ '/logs/user?id=' + item[0][0] }>{ item[0][1] }</a></td>
      <td>{ item[1] }</td>
      <td><timer value={ item[2] }></timer></td>
    </tr>
  </table>

  <style scoped>
    table, th, td {
      border: 1px solid black;
    }
    a {
      text-decoration:none;
    }
    a:hover {
      text-decoration:underline;
    }
    .lastMSGUser{
      color:#777;
    }
    li {
      font-family: Helvetica Neue,Helvetica,sans-serif;
      font-size: 12px;
      line-height: 20px;
      color: #444;
      list-style-type: none;
    }
  </style>

  <script>
    var self = this;

    this.serverId = riot.route.query().id;
    this.data = null;
    this.latestMessages = [];

    this.sortFn = self.compareCount;

    compareCount(a, b) {
      return b[1] - a[1];
    }

    compareActive(a, b) {
      return b[2] - a[2];
    }

    changeSort(sort) {
      self.sortFn = sort;
      self.data.sort(self.sortFn);
      self.update();
    }

    $.get({
      url: '/logs/api/top/' + this.serverId,
      success: function(data) {
        self.data = data; self.update();
        for (var d of self.data)
          d[2] *= 1000;
      },
      error: function(e) { console.log(e); }
    });

    var ws = new WebSocket('wss://' + window.location.host + '/ws/logs');

    ws.onopen = function() {
      console.log('opened');
    };

    ws.onmessage = function(d) {
      var data = JSON.parse(d.data);

      if (data.server.id == self.serverId) {
        self.latestMessages.push(data);
        if (self.latestMessages.length > 10)
          self.latestMessages.splice(0, self.latestMessages.length - 10);

        for (var d of self.data)
          if (d[0][0] == data.author.id) {
            d[1] += 1;
            d[2] = new Date().getTime();
          }

        self.data.sort(self.sortFn);

        self.update();
      }
    };

  </script>

</app>
