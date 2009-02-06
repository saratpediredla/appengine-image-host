"""
Frontend for the image host. This does the actual serving of the images
for use on others sites and within the admin
"""

import os
import datetime

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models import Image
import GoogleS3
import awskeys
  
class GenericServer(webapp.RequestHandler):
    """
    Image server designed to handle serving png images from
    different object properties
    """
    property = 'image'
    def get(self):
        # key is provided in the query string
        # Try and create an s3 connection
        if len(awskeys.AWS_ACCESS_KEY_ID) > 0 and len(awskeys.AWS_SECRET_ACCESS_KEY) > 0:
            s3 = GoogleS3.AWSAuthConnection(awskeys.AWS_ACCESS_KEY_ID, awskeys.AWS_SECRET_ACCESS_KEY)
        else:
            s3 = None
        if s3 is None:
            image = db.get(self.request.get("id"))
            if image.image:
                # we have an image so prepare the response
                # with the relevant headers
                self.response.headers['Content-Type'] = "image/png"
                # and then write our the image data direct to the response
                self.response.out.write(eval("image.%s" % self.property))
            else:
                # we should probably return an image with the correct header
                # here instead of the default html 404
                self.error(404)
        else:
            image = s3.get(awskeys.BUCKET_NAME,self.request.get("id")+"_"+self.property)
            if image.http_response.status_code == 200:
                self.response.headers['Content-Type'] = "image/png"
                self.response.out.write(image.object.data)
            else:
                self.error(404)

class ImageServer(GenericServer):
    "Serve the main image"
    property = 'image'

class ThumbServer(GenericServer):
    "Serve the thumbnail image"
    property = 'thumb'

class OriginalServer(GenericServer):
    "Serve the original uploaded image. Currently unused."
    property = 'original'

application = webapp.WSGIApplication([
    ('/i/img', ImageServer),
    ('/i/thumb', ThumbServer),
], debug=True)

def main():
    "Run the application"
    run_wsgi_app(application)

if __name__ == '__main__':
    main()