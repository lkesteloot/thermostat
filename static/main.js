
var g_chart = null;

function createChart(series) {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");

    const charts = document.getElementById("charts");
    charts.appendChild(canvas);

    const cfg = {
        type: "line",
        data: {
            datasets: series,
        },
        options: {
            title: {
                display: true,
                fontSize: 24,
                text: "Temperature",
            },
            scales: {
                xAxes: [{
                    type: "time",
                    distribution: "linear",
                    time: {
                        unit: "hour",
                        round: true,
                        parser: function(date) {
                            return moment.utc(date).local();
                        },
                    },
                    ticks: {
                        source: "auto",
                        autoSkip: true,
                    },
                }],
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: "Fahrenheit",
                    },
                    ticks: {
                        beginAtZero: false,
                        /*
                        callback: function (value, index, values) {
                            // Add commas.
                            return value.toLocaleString();
                        },
                        */
                    }
                }]
            }
        }
    };

    g_chart = new Chart(ctx, cfg);
}

function plotTemps(samples) {
    const series = [
        {
            data: samples.map(sample => ({
                "t": sample.recorded_at,
                "y": sample.actual_temp,
            })),
            label: "Actual",
            pointRadius: 0,
            borderColor: "#00C000",
            fill: false,
            pointHitRadius: 10,
            cubicInterpolationMode: "monotone",
        },
        {
            data: samples.map(sample => ({
                "t": sample.recorded_at,
                "y": sample.outside_temp,
            })),
            label: "Outside",
            pointRadius: 0,
            borderColor: "#0000C0",
            fill: false,
            pointHitRadius: 10,
            cubicInterpolationMode: "monotone",
        },
        {
            data: samples.map(sample => ({
                "t": sample.recorded_at,
                "y": sample.set_temp,
            })),
            label: "Set",
            pointRadius: 0,
            borderColor: "#C00000",
            fill: false,
            pointHitRadius: 10,
            cubicInterpolationMode: "monotone",
        },
    ];

    if (g_chart === null) {
        createChart(series);
    } else {
        g_chart.data.datasets = series;
        g_chart.update(0);
    }
}

function fetchData() {
    fetch("/api/temp?minutes=1440")
        .then(response => {
            if (response.status !== 200) {
                throw new Error("Status Code: " + response.status);
            } else {
                return response.json();
            }
        })
        .then(data => plotTemps(data.samples))
        .catch(err => console.error("Fetch Error", err));

    setTimeout(fetchData, 60*1000);
}

fetchData();

