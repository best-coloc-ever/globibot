<app>

  <h2>Shame wall</h2>

  <div>
    Reposts for <user snowflake={ userId }></user> on server # { serverId }
  </div>

  <table if={ data } style="table-layout:fixed;">
    <tr>
      <th style="width:60%">Link</th>
      <th style="width:20%">Date reposted</th>
    </tr>

    <tr each={ info in data }>
      <td><a href={ info[0] }>{ info[0] }</a></td>
      <td>{ new Date(info[1] * 1000).toLocaleString() }</td>
    </tr>
  </table>

  <style>
    table, th, td {
      border: 1px solid black;
    }
  </style>

  <script>
    var self = this;

    this.serverId = riot.route.query().server_id;
    this.userId = riot.route.query().user_id;

    this.data = null;

    $.get({
      url: '/repost/api/user/' + this.serverId + '/' + this.userId,
      success: function(data) {
        self.data = data;
        self.update();
      }
    });
  </script>

</app>
