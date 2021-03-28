import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor
import math
from playsound import playsound
import cv2
# Calculate positions from from estimated rotation 



def people_image_information(photo):


    client=boto3.client('rekognition')
 

    #Get image width and height
    image = Image.open(open(photo,'rb'))
    width, height = image.size
    

    print ('Image information: ')
    print (photo)
    print ('Image Height: ' + str(height)) 
    print('Image Width: ' + str(width))    

    draw = ImageDraw.Draw(image)
    # call detect faces and show face age and placement
    # if found, preserve exif info
    stream = io.BytesIO()
    if 'exif' in image.info:
        exif=image.info['exif']
        image.save(stream,format=image.format, exif=exif)
    else:
        image.save(stream, format=image.format)    
    image_binary = stream.getvalue()
   
    response = client.detect_faces(Image={'Bytes': image_binary})
    labels = client.detect_labels(Image={'Bytes': image_binary})
    for label in labels['Labels']:
        print ("Label: " + label['Name'])
        print ("Confidence: " + str(label['Confidence']))
    
    print()
    
    X=[]
    Y=[]
    for person in response['FaceDetails']:
        
        
        
        box = person['BoundingBox']
        imgWidth, imgHeight = image.size
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']
        x=(left+width)/2
        y=(top+height)/2    

        print('Left: ' + '{0:.0f}'.format(left))
        print('Top: ' + '{0:.0f}'.format(top))
        print('Face Width: ' + "{0:.0f}".format(width))
        print('Face Height: ' + "{0:.0f}".format(height))
        print('x: ' + '{0:.0f}'.format(x))
        print('y: ' + '{0:.0f}'.format(y))
        x=int(x)
        y=int(y)
        X.append(x)
        Y.append(y)
        points = (
            (left,top),
            (left + width, top),
            (left + width, top + height),
            (left , top + height),
            (left, top)

        )
        draw.line(points, fill='#00d400', width=5)
        print()
    
    sum = 0
      
    # for each point, finding distance 
    # to rest of the point 
    for i in range(len(X)): 
        for j in range(i+1,len(X)): 
            sum = math.sqrt(((X[i] - X[j])*(X[i] - X[j])) + ((Y[i] - Y[j])*(Y[i] - Y[j]))) 
            if sum<=200:
                playsound('{Location_of_alert_sound}')
                
            else:
                sum=0
    image.show()
    return len(response['FaceDetails'])

def main():
    count = 0

  
     # save frame as JPEG file      
    vidcap = cv2.VideoCapture('{location_of_video}')
    success,image = vidcap.read()
    while success:
          
        vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*1000))  
        cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file      
        success,image = vidcap.read()
        print('Read a new frame: ', success)
        
        
        photo='{Location_where_frames_are_stored}/frame%d.jpg'% count
        count += 1
        people_count=people_image_information(photo)
    #print("People detected: " + str(people_count))


if __name__ == "__main__":
    main()    
