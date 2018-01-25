import subprocess
import tempfile
import json

GLOBAL_OPTIONS = {
    "lang": {
        "rangeSelectorZoom": '',
    },
}

ZOOM_TYPE = dict(h='hour', d='day', w='week', m='month', y='year')

CHART_DATA = lambda quote, base, market, span_factor, span_unit, candle_data: {
    "title": {
        "text": "{}-{} ({})".format(quote, base, market.name),
        "margin": -28
    },
    "yAxis": [
        {
            "height": "100%",
            "labels": {
                "x": -2,
                "align": "right"
            },
            "lineWidth": 1,
        },
    ],
    "chart": {
        "width": 800,
        "height": 400
    },
    "credits": {
        "enabled": False
    },
    "scrollbar": {
        "enabled": False
    },
    "rangeSelector": {
        "buttons": [
            {
                "count": span_factor,
                "text": "All",
                "type": ZOOM_TYPE[span_unit]
            }
        ],
        "allButtonsEnabled": False,
        "selected": 0,
        "inputEnabled": False
    },
    "navigator": {
        "enabled": False
    },
    "series": [
        {
            "data": candle_data,
            "dataGrouping": market.candle_groupings,
            "type": "candlestick",
            "name": "{}{}".format(quote, base)
        }
    ]
}

def make_chart(quote, base, market, span_factor, span_unit, candle_data):
    chart_data = CHART_DATA(
        quote, base, market,
        span_factor, span_unit,
        candle_data,
    )

    _, in_file = tempfile.mkstemp(suffix='.json')
    _, out_file = tempfile.mkstemp(suffix='.png')

    with open(in_file, 'w') as f:
        json.dump(chart_data, f)

    command = [
        'highcharts-export-server',
        '-infile', in_file,
        '-outfile', out_file,
        '-constr', 'StockChart'
    ]

    process = subprocess.run(command, timeout=10)

    return out_file
