import csv
import re
import requests
from bs4 import BeautifulSoup


class BooksScrape:
    data = []

    def start_request(self, url):
        with requests.Session() as session:
            self.parse(session.get(url))

    def parse(self, request):
        soup = BeautifulSoup(request.content, "html.parser")
        urls = soup.select("h3 a")
        for url in urls:
            self.parse_links(url["href"])

        next_page = soup.select_one(".next a")
        if next_page:
            url = self.get_full_url(next_page["href"])
            self.start_request(url)
        else:
            self.write_to_csv()

    def parse_links(self, link):
        url = self.get_full_url(link)
        with requests.Session() as session:
            self.extract_data(session.get(url))

    def extract_data(self, request):
        soup = BeautifulSoup(request.content, "html.parser")
        category = self.extract_category(soup)
        img = self.extract_image_url(soup)
        books_data = {
            "url": request.url,
            "title": soup.find("h1").get_text(),
            "price": soup.select_one("p.price_color").text.replace("£", "").strip(),
            "UPC": soup.select_one("th+td").get_text(),
            "category": category,
            "imageUrl": img
        }
        self.data.append(books_data)
        print(books_data)

    def extract_image_url(self, soup):
        url = "https://books.toscrape.com/"
        img = soup.find("img").get("src")
        pattern = r"(media.*)"
        result = re.findall(pattern, img)
        if result:
            return url + result[0]

    def extract_category(self, soup):
        categories = [item.get_text() for item in soup.select(".breadcrumb li a")]
        return "/".join(categories)

    def write_to_csv(self):
        filename = "books_data.csv"
        with open(filename, mode="w", newline="") as file:
            fieldnames = ["url", "category", "title", "price", "imageUrl", "UPC"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(self.data)

        print("Data written to", filename)

    def get_full_url(self, link):
        url = "https://books.toscrape.com/"
        if "catalogue" not in link:
            link = f"catalogue/{link}"
        return url + link


x = BooksScrape()
x.start_request("https://books.toscrape.com/")
