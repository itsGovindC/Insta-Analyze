# Insta-Analyze
Social Media Analytics Tool that creates analytics purely from a person's instagram

In order to run this properly, you need a Google Cloud Account setup properly.

When you do, replace the  following with your KEY and GOOGLE_APPLICATION_CREDENTIALS location (typically a json source file)

```python
gmaps = googlemaps.Client(key='google-maps-key')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="Directory of your google app credentials"
```
