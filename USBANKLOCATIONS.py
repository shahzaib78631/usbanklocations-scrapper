import requests
from bs4 import BeautifulSoup
import csv
import argparse

# start the session
conn = requests.Session()

# URL from which we are going to scrape the data
URL = "https://www.usbanklocations.com/banks.php"

# Name of the bank
# bankName = "Savings Bank of Danbury"

head = ["name", "type", "street", "locality", "region", "postal_code"]
database = []


def search(bankName, page=1):
    payload = {"q": bankName, "ps": page}
    response = conn.get(URL, params=payload)

    soup = BeautifulSoup(response.content, "html.parser")
    return soup


def getTotalPages(soup):
    totalPages = soup.find("table", "lsortby").next_sibling
    totalPages = totalPages.string.split(".")[1].strip().split(" ")[-1]
    return int(totalPages)


def get_data(row):
    """Function for extraction data"""
    for item in row:
        try:
            info = []
            row = item.find("b")
            bankName = row.get_text()
            info.append(bankName)
            bankData = row.next_siblings
            print(bankName)
            for i in bankData:
                if i.string != None:
                    print(i.string)
                    info.append(i.string)
            print("-" * 30)
            # Extract locality, region and postal code
            # from the last index
            temp = info[-1].split(",")
            locality = temp[0]
            rp = temp[1].strip().split(" ")
            region = rp[0]
            postalCode = rp[1]

            # replace last index value with locality
            info[-1] = locality
            # appen region and postal code
            info.append(region)
            info.append(postalCode)

            # Pack the data
            database = dict(zip(head, info))

            # Write it to csv
            with open("bankdata.csv", "a") as f:  # Just use 'w' mode in 3.x
                w = csv.DictWriter(f, fieldnames=head)
                if not f:
                    w.writeheader()
                w.writerow(database)
        except Exception as e:
            print("exception: ", e)
            # continue


if __name__ == "__main__":
    print("-" * 60)
    print(" _   _ ___ ___   _   _  _ _  ___    ___   ___   _ _____ ___ ___  _  _ ___  ")
    print("| | | / __| _ ) /_\ | \| | |/ / |  / _ \ / __| /_\_   _|_ _/ _ \| \| / __| ")
    print("| |_| \__ \ _ \/ _ \| .` | ' <| |_| (_) | (__ / _ \| |  | | (_) | .` \__ \ ")
    print(" \___/|___/___/_/ \_\_|\_|_|\_\____\___/ \___/_/ \_\_| |___\___/|_|\_|___/ ")
    print("-" * 60)
    # Add argumets
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="Name of the CSV FILE with extension")

    args = parser.parse_args()

    try:
        if args.filename:
            banks = ""
            # Open the file which contain the file name
            with open(args.filename, newline="") as csvfile:
                csvreader = csv.reader(csvfile, delimiter=",")
                banks = [bank[0] for bank in csvreader]
            # for each bank name in the file
            for bank in banks:
                # search it on the website
                soup = search(bank)
                # get the total pages
                totalPages = getTotalPages(soup)
                # for each page of the search
                for i in range(totalPages + 1):
                    soup = search(bank, i)
                    plb = soup.select(".plb")
                    plw = soup.select(".plw")
                    data = [plb, plw]
                    for r in data:
                        get_data(r)
            print("File Saved")
        else:
            print("Please Provide csv File which contain Bank Names")
            exit()
    except Exception as e:
        print("There is some error in your csv file.")
        print("Please check your csv file and try again.")
        exit()
