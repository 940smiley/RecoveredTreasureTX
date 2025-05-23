# Recovered Treasure TX - Card Collection Analyzer Frontend

This is a static frontend GUI for analyzing your card collection CSV files directly in the browser using Pyodide (Python in WebAssembly). You can host this on GitHub Pages.

## Features
- Upload a CSV file of your collection
- Run basic analysis (using pandas) in the browser
- View summary statistics instantly

## How to Use
1. Open `index.html` in your browser, or deploy the `frontend` folder to GitHub Pages.
2. Upload your CSV file.
3. Click "Analyze Collection" to see the results.

## Deploying to GitHub Pages
1. Commit the `frontend` folder to your repository.
2. In your repo settings, set GitHub Pages source to `/frontend` (or move contents to `/docs` and set source to `/docs`).
3. Visit your GitHub Pages URL to use the app.

## Extending Functionality
- To run more advanced analysis, port your Python logic from the main scripts into the Pyodide code in `main.js`.
- For visualizations, use libraries like matplotlib (with Pyodide) or render charts in JS.

---

For help extending the GUI or integrating more of your Python scripts, just ask!
