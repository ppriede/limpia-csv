import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory storage of dataframes keyed by filename
DATA = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return redirect(url_for('index'))
    path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(path)
    df = pd.read_csv(path)
    if 'label' not in df.columns:
        df['label'] = ''
    DATA[file.filename] = df
    return redirect(url_for('data_view', filename=file.filename))

@app.route('/data/<filename>')
def data_view(filename):
    df = DATA.get(filename)
    if df is None:
        return redirect(url_for('index'))
    return render_template('data.html', filename=filename, tables=[df.head().to_html(classes='data')], titles=df.columns.values)

@app.route('/label/<filename>', methods=['POST'])
def label(filename):
    df = DATA.get(filename)
    if df is None:
        return redirect(url_for('index'))
    start = int(request.form.get('start', 0))
    end = int(request.form.get('end', len(df)-1))
    label = request.form.get('label', '')
    df.loc[start:end, 'label'] = label
    return redirect(url_for('data_view', filename=filename))

@app.route('/stats/<filename>')
def stats(filename):
    df = DATA.get(filename)
    if df is None:
        return redirect(url_for('index'))
    lbl = request.args.get('label')
    if lbl:
        subset = df[df['label'] == lbl]
    else:
        subset = df
    if subset.empty:
        res = {}
    else:
        values = subset.iloc[:,1].astype(float)  # assume second column has data
        res = {
            'media': values.mean(),
            'mediana': values.median(),
            'promedio_energetico_ruido': np.sqrt(np.mean(values**2)),
            'p90': np.percentile(values, 90),
            'p10': np.percentile(values, 10)
        }
    return render_template('stats.html', filename=filename, stats=res, label=lbl)


@app.route('/plot/<filename>')
def plot(filename):
    df = DATA.get(filename)
    if df is None:
        return redirect(url_for('index'))
    cols = df.columns[1:]
    return render_template('plot.html', filename=filename, columns=cols)


@app.route('/data_json/<filename>')
def data_json(filename):
    df = DATA.get(filename)
    if df is None:
        return jsonify({})
    col = request.args.get('column', df.columns[1])
    return jsonify({
        'x': df.iloc[:, 0].astype(str).tolist(),
        'y': df[col].astype(float).tolist()
    })


@app.route('/compute_stats/<filename>', methods=['POST'])
def compute_stats(filename):
    df = DATA.get(filename)
    if df is None:
        return jsonify({})
    data = request.get_json() or {}
    col = data.get('column', df.columns[1])
    indices = [int(i) for i in data.get('indices', [])]
    subset = df.iloc[indices] if indices else df
    values = subset[col].astype(float)
    res = {
        'media': values.mean(),
        'mediana': values.median(),
        'promedio_energetico_ruido': float(np.sqrt(np.mean(values ** 2))),
        'p90': float(np.percentile(values, 90)),
        'p10': float(np.percentile(values, 10))
    }
    return jsonify(res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
