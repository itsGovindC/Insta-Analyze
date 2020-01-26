import io
import os
import json
import instaloader
import googlemaps
import glob
import pandas

gmaps = googlemaps.Client(key='google-maps-key')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="Directory of your google app credentials"
# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
# Imports Message to Dict for the Dictionary creation
from google.protobuf.json_format import MessageToDict

# Instantiates a client
client = vision.ImageAnnotatorClient()

#Commannd Line Interface
user = input("Enter Instagram username to scrape: ")
login = input("Enter your instagram username: ")


# Download user's pictures
def downloadImages(user, login):
    profile = '{profile}'
    os.system(f"instaloader --no-videos --no-captions --no-metadata-json --geotags --login={login} --dirname-pattern=ImageData/{profile} profile {user}")
    print("Downloaded!")

def process_image(client,image_location,user):
    # The name of the image file to annotate
    file_name = os.path.abspath(image_location)

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    image = types.Image(content=content)

    # Performs label detection on the image file
    response = client.label_detection(image=image)
    tempDict = MessageToDict(response)

    #Creating the dump location for JSON Files
    base = os.path.basename(image_location)
    file_name_edited = os.path.splitext(base)[0]
    save_path = 'JSON\\' + user
    completeName = os.path.join(save_path,file_name_edited + ".json")

    #create directory for the user if it does not exist already
    if(not(os.path.isdir(os.path.dirname(completeName)))):
        os.mkdir(os.path.dirname(completeName))

    #Dumping to compiled file location
    with open(completeName, 'w') as f:
        json.dump(tempDict, f,indent=4,sort_keys=True)


#temporary splitting of json per picture to multiple JSON's
def convert_to_format(file_name):
    temp = open(file_name)
    data = json.load(temp)
    temp.close()
    list1 = data['labelAnnotations'] #list of JSON 
    count = 0
    for x in list1: 
        if(count==0):
            count+=1
            with open(file_name,'w') as f:
                json.dump(x,f,indent=4,sort_keys=True)
        else:
            base = os.path.basename(file_name)
            base = os.path.splitext(base)[0] +'_temp_' +str(count) 
            head = os.path.split(file_name)[0]
            file_name_edited = os.path.join(head,base + ".json") #creating different files for each value of list1
            with open(file_name_edited,'w') as f:
                json.dump(x,f,indent=4,sort_keys=True)
            count+=1

#does above process on every single JSON file that has not been processed
def process_json(user):
    for filename in os.listdir(f'JSON\{user}'):
        name = os.path.join(f'JSON\{user}', filename)
        if name.endswith(".json") and (not('location' in name)):
            convert_to_format(name)

#combines all the JSON files into a massive csv and removes  unncessary data
def json_to_csv(user):
    result = []
    for f in glob.glob('JSON\\'+ user +'\\*.json'):
        if(not('location' in f)):
            with open(f, "rb") as infile:
                result.append(json.load(infile))

    with open('JSON\\'+ user +'\\' +"merged_file.json", "w") as outfile:
        json.dump(result, outfile)
    df=pandas.read_json('JSON\\'+ user +'\\' +"merged_file.json")
    df=df.drop(columns=['mid','topicality'])
    df['freq'] = df.groupby('description')['description'].transform('size')
    df=df.groupby('description', as_index=False).mean()
    df=df.sort_values(by='freq',ascending=False)
    df=df.head(100)
    df=df.tail(80)
    df.to_csv('JSON\\'+ user +'\\' +'output.csv', index=False)

    for f in glob.glob('JSON\\'+ user +'\\*.json'):
        if(not('location' in f)):
            os.remove(f)



def process_images(user):
    for filename in os.listdir(f'ImageData\{user}'):
        name = os.path.join(f'ImageData\{user}', filename)
        if name.endswith(".jpg") : 
            process_image(client,name,user)
            #print("image")
        elif name.endswith(".txt"):
            try:
                with open(name,'r') as f:
                    for i, line in enumerate(f):
                        if(i == 1):
                            #Get coordinates from instagram geotag
                            coords = (line[line.index("=")+1:line.index("&")]).split(",")
                            reverse_geocode_result = gmaps.reverse_geocode((coords[0],coords[1]))

                            #Creating the dump location for JSON Files
                            base = os.path.basename(name)
                            file_name_edited = os.path.splitext(base)[0]
                            save_path = 'JSON'  +'\\' + user
                            completeName = os.path.join(save_path,file_name_edited + ".json")
                            with open(completeName,'w') as f:
                                json.dump(reverse_geocode_result,f,indent=4)
            except:
                pass
    process_json(user)
    json_to_csv(user)
downloadImages(user, login)
process_images(user)
