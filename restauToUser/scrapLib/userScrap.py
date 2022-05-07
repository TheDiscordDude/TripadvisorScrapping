import re
from datetime import datetime
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from .utils import restart_program
import time


# ------------ GETS THE USER PROFILE LINK ------------

def get_user_link_from_review(review_number: int, driver):
    """
     Retrieves the user profile link from a restaurant review.
    :param review_number: the number of the review on the page. It usually goes from 0 to 9, because there is 10 element on a page at max
    :param driver: It's the webdriver of the page
    :return: The link to the user profile page or None when the User doesn't use a Tripadvisor Account
    """
    try:
        users = WebDriverWait(driver, 10).until(
            ec.presence_of_all_elements_located((By.CLASS_NAME, "member_info"))
        )
    except TimeoutException:
        print("Timeout Exception : Couldn't access members info for this restaurant")

    try:
        user_macaron = WebDriverWait(users[review_number], 10).until(
            ec.element_to_be_clickable((By.CLASS_NAME, "memberOverlayLink"))
        )
    except StaleElementReferenceException:
        print("StaleElementReferenceException while trying to access the link of the user overlay")
        restart_program()
    except:
        print("The selected user isn't on tripadvisor (might be on facebook)")
        return None
    # Dans un premier temps on chope le macaron et on click dessus
    try:
        driver.execute_script("arguments[0].click();", user_macaron)
    except:
        print("The selected user isn't on tripadvisor (might be on facebook)")
        return None
    try:
        overlay = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, "memberOverlayRedesign"))
        )
    except TimeoutException:
        print("Timeout Exception while waiting for the user Overlay")
        restart_program()

    # Dans un second temps on chope l'overlay et le premier lien stocké à l'intérieur
    user_link_tag = overlay.find_element(By.TAG_NAME, "a")
    user_link = user_link_tag.get_attribute("href")

    time.sleep(1)

    # Et dans un dernier temps, on close la fenetre
    close_button = driver.find_elements(By.CLASS_NAME, "ui_close_x")[-1]
    driver.execute_script("arguments[0].click();", close_button)

    return user_link


# ------------ GETS THE USER PSEUDO ------------

def get_user_pseudo(driver):
    """
    Retrieves the user pseudo from its profile page
    :param driver: It's the webdriver of the page
    :return: the user pseudo
    """
    try:
        pseudo_tag = driver.find_element(By.CLASS_NAME, "Hgccy")
        pseudo = pseudo_tag.text
    except NoSuchElementException as e:
        print(str(e) + "for User Pseudo")
        pseudo = None
    return pseudo


# ------------ GET USER ID ------------

def get_user_id(url: str):
    """
    Retrieves the user id after the @ in the profile page
    :param url: url to the profile page
    :return: a string representing the userid
    """
    user_id = url.split("/")[-1]
    if "." in user_id:
        return None
    return user_id


# ------------ GETS USER LOCATION ------------

def get_user_location(driver):
    """
    Retrieves the user location/address of the user in their profile
    :param driver: It's the webdriver of the page
    :return: a string representing the location / address of the user
    """
    try:
        location_tag = driver.find_element(By.XPATH, ".//span[@class='fIKCp _R S4 H3 ShLyt default']")
        location = location_tag.text
    except NoSuchElementException:
        print("NoSuchElementException While getting user location")
        location = None
    return location


# ------------ GETS USER INSCRIPTION DATE ------------

def get_user_inscription_date(driver):
    """
    Retrieves the user inscription date
    :param driver: It's the webdriver of the page, currently on the user profile page
    :return: a date element representing the inscription date of the user on tripadvisor
    """
    try:
        inscription_date_tag = driver.find_element(By.XPATH, ".//span[@class='dspcc _R H3']")
        inscription_date = inscription_date_tag.text
        inscription_date = inscription_date.replace("Joined in ", "")
        inscription_date = datetime.strptime(inscription_date, "%b %Y")
    except NoSuchElementException:
        print("NoSuchElementException while getting the user inscription date")
        inscription_date = None
    return inscription_date


# ------------ GETS USER CONTRIBUTIONS ------------

def get_user_contribution_details(driver):
    """
    Retrieves the number of photos, reviews and likes the user has
    :param driver: It's the webdriver of the page, currently on the user profile page
    :return: returns a tuple of int values representing : the number of photos, reviews and likes
    """
    try:
        contributions_link = driver.find_element(By.XPATH, ".//a[@class='dnaXn b Wc _S']")
        driver.execute_script("arguments[0].click();", contributions_link)
        try:
            element_present = ec.presence_of_all_elements_located((By.CLASS_NAME, 'fHLdN'))
            contribs_details_tags = WebDriverWait(driver, 100).until(element_present)
        except TimeoutException:
            print("Timed out waiting for user contrib details to load.")
            restart_program()

        nb_photos = None
        nb_reviews = None
        nb_likes = None
        for detailTag in contribs_details_tags:
            if "photo" in detailTag.text:
                nb_photos = get_nb_from_contrib_details(detailTag)
            elif "review" in detailTag.text:
                nb_reviews = get_nb_from_contrib_details(detailTag)
            elif "helpful votes" in detailTag.text:
                nb_likes = get_nb_from_contrib_details(detailTag)

        return nb_photos, nb_reviews, nb_likes
    except NoSuchElementException:
        print("NoSuchElementException while Getting user contribution details")
    return None, None, None


def get_nb_from_contrib_details(nb_tag):
    """
    This function retrieves the number from a text like " 45 reviews"
    :param nb_tag: a webelement representing the tag containing the number.
    :return: the number contained in the tag
    """
    match = re.search('[0-9]+(\.[0-9]+)?', nb_tag.text)
    nb_txt = match.group(0)
    nb_txt = nb_txt.replace(".", "")
    return int("0" + nb_txt)


# ------------ GETS USER DESCRIPTION ------------

def get_user_descrition(driver):
    """
    Retrieves the description of a user from its profile page
    :param driver: It's the webdriver of the page, currently on the user profile page
    :return: a string representing the description of the user
    """
    description = None
    try:
        description_tag = driver.find_element(By.CLASS_NAME, "EhKyl")
        """description_tag=WebDriverWait(driver, 0.5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "EhKyl"))
        )"""
        description = description_tag.text
    except TimeoutException:
        print("Timed out while waiting for user description element")
    except NoSuchElementException:
        print("NoSuchElementException while getting user description")
    return description


# ------------ GETS ALL THE INFOS ON USERS ------------

def get_user_infos(driver, user_link):
    """
    Retrieves all the necessary infos from a user to send it in a database
    :param user_link:
    :param driver: It's the webdriver of the page, currently on the user profile page
    :return: a dictionary containing all the infos on the restaurant
    """
    try:
        driver.find_element(By.CLASS_NAME, "error404 ")
        return None
    except NoSuchElementException:
        pass
    user_id = get_user_id(user_link)
    pseudo = get_user_pseudo(driver)
    if not pseudo:
        pseudo = user_id
    location = get_user_location(driver)
    inscription_date = get_user_inscription_date(driver)
    try:
        nb_photos, nb_reviews, nb_likes = get_user_contribution_details(driver)
    except TypeError:
        print("Contribution details returns None")
        restart_program()
    description = get_user_descrition(driver)

    return {
        "userid": user_id,
        "pseudo": pseudo,
        "location": location,
        "joindate": inscription_date,
        "photos": nb_photos,
        "reviews": nb_reviews,
        "likes": nb_likes,
        "description": description
    }
