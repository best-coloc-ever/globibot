<app>

  <h2>Reposts on # { serverId }</h2>
  Test your link here: <input id="input" onKeyUp={ checkLink }></input>
  <br>
  <br>
  <br>
  <div if={ result != null }>
    <div if={ result }>
      Your link has already been posted by <user name="user_name" snowflake={ result[0] }></user> on { new Date(result[1] * 1000) }
    </div>

    <div if={ !result }>
      Your link has never been posted on this server!
    </div>
  </div>

  <h2>Recent links</h2>

  <table if={ recentData } style="table-layout:fixed;">
    <tr>
      <th style="width:70%">Link</th>
      <th style="width:20%">Author</th>
      <th style="width:10%">When</th>
    </tr>

    <tr each={ info in recentData }>
      <td><a href={ info[0] }>{ info[0] }</a></td>
      <td><user snowflake={ info[1] }></user></td>
      <td><timer value={ info[2] * 1000 }></timer></td>
    </tr>
  </table>

  <h2>Shame wall</h2>

  <table if={ shameData } style="width:30%;min-width:600px;table-layout:fixed;">
    <tr>
      <th style="width:20%">Author</th>
      <th style="width:10%">Repost count</th>
    </tr>

    <tr each={ info in shameData }>
      <td>
        <a href={ "/repost/user?user_id=" + info[0] + "&server_id=" + serverId  }>
          <user snowflake={ info[0] }></user>
        </a>
      </td>
      <td>{ info[1] }</td>
    </tr>
  </table>

  <style>
    table, th, td {
      border: 1px solid black;
    }
  </style>

  <script>
    var self = this;

    this.serverId = riot.route.query().id;
    this.data = null;
    this.recentData = null;
    this.shameData = null;
    this.result = null;

    $.get({
      url: '/repost/api/' + this.serverId,
      success: function(data) {
        self.data = data;
        self.updateTable();
      }
    });

    $.get({
      url: '/repost/api/shames/' + this.serverId,
      success: function(data) {
        self.shameData = [];
        for (var k in data)
          self.shameData.push([k, data[k].length]);
        self.shameData.sort(function(a, b) {
          return b[1] - a[1];
        });
        self.update();
      }
    });

    checkLink() {
      var link = $('#input').val();
      if (link in self.data) {
        this.result = self.data[link];
        this.tags.user_name.fetchUser();
      }
      else
        this.result = false;

      this.update();
    }

    updateTable() {
      self.recentData = [];
      for (var k in self.data) {
        var info = self.data[k];
        self.recentData.push([k, info[0], info[1]]);
      }
      self.recentData.sort(function(a, b) {
        return b[2] - a[2];
      });
      self.recentData.splice(20);
      self.update();
    }
  </script>

</app>
