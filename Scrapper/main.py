import logging
from nudenet import NudeDetector
from nudenet import NudeClassifier
from scrapper import Scrapper

# Create and configure the logger object
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Overall minimum logging level

stream_handler = logging.StreamHandler()  # Configure the logging messages displayed in the Terminal
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)  # Minimum logging level for the StreamHandler

file_handler = logging.FileHandler('info.log')  # Configure the logging messages written to a file
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)  # Minimum logging level for the FileHandler

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


if __name__ == '__main__':  # Execute the following code only when executing main.py (not when importing it)
    scrapper = Scrapper()
    print(scrapper.ads_list)
    
    # classifier = NudeClassifier()
    # print(classifier.classify('./test1.jpg'))
    
    # detector = NudeDetector()
    # print(detector.detect('./test1.jpg'))
    # detector.censor('./test1.jpg', out_path='./test1_censor.jpg', visualize=False)
