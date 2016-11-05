<game-stats-user-view>

  <!-- layout -->
  <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col">

    <h4 align="center">Game stats for <user snowflake={ opts.userId }></user></h4>

    <div class="mdl-grid">

      <div class="mdl-cell mdl-cell--3-col"></div>
      <div class="mdl-cell mdl-cell--6-col">
        <table class="mdl-data-table mdl-js-data-table">
          <col span="1", class="small">
          <tr>
            <th>#</th>
            <th class="mdl-data-table__cell--non-numeric">Game</th>
            <th>Total time played</th>
          </tr>
          <tr each={ row, i in data }>
            <td>{ i + 1 }</td>
            <td class="mdl-data-table__cell--non-numeric">
              <a href={ '#game-stats/game/' + row.name }>{ row.name }</a>
            </td>
            <td class="mdl-data-table__cell">{ duration(row.duration) }</td>
          </tr>
      </div>

    </div>

  </div>


  <!-- style -->
  <style scoped>
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
      API.gameStatsUser(opts.userId)
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

</game-stats-user-view>
