import requests
import json
import pytesseract
from PIL import Image
import PyPDF2
import fitz
import argparse

def extract_text_from_pdf(pdf_url):
    response = requests.get(pdf_url)
    response.raise_for_status()
    pdf_content = response.content
    doc = fitz.open("pdf", pdf_content)

    page = doc[0]
    text = page.get_text()

    doc.close()
    return text.encode('utf-8').decode('utf-8')

# Function to extract text from PDF using PyMuPDF
def ocr_pdf(pdf_url):
    text = ""
    response = requests.get(pdf_url, stream=True, verify=False)

    if response.status_code == 200:
        # Open the PDF document using PyMuPDF (fitz)
        pdf_document = fitz.open(stream=response.content, filetype="pdf")

        for page_number in range(pdf_document.page_count):
            page = pdf_document.load_page(page_number)
            image = page.get_pixmap()

            # Convert the image to a format compatible with pytesseract
            img = Image.frombytes("RGB", [image.width, image.height], image.samples)

            page_text = pytesseract.image_to_string(img, lang='vie')

            text += page_text + '\n'

        pdf_document.close()
    else:
        print("Failed to download the PDF file. Status code:", response.status_code)

    return text

# Function to extract text from image using pytesseract
def extract_text_from_image(image_path):
	response = requests.get(image_path, stream=True, verify=False)
	if response.status_code == 200:
		image = Image.open(response.raw)

		text = pytesseract.image_to_string(image, lang='vie')

		image.close()

		return text
	else:
		print("Failed to download the image. Status code:", response.status_code)
		return None

def is_pdf(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower() == '.pdf'

def get_extract_books():
    bookUrl = url + "Book/get-extract"
    try:
    	response = requests.get(bookUrl, verify=False)

    	if response.status_code == 200:
    	    json_response = response.json()
    	    return [book['id'] for book in json_response['books']]
    	else:
    	    return []
    except requests.exceptions.RequestException as e:
    	return []

def get_extract_pages(bookId):
	pageUrl = url + f"Page/get-extract/{bookId}"
	try:
		response = requests.get(pageUrl, verify=False)

		if response.status_code == 200:
		    json_response = response.json()
		    return [page for page in json_response['pages']]
		else:
		    return []
	except requests.exceptions.RequestException as e:
		return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='API url')
    args = parser.parse_args()

    input_data = args.url

    global url
    url = input_data
    book_ids = get_extract_books()

    if len(book_ids):
        print("No pages need to extract")

    page_urls = []

    for bookId in book_ids:
        pages = get_extract_pages(bookId)
        for page in pages:
            if page['url1'] == None: continue
            page_urls.append({'id' : page['id'], 'url': page['url1'], 'content': page['textContent']})

    for item in page_urls:
        try:
            if item['url'].split('.')[-1] == 'pdf':
                link = url + f"Pdf/{item['url']}"
                print(link)
                content = extract_text_from_pdf(link)
                if content == '':
                    print('Empty')
                    content = str(ocr_pdf(link))
            else:
                link = url + f"Image/get-scanned/{item['url']}"
                content = str(extract_text_from_image(link))

            if content != '' and item['content'] == '':
                update_url = url + f'Page/{item["id"]}/update-extracted-text?text={content}'
                response = requests.post(update_url, verify=False)

                if response.status_code == 200:
                    print(f"Updated text for item {item['id']} successfully.")
                else:
                    print(f"Failed to update text for item {item['id']} with status code {response.status_code}: {response.text}")

        except Exception as e:
            print(f"An error occurred for item {item['id']}: {str(e)}")











