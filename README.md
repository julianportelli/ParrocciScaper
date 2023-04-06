# ParrocciScaper

This is a sample web scraper, written in Python, which extracts data from the website https://parrocci.knisja.mt/, which contains information about Catholic parishes in Malta. The code uses the BeautifulSoup library to parse the HTML content of the website and the pandas library to store the extracted data in a tabular format.

The code begins by defining several constants, such as the names of the columns in the resulting pandas DataFrame, the types of churches that are considered, and the root URL of the website.

The next part of the code creates three directories to store cached HTML content. The `getSiteBeautifulSoup` function takes a URL as input and retrieves the corresponding HTML content, either from a local cache or by sending an HTTP request to the server. The function returns a BeautifulSoup object that can be used to navigate the HTML structure.

The code then retrieves the home page of the website and extracts the section that contains information about the different localities in Malta. For each locality, the code navigates to the corresponding page and extracts information about the parish and its churches. The resulting data is stored in a pandas DataFrame.

The code for each locality first extracts the name of the locality and the name of the parish. It then extracts information about the main priest of the parish, known as the kappillan. This includes the name, email address, and phone number of the kappillan.

Next, the code extracts information about each church in the parish, which can be one of three types: knisja parrokkjali (parish church), kappelli tal-adorazzjoni (adoration chapels), and knejjes u kappelli oħra (other churches and chapels). For each church, the code extracts the name, type, and the name and contact information of the person in charge.

Finally, the resulting pandas DataFrame is saved to an Excel file.

# Requirements
Python 3 is required to run this program.

# Installation

Install dependencies3: **pip install -r requirements.txt**

Run the main python file: **python main.py**
