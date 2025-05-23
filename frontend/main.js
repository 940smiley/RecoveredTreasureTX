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
output = df.describe().to_string()
`;
    try {
        await pyodide.runPythonAsync(code);
        const output = pyodide.globals.get('output');
        document.getElementById('output').innerText = output;
    } catch (err) {
        document.getElementById('output').innerText = 'Error: ' + err;
    }
}

main();
