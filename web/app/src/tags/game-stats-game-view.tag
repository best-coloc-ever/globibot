<game-stats-game-view>

  <!-- layout -->
  <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col">

    <h4 align="center">
      Play time for <span class="game-name">{ opts.game }</span>
    </h4>

    <div class="mdl-grid">

      <div class="mdl-cell mdl-cell--3-col"></div>
      <div class="mdl-cell mdl-cell--6-col">
        <table class="mdl-data-table mdl-js-data-table">
          <col span="1", class="small">
          <tr>
            <th>#</th>
            <th class="mdl-data-table__cell--non-numeric">User</th>
            <th>Total time played</th>
          </tr>
          <tr each={ row, i in data }>
            <td>{ i + 1 }</td>
            <td class="mdl-data-table__cell--non-numeric">
              <a href={ '#game-stats/user/' + row.user.id }>{ row.user.name }</a>
            </td>
            <td class="mdl-data-table__cell">{ duration(row.duration) }</td>
          </tr>
        </table>
      </div>

    </div>

  </div>

  <!-- style -->
  <style scoped>
    .game-name {
      font-weight: bold;
    }

    tr {
      height: 1em;
    }

    td {
      overflow: hidden;
      white-space: nowrap;
    }

    .small {
      width: 50px;
    }

    table {
      table-layout: fixed;
      width: 100%;
    }
  </style>


  <!-- logic -->
  <script>
    import API from '../api.js'
    import humanizeDuration from 'humanize-duration'

    this.data = null

    this.on('mount', () => {
      API.gameStatsGame(opts.game)
        .then(data => {
          this.data = data
          this.update()
          componentHandler.upgradeElements(this.root)
        })
    })

    this.duration = seconds => {
      return humanizeDuration(seconds * 1000, { largest: 2, round: true })
    }
  </script>

</game-stats-game-view>
