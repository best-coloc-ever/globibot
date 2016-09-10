<logs-view>

  <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col">
    <h4 align="center">Top Message count per user on <server snowflake={ serverId } if={ serverId }></server></h4>

    <div class="mdl-grid">
      <div class="mdl-cell mdl-cell--2-col"></div>
      <div class="mdl-cell mdl-cell--8-col">
        <table if={ data } class="mdl-data-table mdl-js-data-table">
          <tr>
            <th>#</th>
            <th class="mdl-data-table__cell--non-numeric">User</th>
            <th class="mdl-data-table__header--sorted-descending">Message count</th> <!-- <a onclick={ changeSort.bind(undefined, compareCount) }>Message count</a> -->
            <!-- <th style="width:20%; color: blue"><a onclick={ changeSort.bind(undefined, compareActive) }>Last active</a></th> -->
          </tr>

          <tr each={ item, i in data }>
            <td>{ i + 1 }</td>
            <td class="mdl-data-table__cell--non-numeric"><a href={ '#logs/' + item[0][0] }>{ item[0][1] }</a></td>
            <td>{ item[1] }</td>
            <!-- <td><timer value={ item[2] }></timer></td> -->
          </tr>
        </table>
      </div>
    </div>
  </div>

  <style scoped>
    table {
      width: 100%;
    }
  </style>

  <script>
    var self = this

    this.serverId = null
    this.data = null

    this.on('mount', () => {
      componentHandler.upgradeElements(this.root)

      let headers = new Headers({
        'Authorization': 'Bearer ' + this.opts.app.token
      })

      fetch('/bot/logs/top', { headers: headers, credentials: 'same-origin' })
        .then(r => r.json())
        .then(data => {
          self.serverId = data.server_id
          self.data = data.data
          console.log(data)
          self.update()
        })
    })
  </script>

</logs-view>
