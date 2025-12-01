let allData = [];
let filteredData = [];
let selectedIndices = [];
let currentPage = 1;
const itemsPerPage = 10;

// Clean tweet text
function cleanTweet(tweet) {
    if (!tweet) return "";

    let tweetStr = String(tweet);

    // Remove array-like formatting
    if ((tweetStr.startsWith("['") && tweetStr.endsWith("']")) ||
        (tweetStr.startsWith('["') && tweetStr.endsWith('"]'))) {
        tweetStr = tweetStr.substring(2, tweetStr.length - 2);
        if (tweetStr.includes(',') && (tweetStr.match(/'/g) || []).length > 2) {
            const parts = tweetStr.split("',");
            if (parts.length > 0) {
                tweetStr = parts[0].trim();
                if (tweetStr.startsWith("'") || tweetStr.startsWith('"')) {
                    tweetStr = tweetStr.substring(1);
                }
                if (tweetStr.endsWith("'") || tweetStr.endsWith('"')) {
                    tweetStr = tweetStr.substring(0, tweetStr.length - 1);
                }
            }
        }
    }

    // Handle byte strings
    if (tweetStr.startsWith("b'") || tweetStr.startsWith('b"')) {
        tweetStr = tweetStr.substring(2);
        if (tweetStr.endsWith("'") || tweetStr.endsWith('"')) {
            tweetStr = tweetStr.substring(0, tweetStr.length - 1);
        }
        tweetStr = tweetStr.replace(/\\n/g, '\n').replace(/\\t/g, '\t').replace(/\\r/g, '\r');
    }

    // Decode HTML entities
    tweetStr = tweetStr.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');

    // Normalize whitespace
    tweetStr = tweetStr.replace(/\s+/g, ' ').trim();

    return tweetStr;
}

// Load CSV data
function loadData() {
    Papa.parse('ProcessedTweets.csv', {
        download: true,
        header: true,
        complete: function(results) {
            allData = results.data.map((row, index) => ({
                index: index,
                Month: row.Month,
                Sentiment: parseFloat(row.Sentiment),
                Subjectivity: parseFloat(row.Subjectivity),
                Dimension1: parseFloat(row['Dimension 1']),
                Dimension2: parseFloat(row['Dimension 2']),
                RawTweet: cleanTweet(row.RawTweet)
            })).filter(row => !isNaN(row.Sentiment) && !isNaN(row.Subjectivity));

            initializeControls();
            updateVisualization();
        }
    });
}

// Initialize dropdowns and sliders
function initializeControls() {
    const months = [...new Set(allData.map(d => d.Month))].sort();
    const monthDropdown = document.getElementById('month-dropdown');

    months.forEach(month => {
        const option = document.createElement('option');
        option.value = month;
        option.textContent = month;
        monthDropdown.appendChild(option);
    });

    // Add event listeners
    monthDropdown.addEventListener('change', updateVisualization);

    // Initialize sentiment slider
    const sentimentSlider = document.getElementById('sentiment-slider');
    noUiSlider.create(sentimentSlider, {
        start: [-1.0, 1.0],
        connect: true,
        range: {
            'min': -1.0,
            'max': 1.0
        },
        step: 0.01,
        tooltips: [
            { to: function(value) { return value.toFixed(2); } },
            { to: function(value) { return value.toFixed(2); } }
        ]
    });

    sentimentSlider.noUiSlider.on('update', function(values) {
        document.getElementById('sentiment-min-value').textContent = parseFloat(values[0]).toFixed(2);
        document.getElementById('sentiment-max-value').textContent = parseFloat(values[1]).toFixed(2);
    });

    sentimentSlider.noUiSlider.on('change', updateVisualization);

    // Initialize subjectivity slider
    const subjectivitySlider = document.getElementById('subjectivity-slider');
    noUiSlider.create(subjectivitySlider, {
        start: [0.0, 1.0],
        connect: true,
        range: {
            'min': 0.0,
            'max': 1.0
        },
        step: 0.01,
        tooltips: [
            { to: function(value) { return value.toFixed(2); } },
            { to: function(value) { return value.toFixed(2); } }
        ]
    });

    subjectivitySlider.noUiSlider.on('update', function(values) {
        document.getElementById('subjectivity-min-value').textContent = parseFloat(values[0]).toFixed(2);
        document.getElementById('subjectivity-max-value').textContent = parseFloat(values[1]).toFixed(2);
    });

    subjectivitySlider.noUiSlider.on('change', updateVisualization);
}

// Filter data based on controls
function filterData() {
    const selectedMonth = document.getElementById('month-dropdown').value;
    const sentimentValues = document.getElementById('sentiment-slider').noUiSlider.get();
    const sentimentMin = parseFloat(sentimentValues[0]);
    const sentimentMax = parseFloat(sentimentValues[1]);
    const subjectivityValues = document.getElementById('subjectivity-slider').noUiSlider.get();
    const subjectivityMin = parseFloat(subjectivityValues[0]);
    const subjectivityMax = parseFloat(subjectivityValues[1]);

    filteredData = allData.filter(d =>
        d.Month === selectedMonth &&
        d.Sentiment >= sentimentMin &&
        d.Sentiment <= sentimentMax &&
        d.Subjectivity >= subjectivityMin &&
        d.Subjectivity <= subjectivityMax
    );
}

// Update scatter plot
function updateScatterPlot() {
    const trace = {
        x: filteredData.map(d => d.Dimension1),
        y: filteredData.map(d => d.Dimension2),
        mode: 'markers',
        type: 'scattergl',
        marker: {
            size: 8,
            color: '#333333',
            opacity: 0.8,
            line: { width: 0 }
        },
        customdata: filteredData.map(d => d.index),
        hovertemplate: '<extra></extra>'
    };

    const layout = {
        xaxis: {
            showgrid: true,
            gridcolor: 'lightgray',
            zeroline: false,
            showticklabels: false,
            title: ''
        },
        yaxis: {
            showgrid: true,
            gridcolor: 'lightgray',
            zeroline: false,
            showticklabels: false,
            title: ''
        },
        plot_bgcolor: '#f5f5f5',
        paper_bgcolor: 'white',
        margin: { l: 40, r: 60, t: 40, b: 40 },
        hovermode: 'closest',
        dragmode: 'lasso',
        title: ''
    };

    const config = {
        displayModeBar: true,
        modeBarButtonsToRemove: ['autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian'],
        displaylogo: false,
        modeBarButtonsToAdd: ['select2d', 'lasso2d'],
        toImageButtonOptions: {
            format: 'png',
            filename: 'custom_image',
            height: 500,
            width: 700,
            scale: 1
        }
    };

    Plotly.newPlot('scatter-plot', [trace], layout, config);

    // Handle selection
    const plotElement = document.getElementById('scatter-plot');
    plotElement.on('plotly_selected', function(eventData) {
        if (eventData && eventData.points) {
            selectedIndices = eventData.points.map(p => p.customdata);
            updateTable();
        }
    });

    // Fix modebar orientation
    setTimeout(fixModebar, 500);
}

// Fix modebar SVG orientation
function fixModebar() {
    const modebars = document.querySelectorAll('.modebar');
    modebars.forEach(function(modebar) {
        modebar.style.setProperty('right', '5px', 'important');
        modebar.style.setProperty('left', 'auto', 'important');
        modebar.style.setProperty('position', 'absolute', 'important');
        modebar.style.setProperty('top', '10px', 'important');
        modebar.style.setProperty('display', 'flex', 'important');
        modebar.style.setProperty('flex-direction', 'column', 'important');
    });

    const svgs = document.querySelectorAll('.modebar-btn svg');
    svgs.forEach(function(svg) {
        svg.style.setProperty('transform', 'scaleY(-1)', 'important');
    });
}

// Update data table
function updateTable() {
    const tbody = document.getElementById('tweet-table-body');
    tbody.innerHTML = '';

    let dataToShow = [];
    if (selectedIndices.length > 0) {
        dataToShow = filteredData.filter(d => selectedIndices.includes(d.index));
    }

    const totalPages = Math.ceil(dataToShow.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, dataToShow.length);

    for (let i = startIndex; i < endIndex; i++) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.textContent = dataToShow[i].RawTweet;
        row.appendChild(cell);
        tbody.appendChild(row);
    }

    // Update pagination
    document.getElementById('page-info').textContent =
        dataToShow.length > 0 ? `Page ${currentPage} of ${totalPages}` : 'No data';
    document.getElementById('prev-page').disabled = currentPage <= 1;
    document.getElementById('next-page').disabled = currentPage >= totalPages || dataToShow.length === 0;
}

// Update everything
function updateVisualization() {
    filterData();
    updateScatterPlot();
    selectedIndices = [];
    currentPage = 1;
    updateTable();
}

// Pagination handlers
document.getElementById('prev-page').addEventListener('click', function() {
    if (currentPage > 1) {
        currentPage--;
        updateTable();
    }
});

document.getElementById('next-page').addEventListener('click', function() {
    currentPage++;
    updateTable();
});

// Load data on page load
loadData();
