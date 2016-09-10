<logs-view-user>

  <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col">
    <h4 align="center">Log details for <user snowflake={ userId }></user></h4>

    <h5>
    Message count: { raw_data.length }<br>
    Average message length: { avgLength.toFixed(2) } characters<br>
    Average word count per message: { avgWC.toFixed(2) } words<br>
    </h5>

    <div class="mdl-grid">
      <div class="mdl-cell mdl-cell--2-col"></div>
      <div class="mdl-cell mdl-cell--8-col">
        <table if={ data } class="mdl-data-table mdl-js-data-table">
          <tr>
            <th >#</th>
            <th class="mdl-data-table__cell--non-numeric">word</th>
            <th class="mdl-data-table__header--sorted-descending">count</th>
            <!-- <th style="width:10%">last used</th> -->
          </tr>

          <tr each={ item, i in data }>
            <td>{ i + 1 }</td>
            <td class="mdl-data-table__cell--non-numeric">{ item[0] }</td>
            <td>{ item[1] }</td>
            <!-- <td><timer value={ item[2] * 1000 }></timer></td> -->
          </tr>
        </table>
      </div>
    </div>
  </div>

  <style scoped>
    h5 {
      margin-left: 20px;
    }
    table {
      width: 100%;
    }
    td, th{
      word-wrap:break-word;
      overflow-wrap:break-word;
      max-width: 300px;
    }
  </style>

  <script>
    var self = this

    this.userId = opts.userId

    this.raw_data = null
    this.data = []
    this.avgLength = 0
    this.avgWC = 0

    this.on('mount', () => {
      componentHandler.upgradeElements(this.root)

      let headers = new Headers({
        'Authorization': 'Bearer ' + this.opts.app.token
      })

      fetch('/bot/logs/user/' + self.userId, { headers: headers, credentials: 'same-origin' })
        .then(r => r.json())
        .then(data => {
          self.raw_data = data
          self.rebuild()
        })

    })

    this.rebuild = () => {

      self.data = [];
      var wordMap = {};
      var timeMap = {};
      var wordCount = 0;
      var lengths = 0;
      for (var d of self.raw_data) {
        var message = d[0];
        var stamp = d[1];
        lengths += message.length;

        let words = message.split(' ');
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

</logs-view-user>
