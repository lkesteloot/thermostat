
function plotTemps(samples) {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");

    const charts = document.getElementById("charts");
    charts.appendChild(canvas);

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
        }
    ];

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
                        callback: function (value, index, values) {
                            // Add commas.
                            return value.toLocaleString();
                        },
                    }
                }]
            }
        }
    };

    new Chart(ctx, cfg);
}

fetch("/api/temp")
    .then(response => {
        if (response.status !== 200) {
            console.log("Looks like there was a problem. Status Code: " + response.status);
            return;
        }

        // Examine the text in the response
        response.json().then(data => {
            plotTemps(data.samples);
        });
    })
    .catch(err => {
        console.log("Fetch Error", err);
    });

