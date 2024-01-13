### Install dependencies from requirments.txt
```
pip3 install -r requirements.txt
```

### Install a new dependency
```
pip install <dependency name>
```
Then update requirements.txt
```
pip freeze > requirements.txt
```

## Learnings:

### Dataframes:
Data for a chart should all be in the same dataframe. If not you run into problems, such as having to click the range buttons twice to update the series. 

### WebGL vs SVG-based Rendering:

By default plotly appears to use WebGL under the hood to render traces on charts. Chromium browsers are currently able to support 16 WebGL contexts on a page at any one time.

Once I got to a certain number of charts on a page I was experiecing an issue where some charts would disappear when I refreshed others. This was because the context limit had been exceeded.

To resolve this issue I chose a trace type that used SVG-based rendering instead of WebGL. These are slower to load but this is a tradeoff I'm okay with. 

More info: 

https://plotly.com/python/webgl-vs-svg/#svg-and-canvaswebgl-two-browser-capabilities-for-rendering
https://plotly.com/python/v3/compare-webgl-svg/