// main.js
let pyodideReadyPromise;

async function main() {
    pyodideReadyPromise = loadPyodide();
    document.getElementById('analyzeBtn').addEventListener('click', async () => {
        const fileInput = document.getElementById('csvInput');
        if (!fileInput.files.length) {
            alert('Please select a CSV file.');
            return;
        }
        const file = fileInput.files[0];
        const text = await file.text();
        await runPythonAnalysis(text);
    });
}

async function runPythonAnalysis(csvText) {
    const pyodide = await pyodideReadyPromise;
    await pyodide.loadPackage(['pandas']);
    const code = `
import pandas as pd
from io import StringIO
csv_data = '''${csvText.replace(/'/g, "''")}'''
df = pd.read_csv(StringIO(csv_data))
desc = df.describe()
output = desc.to_json()
columns = list(desc.columns)
index = list(desc.index)
print('DEBUG: desc.to_json()', output)
print('DEBUG: columns', columns)
print('DEBUG: index', index)
`;
    try {
        await pyodide.runPythonAsync(code);
        const output = pyodide.globals.get('output');
        const columns = pyodide.globals.get('columns').toJs();
        const index = pyodide.globals.get('index').toJs();
        const data = JSON.parse(output);
        console.log('DEBUG: Data for table', data, columns, index); // Debugging
        renderTable(data, columns, index);
    } catch (err) {
        document.getElementById('output').innerText = 'Error: ' + err;
        console.error('DEBUG: Error in runPythonAnalysis', err); // Debugging
    }
}

function renderTable(data, columns, index) {
    let html = '<table class="styled-table"><thead><tr><th>Statistic</th>';
    for (const col of columns) {
        html += `<th>${col}</th>`;
    }
    html += '</tr></thead><tbody>';
    for (const stat of index) {
        html += `<tr><td>${stat}</td>`;
        for (const col of columns) {
            let value = data[col][stat];
            if (typeof value === 'number') {
                value = value.toLocaleString(undefined, { maximumFractionDigits: 4 });
            } else if (value === null || value === undefined) {
                value = '';
            }
            html += `<td>${value}</td>`;
        }
        html += '</tr>';
    }
    html += '</tbody></table>';
    document.getElementById('output').innerHTML = html;
}

main();
