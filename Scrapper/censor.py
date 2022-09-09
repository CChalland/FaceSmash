from nudenet import NudeDetector
from nudenet import NudeClassifier
import logging

logger = logging.getLogger()  # This will be the same logger object as the one configured in main.py

class Censor:
    def __init__(self):
        self.pwd = 'media/'
        self.detector = NudeDetector()     # for the "base" version of detector.
    
    
    def censored_image(self, file_location, file_path):
        file_name = './media/' + file_path + '/censored/' + file_location.split('/')[-1]
        
        # Give details about the detection and where
        print(file_location.split('/')[-1], self.detector.detect('./' + file_location))
        
        # Censors the image
        self.detector.censor('./' + file_location, out_path=file_name, visualize=False)

        return file_name
    
    


if __name__ == '__main__':  # Execute the following code only when executing main.py (not when importing it)
    print("Testing")