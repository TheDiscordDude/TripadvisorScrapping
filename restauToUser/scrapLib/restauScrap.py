import re
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from scrapLib.database import get_number_reviews_for_restaurant
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
        phone_number = driver.find_element(By.XPATH, ".//span[@class='fhGHT']").text
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
            ec.presence_of_element_located((By.CLASS_NAME, "RWYkj"))
        )
        title = review_tag.get_attribute("aria-label")
        rating_string = title[0:3]
        rating = float(rating_string[0:3])
    except TimeoutException:
        print("No ratings found for this restaurant")
    return rating


def get_restau_number_of_reviews(driver):
    """
    Gets the number of reviews in the restaurant
    :param driver: It's the webdriver of the current page
    :return: the number of reviews in Integer
    """
    try:
        num = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, "dUfZJ"))
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
    name_tag = driver.find_element(By.TAG_NAME, "h1")
    name = name_tag.text.strip()
    if len(name.split(",")) > 1:
        name = ", ".join(name.split(",")[:-1])
    return name


# ------------ GETS ADDRESS ------------

def get_restau_address(driver):
    """
    Get the address of the restaurant
    :param driver: It's the webdriver of the page, currently on the restaurant page
    :return: the address
    """
    address_tag = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, ".//a[@href='#MAPVIEW']"))
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
    name = get_restau_name(driver)
    id_restau = get_restau_id(url)
    address = get_restau_address(driver)
    phone = get_restau_phone_number(driver)
    rating = get_restau_rating(driver)
    nb_reviews = get_restau_number_of_reviews(driver)

    return {
        "id": id_restau,
        "name": name,
        "phone": phone,
        "address": address,
        "rating": rating,
        "nbreviews": nb_reviews
    }


# ------------ GETS LAST PAGE OF REVIEW ------------

def get_last_visited_restaurant_page(url, restau_id, cursor):
    """
    Gets the very last page we visited for a restaurant. It is useful when we get StaleElementExceptions
    because we don't have to go through every page when there is an Exception.
    :param url: the base url of the restaurant
    :param restau_id: the id of the restaurant
    :param cursor: the db cursor
    :return: the new url
    """
    n_reviews = get_number_reviews_for_restaurant(restau_id, cursor)
    n_page = (n_reviews // 10) * 10
    new_url = url.split("Reviews-")[0] + "Reviews-or" + str(n_page) + "-" + url.split("Reviews-")[1]
    return new_url
