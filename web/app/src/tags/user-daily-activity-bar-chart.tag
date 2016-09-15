<user-daily-activity-bar-chart>

  <div>
    <canvas name="chart" height="200"></canvas>
  </div>

  <style scoped>
  </style>

  <script>
    this.on('mount', () => {
      setTimeout(this.buildChart, 0) // Dom readyness...
    })

    this.buildChart = () => {
      let data = opts.data

      let now = new Date()

      let labels = []
      for (let i = 0; i < data.length; ++i) {
        labels.unshift(`${now.getDate()}/${now.getMonth() + 1}`)
        now = new Date(now.getTime() - 1000 * 3600 * 24)
      }

      new Chart(this.chart, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Unique messages',
              data: data.map(d => d.unique),
              backgroundColor: 'rgba(148, 189, 234, 0.5)',
              borderWidth: 0
            },
            {
              label: 'Edited messages',
              data: data.map(d => d.action - d.unique),
              backgroundColor: 'rgba(54, 114, 181, 0.5)',
              borderWidth: 0
            },
            {
              label: 'Deleted messages',
              data: data.map(d => d.deleted),
              backgroundColor: 'rgba(130, 82, 78, 0.5)',
              borderColor: 'grey',
              borderWidth: 0
            }
          ]
        },
        options: {
          title: {
            display: opts.title,
            text: opts.title
          },
          scales: {
            yAxes: [{
              ticks: {
                beginAtZero:true
              },
              stacked: true
            }],
            xAxes: [{
              stacked: true
            }]
          },
        }
      })
    }
  </script>

</user-daily-activity-bar-chart>
