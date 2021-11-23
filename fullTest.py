import requests
import os
import json
from PIL import Image

# # Edit these to match your setup
# Where images to test with are located
img_path = "./test.imgs/"
# Base URL of your DeepStack server
ds_url = "http://localhost:82/"

# # Test control flags. Set to N to skip test.
# Run face tests
doFace = "Y"
# Run object detection tests
doObj = "Y"
# Run tests for logo custom model. See https://github.com/OlafenwaMoses/DeepStack_OpenLogo
doLogo = "Y"
# Run tests for licence-plate custom model. See https://github.com/odd86/deepstack_licenceplate_model
doPlate = "Y"
# Run tests for dark custom model. See https://github.com/OlafenwaMoses/DeepStack_OpenLogo
doDark = "Y"


def read_binary(file_name):
    f = open(img_path + file_name, "rb")
    if f.mode == "rb":
        return f.read()
    else:
        print("could not read " + img_path + file_name)
        os._exit(1)


# register face for test.
def register_face(file_name, user_id):
    # read binary
    response = requests.post(ds_url + "v1/vision/face/register",
    files={"image":read_binary(file_name)}, data={"userid":user_id}).json()
    print(response)


def detect_test(test_type, file_name, expected):
    print("Testing " + test_type + "-" + file_name)
    image = Image.open(img_path + file_name).convert("RGB")
    response = requests.post(ds_url + "v1/vision/" + test_type, files={"image":read_binary(file_name)}, data={"min_confidence":0.60}).json()
    print(response)

    if not response["success"]:
        print(response["error"])
        os._exit(1)
        
    if "face" == test_type:
        if expected != len(response["predictions"]):
            print("Of " + expected + " expected found faces, found" + len(response["predictions"]))
            os._exit(1)
    else:
        i = 0
        for item in response["predictions"]:
            if response["predictions"][i]["label"] != expected[i]: 
                print(expected[i] + " not found in " + test_type + " test image.")
                y_max = int(item["y_max"])
                y_min = int(item["y_min"])
                x_max = int(item["x_max"])
                x_min = int(item["x_min"])
                cropped = image.crop((x_min, y_min, x_max, y_max))
                cropped.save("error_image{}.jpg".format(i))
                os._exit(1)
            else:
                print(expected[i] + " found in " + test_type + " test image.")
        
            i += 1
    print("Passed test " + test_type + "-" + file_name)


# # quick test the see server is up
response = requests.get(ds_url)
if response.status_code != 200:
    print("DeepStack does not appear be running at " + ds_url)
    print(response)
    os._exit(1)

if doFace == "Y": 
# # face detect test
    detect_test("face", "family.jpg", 4)

    # # face match test
    image_data1 = open(img_path + "obama1.jpg", "rb").read()
    image_data2 = open(img_path + "obama2.jpg", "rb").read()
    
    response = requests.post(ds_url + "v1/vision/face/match", files={"image1":read_binary("obama1.jpg"), "image2":read_binary("obama2.jpg")}).json()
    
    print(response)
    
    # deserializes into dict
    # and returns dict.
    # note needs dumps to clean up or will fail.
    y = json.loads(json.dumps(response))
     
    print("JSON string = ", y)
    rtn = y['similarity']
    print(rtn)
    
    if rtn > 0.70:
        print("match passed")
    else:
        print("Face match failed")
        os._exit(1)
    
    image_data2 = open(img_path + "brad.jpg", "rb").read()
    
    response = requests.post(ds_url + "v1/vision/face/match", files={"image1":read_binary("obama1.jpg"), "image2":read_binary("brad.jpg")}).json()
    
    print(response)
    
    # deserializes into dict
    # and returns dict.
    y = json.loads(json.dumps(response))
     
    print("JSON string = ", y)
    rtn = y['similarity']
    print(rtn)
    
    if rtn < 0.51:
        print("mismatch passed")
    else:
        print("Face mismatch failed")
        os._exit(1)

    # # face recog test
    register_face("tomcruise.jpg", "Tom Cruise")
    register_face("adele.jpg", "Adele")
    register_face("idriselba.jpg", "Idris Elba")
    register_face("perri.jpg", "Christina Perri")
    
    test_image = open(img_path + "adele2.jpg", "rb").read()
    
    res = requests.post(ds_url + "v1/vision/face/recognize",
    files={"image":read_binary("adele2.jpg")}).json()
    print(res)
    
    for user in res["predictions"]:
        print("Found " + user["userid"])
        if user["userid"] != "Adele":
            print("Face recog failed. Found " + user["userid"] + " instead of Adele") 
            os._exit(1)
else:
    print("Face tests skipped")

if doObj == "Y": 
    # # Basic Object test
    detect_test("detection", "test-image3.jpg", ["handbag", "person", "dog", "person"])
    detect_test("detection", "fedex.jpg", ["truck"])

    if doLogo == "Y": 
        detect_test("custom/openlogo", "fedex.jpg", ["fedex", "fedex"])
    else:
        print("Detect openlogo test skipped")

    if doPlate == "Y": 
        detect_test("custom/licence-plate", "fedex.jpg", ["plate"])
    else:
        print("Detect licence-plate test skipped")
        
    if doDark == "Y": 
        detect_test("custom/dark", "dark_image.jpg", ["Motorbike", "People", "Dog", "Dog", "Dog", "Dog", "Dog"])
    else:
        print("Detect dark test skipped")

print("All test passed")
