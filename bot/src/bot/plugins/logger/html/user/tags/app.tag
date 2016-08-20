<app>

  <h4>Top words for user # { userID }</h4>

  <table if={ data }>
    <tr>
      <th>#</th>
      <th>word</th>
      <th>count</th>
    </tr>

    <tr each={ item, i in data }>
      <td>{ i + 1 }</td>
      <td>{ item[0] }</td>
      <td>{ item[1] }</td>
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
        self.raw_data.push(data.message.content);
        self.rebuild();
      }
    };

    rebuild() {

      self.data = [];
      var wordMap = {};
      for (var d of self.raw_data) {
        words = d.split(' ');
        for (var word of words) {
          if (!word)
            continue;
          if (word in wordMap)
            wordMap[word] += 1;
          else
            wordMap[word] = 1;
        }
      }

      for (var k in wordMap)
        self.data.push([k, wordMap[k]]);

      self.data.sort(function(a, b) { return b[1] - a[1]; });

      self.update();
    }
  </script>

</app>
