import PyPDF2
from io import BytesIO
from bs4 import BeautifulSoup

class File_Parser():

    def __init__(self):
        pass

    def extract_plain_text(self, binary_response_content, content_type):
        if content_type[:9] == "text/html":
            return self.extract_plain_text_html(binary_response_content)
        elif content_type == 'application/pdf':
            return self.extract_plain_text_pdf(binary_response_content)
        elif content_type == 'text/plain':
            return self.extract_plain_text_txt(binary_response_content)
        else:
            return "ERROR"

    def extract_plain_text_html(self, binary_response_content):
        soup = BeautifulSoup(binary_response_content, 'html.parser')
        return soup.get_text()

    def extract_plain_text_pdf(self, binary_response_content):
        try:
            pdf = BytesIO(binary_response_content)
            pdfReader = PyPDF2.PdfFileReader(pdf)
            text = ""
            for page_number in range(pdfReader.numPages):
                page = pdfReader.getPage(page_number)
                text += page.extractText()
            return text
        except:
            return "ERROR"

    def extract_plain_text_txt(self, binary_response_content):
        return binary_response_content.decode('UTF-8')