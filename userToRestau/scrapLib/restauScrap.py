import re
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


# ------------ GETS PHONE NUMBER ------------

def get_restau_phone_number(driver):
    """
    Get the phone number
    :param driver: It's the webdriver of the page, currently on the restaurant page
    :return: the phone number
    """
    try:
        phone_number = driver.find_element(By.CLASS_NAME, "phoneNumber").text
        phone_number = phone_number.replace("-", "")
        phone_number = phone_number.replace(" ", "")
        return phone_number
    except NoSuchElementException:
        return None


# ------------ GETS ID ------------

def get_restau_id(url):
    """
    Get the id of the restaurant
    :param url: The url of the restaurant page
    :return: the id
    """
    id_restau = re.findall(r"d[0-9]+", url)[0]
    id_restau = int(id_restau[1:])
    return id_restau


def get_restau_rating(driver):
    """
    Get the rating of the current restaurant
    :param driver: It's the webdriver of the current page
    :return: a float corresponding to the rating or None if it's not found
    """
    rating = None
    try:
        review_tag = WebDriverWait(driver, 10).until(
            ec.presence_of_all_elements_located((By.CLASS_NAME, "ui_bubble_rating"))
        )
        title = review_tag[1].get_attribute("alt")
        if title is None:
            return None
        rating_string = title[0:3]
        rating = float(rating_string[0:3])
    except TimeoutException:
        print("Restaurant Rating not found. Restarting program")
    return rating


def get_restau_number_of_reviews(driver):
    try:
        num = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, "//a[@class='more taLnk']"))

        )
    except:
        return 0
    num = num.text
    num2 = re.search("[0-9]+(,[0-9]*)?", num)
    if num2 is None:
        return 0
    num2 = num2.group(0)
    num2 = num2.replace(",", "")
    return int(num2)


# ------------ GETS NAME ------------

def get_restau_name(driver):
    """
    Get the name of the restaurant
    :param driver: It's the webdriver of the page, currently on the restaurant page
    :return: the name
    """
    name_tag = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "HEADING")))
    name = name_tag.text.strip()
    return name


# ------------ GETS ADDRESS ------------

def get_restau_address(driver):
    """
    Get the address of the restaurant
    :param driver: It's the webdriver of the page, currently on the restaurant page
    :return: the address
    """
    address_tag = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CLASS_NAME, "format_address"))
    )

    return address_tag.text


# ------------ GETS STATUS ------------

def get_restau_infos(driver, url):
    """
    Gathers all the previous information
    :param driver: It's the webdriver of the page
    :param url: the restaurant page url
    :return: all the information about a restaurant
    """
    restau_id = get_restau_id(url)

    name = get_restau_name(driver)
    address = get_restau_address(driver)
    phone = get_restau_phone_number(driver)
    rating = get_restau_rating(driver)
    nb_reviews = get_restau_number_of_reviews(driver)

    return {
        "id": restau_id,
        "name": name,
        "phone": phone,
        "address": address,
        "rating": rating,
        "nbreviews": nb_reviews
    }
