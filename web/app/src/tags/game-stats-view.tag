<game-stats-view>

  <!-- layout -->
  <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col">

    <h4 align="center">Game Stats</h4>

    <div class="mdl-tabs mdl-js-tabs mdl-js-ripple-effect">

      <div class="mdl-grid" name="spinner" if={ !data }>
        <div class="mdl-cell mdl-cell--3-col"></div>
        <div class="mdl-cell mdl-cell--6-col">
          <div class="mdl-progress mdl-js-progress mdl-progress__indeterminate">
          </div>
        </div>
      </div>

      <div class="mdl-tabs__tab-bar">
        <a each={ serverData, i in data }
           href={ '#game-stats-server-panel-' + i }
           class={ 'mdl-tabs__tab': true, 'is-active': (i == 0) }>
          <server snowflake={ serverData.server_id }></server>
        </a>
      </div>

      <div each={ serverData, i in data }
           class={ 'mdl-tabs__panel': true, 'is-active': (i == 0) }
           id={ 'game-stats-server-panel-' + i }>

        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--3-col"></div>
          <div class="mdl-cell mdl-cell--6-col">
            <table class="mdl-data-table mdl-js-data-table">
              <col span="1">
              <col span="1" class="wide">
              <tr>
                <th>#</th>
                <th class="mdl-data-table__cell--non-numeric">Game</th>
                <th>Total time played</th>
                <th>Users Playing</th>
              </tr>
              <tr each={ row, i in serverData.stats }>
                <td>{ i + 1 }</td>
                <td class="mdl-data-table__cell--non-numeric">
                  <a href={ '#game-stats/game/' + row.name }>{ row.name }</a>
                </td>
                <td class="mdl-data-table__cell">{ duration(row.duration) }</td>
                <td class="mdl-data-table__cell">{ row.playing }</td>
              </tr>
            </table>
          </div>
        </div>

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

    .wide {
      width: 200px;
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
      componentHandler.upgradeElements(this['spinner'])

      API.gameStats().then(data => {
        this.data = data
        this.update()
        componentHandler.upgradeElements(this.root)
      })
    })

    this.duration = seconds => {
      return humanizeDuration(seconds * 1000, { largest: 1, round: true })
    }
  </script>

</game-stats-view>
