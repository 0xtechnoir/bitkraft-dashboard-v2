Install dependencies from requirments.txt
```
pip3 install -r requirements.txt
```

Install a new dependency
```
pip install <dependency name>
```
Then update requirements.txt
```
pip freeze > requirements.txt
```

Learnings:

Data for a chart should all be in the same dataframe. If not you run into problems, such as having to click the range buttons twice to update the series. 