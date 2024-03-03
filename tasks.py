from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables

from RPA.PDF import PDF

import time

from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.

    """
    browser.configure(
        slowmo = 300
    )

    open_robot_order_website()
    close_annoying_modal()
    download_orders_file()
    get_orders()
    archive_receipts()

def open_robot_order_website():
    """This function will open the website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    """To close the popup which comes up while opening the website by clicking on OK"""
    page = browser.page()
    page.click('text=OK')

def download_orders_file():
    """Downloads cvs orders file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)


def get_orders():
    """Reads the orders from the CSV file"""
    library = Tables()
    orders = library.read_table_from_csv(
    "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
    )
    for row in orders:
        #print(f"Values in each row : {row}")
        fill_the_form(row)


def fill_the_form(row):
    """To fill the form to order an robot"""
    print(f"Order number executed : {row['Order number']}")
    page = browser.page()

    dict_select_option = {
        "1" : "Roll-a-thor head",
        "2" : "Peanut crusher head",
        "3" : "D.A.V.E head",
        "4" : "Andy Roid head",
        "5" : "Spanner mate head",
        "6" : "Drillbit 2000 head"
    }

    page.select_option("#head",dict_select_option.get(row['Head']))
    page.click(f'//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{row["Body"]}]/label')
    page.fill("input[placeholder='Enter the part number for the legs']", row['Legs'])
    page.fill("#address", row['Address'])
    page.click("#order")
    orderLocator = page.query_selector("#order")
    print(orderLocator)
    if orderLocator:
        print("orderLocator found again")
        page.click("#order")
    anotherLocator = page.query_selector("#order-another")
    print(anotherLocator)
    if anotherLocator:
        print("another locator")
        pdf_file = store_receipt_as_pdf(row['Order number'])
        screenshot_file = screenshot_robot(row['Order number'])
        embed_screenshot_to_receipt(screenshot_file,pdf_file)
        page.click("#order-another")
        close_annoying_modal()


def store_receipt_as_pdf(order_number):
    """Export the data to a pdf file"""
    page = browser.page()
    order_results_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = f"output/receipts/{order_number}.pdf"
    pdf.html_to_pdf(order_results_html, pdf_path)
    return pdf_path

def screenshot_robot(order_number):
    """Take the screenshot of the receipt"""
    page = browser.page()
    screenshot_path = f"output/receipts/{order_number}.png"
    page.screenshot(path=screenshot_path)
    return screenshot_path


def embed_screenshot_to_receipt(screenshot_file, pdf_file):
    """ This action will embeed the screenshot to the receipt"""
    #time.sleep(5)
    pdf = PDF()
    pdf.add_watermark_image_to_pdf (
        image_path=screenshot_file,
        source_path=pdf_file,
        output_path=pdf_file
    )

def archive_receipts():
    """Archives all the receipts into a zip file"""
    lib = Archive()
    lib.archive_folder_with_zip('./output/receipts', './output/receipts.zip')    