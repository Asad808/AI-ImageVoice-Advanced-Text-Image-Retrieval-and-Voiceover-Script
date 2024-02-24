import os, sys
import shutil
from pathlib import Path

try:
    from bing import Bing
except ImportError:  # Python 3
    from .bing import Bing


def download(query, limit=100, output_dir='dataset', adult_filter_off=True, 
force_replace=False, timeout=60, filter="", verbose=True):
    
    """
    Downloads images based on a query using Bing search.

    Parameters:
    query (str): The search query to download images for.
    limit (int, optional): The maximum number of images to download. Defaults to 100.
    output_dir (str, optional): The directory to save downloaded images. Defaults to 'dataset'.
    adult_filter_off (bool, optional): Sets the adult filter. 'True' turns it off. Defaults to True.
    force_replace (bool, optional): If True, existing files in the output directory will be replaced. Defaults to False.
    timeout (int, optional): The timeout for the search request in seconds. Defaults to 60.
    filter (str, optional): Filter for the type of images to download (e.g., 'photo', 'clipart'). Defaults to "".
    verbose (bool, optional): Enables verbose output. Defaults to True.

    Returns:
    list: A list of URLs of the downloaded images.
    """

    # engine = 'bing'
    if adult_filter_off:
        adult = 'off'
    else:
        adult = 'on'

    
    image_dir = Path(output_dir).joinpath(query).absolute() # Create a directory for the search query

    if force_replace:
        if Path.isdir(image_dir):
            shutil.rmtree(image_dir) # Remove existing directory

    # check directory and create if necessary
    try:
        if not Path.is_dir(image_dir):
            Path.mkdir(image_dir, parents=True) # Create directory

    except Exception as e:
        print('[Error]Failed to create directory.', e)
        sys.exit(1)
        
    print("[%] Downloading Images to {}".format(str(image_dir.absolute())))
    bing = Bing(query, limit, image_dir, adult, timeout, filter, verbose) # Create a Bing object
    download_urls =  bing.run() # Store returned URLs
    return download_urls


if __name__ == '__main__':
    download('dog', output_dir="..\\Users\\cat", limit=10, timeout=1)
    
