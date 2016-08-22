<app>

  <h3>Top words for user { userName } # { userID }</h4>

  <h5>
  Message count: { raw_data.length }<br>
  Average message length: { avgLength.toFixed(2) } characters<br>
  Average word count per message: { avgWC.toFixed(2) } words<br>
  </h5>

  <table if={ data } style="width:100%;min-width:600pxtable-layout:fixed">
    <tr>
      <th style="width:10%">#</th>
      <th style="width:60%">word</th>
      <th style="width:10%">count</th>
      <th style="width:10%">last used</th>
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
    table td{
      overflow-wrap:break-word;
    }
  </style>

  <script>
    var self = this;

    this.userID = riot.route.query().id;
    this.raw_data = null;
    this.data = [];
    this.avgLength = 0;
    this.avgWC = 0;
    this.userName = '';

    $.get({
      url: '/logs/api/user/' + this.userID,
      success: function(data) {
        self.raw_data = data;
        self.rebuild();
      },
      error: function(e) { console.log(e); }
    });

    $.get({
      url: '/user/' + this.userID,
      success: function(data) {
        console.log(data)
        self.userName = data.username;
        self.update();
      }
    })

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
      var wordCount = 0;
      var lengths = 0;
      for (var d of self.raw_data) {
        var message = d[0];
        var stamp = d[1];
        lengths += message.length;

        words = message.split(' ');
        for (var word of words) {
          word = word.toLowerCase();
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

          wordCount++;
        }
      }

      for (var k in wordMap) {
        if (wordMap[k] > 1)
          self.data.push([k, wordMap[k], timeMap[k]]);
      }

      self.data.sort(function(a, b) { return b[1] - a[1]; });
      self.avgWC = wordCount / self.raw_data.length;
      self.avgLength = lengths / self.raw_data.length;

      self.update();
    }
  </script>

</app>
