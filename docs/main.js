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
`;
    try {
        await pyodide.runPythonAsync(code);
        const output = pyodide.globals.get('output');
        const columns = pyodide.globals.get('columns').toJs();
        const index = pyodide.globals.get('index').toJs();
        const data = JSON.parse(output);
        renderTable(data, columns, index);
    } catch (err) {
        document.getElementById('output').innerText = 'Error: ' + err;
    }
}

function renderTable(data, columns, index) {
    let html = '<table class="styled-table"><thead><tr><th></th>';
    for (const col of columns) {
        html += `<th>${col}</th>`;
    }
    html += '</tr></thead><tbody>';
    for (const row of index) {
        html += `<tr><td>${row}</td>`;
        for (const col of columns) {
            html += `<td>${Number(data[col][row]).toLocaleString(undefined, {maximumFractionDigits: 4})}</td>`;
        }
        html += '</tr>';
    }
    html += '</tbody></table>';
    document.getElementById('output').innerHTML = html;
}

main();
