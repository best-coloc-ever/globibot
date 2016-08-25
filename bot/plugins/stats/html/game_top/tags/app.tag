<app>

  <h4>Top games on server # { serverId } (Updates every 10 minutes)</h4>

  <table if={ data }>
    <tr>
      <th>#</th>
      <th>Game name</th>
      <th>Playtime (hours)</th>
      <th># playing</th>
      <th>Nerdiest</th>
    </tr>

    <tr each={ item, i in data }>
      <td>{ i + 1 }</td>
      <td>{ item[0] }</td>
      <td>{ (item[1] / 3600).toFixed(2) }</td>
      <td>{ item[2] }</td>
      <td><a href={ '/stats/user?id=' + item[3][0] }>{ item[3][1] }</a></td>
    </tr>
  </table>

  <style scoped>
    table, th, td {
      border: 1px solid black;
    }
  </style>

  <script>
    var self = this;

    this.serverId = riot.route.query().id;
    this.data = null;

    $.get({
      url: '/stats/api/games/top/' + this.serverId,
      success: function(data) { self.data = data; self.update(); },
      error: function(e) { console.log(e); }
    });
  </script>

</app>
