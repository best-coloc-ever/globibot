<app>

  <h4>Top words for user # { userID }</h4>

  <table if={ data }>
    <tr>
      <th>#</th>
      <th>word</th>
      <th>count</th>
      <th>last used</th>
    </tr>

    <tr each={ item, i in data }>
      <td>{ i + 1 }</td>
      <td>{ item[0] }</td>
      <td>{ item[1] }</td>
      <td><timer value={ item[2] }></timer></td>
    </tr>
  </table>

  <style scoped>
    table, th, td {
      border: 1px solid black;
    }
  </style>

  <script>
    var self = this;

    this.userID = riot.route.query().id;
    this.raw_data = null;
    this.data = [];

    $.get({
      url: '/logs/api/user/' + this.userID,
      success: function(data) {
        self.raw_data = data;
        self.rebuild();
      },
      error: function(e) { console.log(e); }
    });

     var ws = new WebSocket('wss://' + window.location.host + '/ws/logs');

    ws.onopen = function() {
      console.log('opened');
    };

    ws.onmessage = function(d) {
      var data = JSON.parse(d.data);

      if (data.author.id == self.userID) {
        self.raw_data.push([data.message.content, new Date().getTime() / 1000]);
        self.rebuild();
      }
    };

    rebuild() {

      self.data = [];
      var wordMap = {};
      var timeMap = {};
      for (var d of self.raw_data) {
        var message = d[0];
        var stamp = d[1];

        words = message.split(' ');
        for (var word of words) {
          if (!word)
            continue;
          if (word in wordMap)
            wordMap[word] += 1;
          else
            wordMap[word] = 1;

          if (word in timeMap) {
            if (stamp > timeMap[word])
              timeMap[word] = stamp;
          }
          else
            timeMap[word] = stamp;
        }
      }

      for (var k in wordMap) {
        if (wordMap[k] > 1)
          self.data.push([k, wordMap[k], timeMap[k]]);
      }

      self.data.sort(function(a, b) { return b[1] - a[1]; });

      self.update();
    }
  </script>

</app>
