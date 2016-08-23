<app>

  <h2>Reposts on # { serverId }</h2>
  Test your link here: <input id="input" onKeyUp={ checkLink }></input>
  <br>
  <br>
  <br>
  <div if={ result != null }>
    <div if={ result }>
      Your link has already been posted by <user name="user" snowflake={ result[0] }></user> on { new Date(result[1] * 1000) }
    </div>

    <div if={ !result }>
      Your link has never been posted on this server!
    </div>
  </div>

  <h2>Recent links</h2>

  <table if={ recentData } style="width:70%;min-width:600px;table-layout:fixed;">
    <tr>
      <th style="width:40%">link</th>
      <th style="width:20%">author</th>
      <th style="width:10%">when</th>
    </tr>

    <tr each={ info in recentData }>
      <td><a href={ info[0] }>{ info[0] }</a></td>
      <td><user snowflake={ info[1] }></user></td>
      <td><timer value={ info[2] * 1000 }></timer></td>
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
    this.result = null;

    $.get({
      url: '/repost/api/' + this.serverId,
      success: function(data) {
        self.data = data;
        self.updateTable();
      }
    });

    checkLink() {
      var link = $('#input').val();
      if (link in self.data) {
        this.result = self.data[link];
        this.tags.user.fetchUser();
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
